# sales/admin.py
from django.contrib import admin
from .models import (
    Customer, Service, Invoice, InvoiceDetail, 
    ServicePackage, PackageUsageHistory, Appointment, Payment, Voucher, Product
)

# ... các class Admin cũ giữ nguyên ...
class InvoiceDetailInline(admin.TabularInline):
    model = InvoiceDetail; extra = 0; readonly_fields = ('item_type', 'unit_price')
@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'status', 'final_amount', 'created_at'); list_filter = ('status', 'created_at'); search_fields = ('customer__full_name', 'customer__phone_number'); inlines = [InvoiceDetailInline]; readonly_fields = ('sub_total', 'discount_amount', 'final_amount', 'paid_amount')
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'created_at'); search_fields = ('full_name', 'phone_number')
@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('customer', 'service', 'staff', 'start_time', 'status'); list_filter = ('status', 'start_time'); search_fields = ('customer__full_name',)
@admin.register(Voucher)
class VoucherAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'value', 'is_active', 'valid_to'); list_filter = ('is_active', 'discount_type')

# ✅ Đăng ký model mới
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'quantity_in_stock', 'is_active')
    search_fields = ('name',)
    list_filter = ('is_active',)

admin.site.register(Service)
admin.site.register(ServicePackage)
admin.site.register(PackageUsageHistory)
admin.site.register(Payment)
admin.site.register(GiftCard)