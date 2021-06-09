from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.views import generic
import datetime
from django.utils import timezone
from urllib.parse import urlencode
from .models import Portal, Roll, Voucher
from .forms import PrintSettingsForm



def redirect_params(url, params=None):
    response = redirect(url)
    if params:
        query_string = urlencode(params, True)
        response['Location'] += '?' + query_string
    return response



class PortalListView(generic.ListView):
    model = Portal


def printselection(request, portal_id):
    portal = get_object_or_404(Portal, pk=portal_id)

    if request.method == 'POST':
        printer_type = request.POST['printer_type']
        quantity = int(request.POST['quantity'])
        roll_id = int(request.POST['roll_id'])

        roll = get_object_or_404(Roll, pk=roll_id)

        # Validate parameters
        if printer_type not in ('address_labels', 'letter'):
            return render(request, 'voucher/print_selection.html', {'portal':portal,'error_message':'Invalid printer type', 'printer_type':printer_type, 'quantity':quantity, 'roll_id': roll_id})
        if (quantity < 1):
            return render(request, 'voucher/print_selection.html', {'portal':portal,'error_message':'Invalid quantity', 'printer_type':printer_type, 'quantity':quantity, 'roll_id': roll_id})
        if (quantity > roll.remaining_vouchers()):
            return render(request, 'voucher/print_selection.html', {'portal':portal,'error_message':'Not enough vouchers available.', 'printer_type':printer_type, 'quantity':quantity, 'roll_id': roll_id})
            
        # Get only unprinted vouchers from this roll
        vouchers = Voucher.objects.filter(roll=roll.id)
        vouchers = vouchers.filter(date_printed__isnull=True)
        # Retrieve the id values as a flat list (convert to list(), otherwise the query will change when we update these values!)
        vouchers = list(vouchers.values_list('id', flat=True)[:quantity])

        # Mark these vouchers as printed
        # FIXME also add user who printed them when authentication is setup
        Voucher.objects.filter(id__in=vouchers).update(date_printed=timezone.now())

        return redirect_params(reverse('voucher:print', kwargs={'portal_id': portal_id, 'roll_id': roll_id, 'printer_type': printer_type}), {'v': vouchers})
    else:
        return render(request, 'voucher/print_selection.html', {'portal':portal,'quantity':5})

def print(request, portal_id, roll_id, printer_type):
    portal = get_object_or_404(Portal, pk=portal_id)
    roll = get_object_or_404(Roll, pk=roll_id)
    
    # Retrieve the vouchers by id, and verify they are ok to print (someone could have altered GET string)
    # Make sure they match the roll, and were marked as printed within the last hour
    # FIXME - by the current user
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
        'printer_type': printer_type,
        'codes': codes,
    }

    if printer_type == 'address_labels':
        return render(request, 'voucher/print_dymo.html', context)
    elif printer_type == 'letter':
        return render(request, 'voucher/print_letter.html', context)
    else:
        return render(request, 'voucher/print_letter.html', context)
