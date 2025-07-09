# sales/admin.py
from django.contrib import admin
from .models import (
    Customer, 
    Service, 
    ServicePackage, 
    Product, 
    GiftCard, 
    Invoice, 
    InvoiceDetail, 
    PackageUsageHistory, 
    Payment, 
    Appointment
)

# Tùy chỉnh hiển thị cho Invoice trong trang admin
class InvoiceDetailInline(admin.TabularInline):
    model = InvoiceDetail
    extra = 0 # Không hiển thị form trống
    readonly_fields = ('product', 'service', 'service_package', 'quantity', 'unit_price') # Chỉ đọc

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'staff', 'final_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at', 'staff')
    search_fields = ('id', 'customer__full_name', 'customer__phone_number')
    inlines = [InvoiceDetailInline, PaymentInline]
    readonly_fields = ('sub_total', 'final_amount', 'paid_amount')

# Tùy chỉnh hiển thị cho Customer
@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'phone_number', 'credit_balance', 'created_at')
    search_fields = ('full_name', 'phone_number', 'profile_code')

# Đăng ký các model còn lại
admin.site.register(Service)
admin.site.register(ServicePackage)
admin.site.register(Product)
admin.site.register(GiftCard)
admin.site.register(PackageUsageHistory)
admin.site.register(Payment)
admin.site.register(Appointment)
admin.site.register(InvoiceDetail) # Đăng ký cả InvoiceDetail để có thể xem riêng