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

from django.contrib import admin
from .models import Portal, Roll, Voucher, PrintTemplate


class VoucherInline(admin.TabularInline):
    model = Voucher
    readonly_fields = ('code', 'date_printed', 'printed_by')
    extra = 0

class PortalAdmin(admin.ModelAdmin):
    list_display = ('name','ssid','active','roll_count')

class RollAdmin(admin.ModelAdmin):
    list_display = ('portal', 'description', 'number', 'total_vouchers', 'remaining_vouchers', 'active')
    inlines = [VoucherInline]
    list_filter = ('portal',)

class VoucherAdmin(admin.ModelAdmin):
    date_hierarchy = 'date_printed'
    list_display = ('roll', 'printed_by', 'date_printed', 'code')
    list_filter = (
        ('date_printed', admin.EmptyFieldListFilter),
        'printed_by',
        'roll',
    )

class TemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'type')


admin.site.register(Portal, PortalAdmin)
admin.site.register(Roll, RollAdmin)
admin.site.register(Voucher, VoucherAdmin)
admin.site.register(PrintTemplate, TemplateAdmin)

