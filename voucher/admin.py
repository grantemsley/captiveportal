from django.contrib import admin
from .models import Portal, Roll, Voucher


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


admin.site.register(Portal, PortalAdmin)
admin.site.register(Roll, RollAdmin)

