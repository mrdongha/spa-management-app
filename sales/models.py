# sales/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import F
from decimal import Decimal

class Customer(models.Model):
    full_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15, unique=True)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"

class Service(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class ServicePackage(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    total_sessions = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name} ({self.total_sessions} buổi)"

class Voucher(models.Model):
    DISCOUNT_TYPES = [('percentage', 'Phần trăm'), ('fixed', 'Số tiền cố định'),]
    code = models.CharField(max_length=50, unique=True, help_text="VD: GIAM10, KHAITRUONG")
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    value = models.DecimalField(max_digits=12, decimal_places=2, help_text="Nếu là phần trăm, nhập 10 cho 10%. Nếu là tiền cố định, nhập số tiền.")
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField(default=timezone.now)
    valid_to = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        if self.discount_type == 'percentage':
            return f"{self.code} - Giảm {self.value}%"
        return f"{self.code} - Giảm {self.value:,.0f}đ"

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    quantity_in_stock = models.PositiveIntegerField(default=0, help_text="Số lượng tồn kho")
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    def __str__(self):
        return f"{self.name} (Tồn kho: {self.quantity_in_stock})"

class Invoice(models.Model):
    STATUS_CHOICES = [('unpaid', 'Chưa thanh toán'), ('paid', 'Đã thanh toán'), ('cancelled', 'Đã hủy'),]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='invoices')
    voucher_applied = models.ForeignKey(Voucher, on_delete=models.SET_NULL, null=True, blank=True)
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Tổng tiền trước giảm giá")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Tổng tiền sau giảm giá")
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='unpaid')
    created_at = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"Hóa đơn #{self.id} - {self.customer.full_name}"
    @property
    def amount_due(self):
        return self.final_amount - self.paid_amount

class InvoiceDetail(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='details')
    product = models.ForeignKey(Product, on_delete=models.PROTECT, null=True, blank=True)
    service = models.ForeignKey(Service, on_delete=models.PROTECT, null=True, blank=True)
    service_package = models.ForeignKey(ServicePackage, on_delete=models.PROTECT, null=True, blank=True)
    item_type = models.CharField(max_length=20, default='service')
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    def __str__(self):
        item_name = "Sản phẩm không xác định"
        if self.item_type == 'service': item_name = self.service.name
        elif self.item_type == 'package': item_name = self.service_package.name
        elif self.item_type == 'product': item_name = self.product.name
        return f"{item_name} (x{self.quantity}) on Invoice #{self.invoice.id}"

class PackageUsageHistory(models.Model):
    invoice_detail = models.ForeignKey(InvoiceDetail, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    used_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Khách {self.customer.full_name} dùng gói #{self.invoice_detail.id} lúc {self.used_at}"

class Payment(models.Model):
    PAYMENT_CHOICES = [('cash', 'Tiền mặt'), ('card', 'Thẻ'), ('transfer', 'Chuyển khoản'),]
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2) # <<< ĐÃ SỬA TÊN TRƯỜNG TẠI ĐÂY
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES)
    payment_time = models.DateTimeField(default=timezone.now)
    def __str__(self):
        return f"Thanh toán {self.amount_paid} cho hóa đơn #{self.invoice.id}"

class Appointment(models.Model):
    STATUS_CHOICES = [('scheduled', 'Đã lên lịch'), ('completed', 'Đã hoàn thành'), ('cancelled', 'Đã hủy'),]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, null=True)
    def __str__(self):
        return f"Lịch hẹn cho {self.customer.full_name} lúc {self.start_time.strftime('%H:%M %d/%m/%Y')}"