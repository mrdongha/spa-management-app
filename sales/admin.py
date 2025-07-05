# sales/admin.py
from django.contrib import admin
# THÊM 'GiftCard' VÀO DÒNG IMPORT DƯỚI ĐÂY
from .models import (
    Customer, Service, ServicePackage, Voucher, Product, 
    Invoice, InvoiceDetail, PackageUsageHistory, Payment, 
    Appointment, GiftCard
)

# Đăng ký các model của bạn vào trang admin
admin.site.register(Customer)
admin.site.register(Service)
admin.site.register(ServicePackage)
admin.site.register(Voucher)
admin.site.register(Product)
admin.site.register(Invoice)
admin.site.register(InvoiceDetail)
admin.site.register(PackageUsageHistory)
admin.site.register(Payment)
admin.site.register(Appointment)
admin.site.register(GiftCard)