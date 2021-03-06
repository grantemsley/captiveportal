# Copyright (C) 2021 Grant Emsley <grant@emsley.ca>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#            http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
import datetime
from django.utils import timezone
from urllib.parse import urlencode
from .models import Portal, Roll, Voucher, PrintTemplate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.contrib import messages



def redirect_params(url, params=None):
    response = redirect(url)
    if params:
        query_string = urlencode(params, True)
        response['Location'] += '?' + query_string
    return response


class PortalListView(LoginRequiredMixin, generic.ListView):
    model = Portal

    def get_queryset(self):
        # Limit only to active portals
        qs = super().get_queryset()
        qs = qs.filter(active=True)

        # Hide portals where the user has no groups that are allowed printing.
        groups = self.request.user.groups.values_list('id', flat=True)
        qs = qs.filter(allow_printing__in=groups)

        # Groups query can cause duplicate records.
        qs = qs.distinct()

        return qs


@login_required
def printselection(request, portal_id):
    
    # Make sure the portal is active and user has access.
    groups = request.user.groups.values_list('id', flat=True)
    try:
        portal = Portal.objects.filter(pk=portal_id,active=True,allow_printing__in=groups).distinct().get()
    except Portal.DoesNotExist:
        raise Http404("Portal does not exist")


    if request.method == 'POST':
        printtemplate_id = request.POST['printtemplate_id']
        quantity = int(request.POST['quantity'])
        roll_id = int(request.POST['roll_id'])

        roll = get_object_or_404(Roll, pk=roll_id)
        printtemplate = get_object_or_404(PrintTemplate, pk=printtemplate_id)

        # Validate parameters
        if (quantity < 1):
            messages.add_message(request, messages.ERROR, 'Invalid quantity.')
            return render(request, 'voucher/print_selection.html', {'portal':portal, 'printtemplate_id':printtemplate_id, 'quantity':quantity, 'roll_id': roll_id})
        if (quantity > roll.remaining_vouchers()):
            messages.add_message(request, messages.ERROR, 'Not enough vouchers available.')
            return render(request, 'voucher/print_selection.html', {'portal':portal, 'printtemplate_id':printtemplate_id, 'quantity':quantity, 'roll_id': roll_id})
            
        # Get only unprinted vouchers from this roll
        vouchers = Voucher.objects.filter(roll=roll.id)
        vouchers = vouchers.filter(date_printed__isnull=True)
        # Retrieve the id values as a flat list (convert to list(), otherwise the query will change when we update these values!)
        vouchers = list(vouchers.values_list('id', flat=True)[:quantity])

        # Mark these vouchers as printed
        Voucher.objects.filter(id__in=vouchers).update(date_printed=timezone.now(),printed_by=request.user.get_username())

        return redirect_params(reverse('voucher:print', kwargs={'portal_id': portal_id, 'roll_id': roll_id, 'printtemplate_id': printtemplate_id}), {'v': vouchers})
    else:
        return render(request, 'voucher/print_selection.html', {'portal':portal,'quantity':5})

@login_required
def print(request, portal_id, roll_id, printtemplate_id):
    # Make sure the portal is active and user has access.
    groups = request.user.groups.values_list('id', flat=True)
    try:
        portal = Portal.objects.filter(pk=portal_id,active=True,allow_printing__in=groups).distinct().get()
    except Portal.DoesNotExist:
        raise Http404("Portal does not exist")

    roll = get_object_or_404(Roll, pk=roll_id)
    printtemplate = get_object_or_404(PrintTemplate, pk=printtemplate_id)
    
    # Retrieve the vouchers by id, and verify they are ok to print (someone could have altered GET string)
    # Make sure they match the roll, and were marked as printed within the last hour
    voucherlist = request.GET.getlist('v')
    vouchers = Voucher.objects.filter(id__in=voucherlist)
    vouchers = vouchers.filter(roll=roll.id)
    vouchers = vouchers.filter(date_printed__isnull=False)
    last_hour = timezone.now() - datetime.timedelta(hours=1)
    vouchers = vouchers.filter(date_printed__gt=last_hour)
    codes = list(vouchers.values_list('code', flat=True))

    context = {
        'roll': roll,
        'portal': portal,
        'printtemplate': printtemplate,
        'codes': codes,
    }

    if printtemplate.type == "Paper":
        return render(request, 'voucher/print_paper.html', context)
    elif printtemplate.type == "Dymo":
        return render(request, 'voucher/print_dymo.html', context)
    else:
        raise Http404("Invalid print template type")    
