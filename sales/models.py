# sales/models.py
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from decimal import Decimal

class Customer(models.Model):
    profile_code = models.CharField(max_length=50, unique=True, blank=True, null=True, verbose_name="Mã hồ sơ")
    full_name = models.CharField(max_length=100, verbose_name="Họ và tên")
    phone_number = models.CharField(max_length=15, unique=True, verbose_name="Số điện thoại")
    email = models.EmailField(blank=True, null=True)
    credit_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Số dư tín dụng")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tham gia")

    def __str__(self):
        return self.full_name

class Service(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên dịch vụ")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")

    def __str__(self):
        return f"{self.name} - {self.price:,.0f}đ"

class ServicePackage(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên gói dịch vụ")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá")
    total_sessions = models.PositiveIntegerField(default=1, verbose_name="Số buổi")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")

    def __str__(self):
        return f"{self.name} ({self.total_sessions} buổi) - {self.price:,.0f}đ"

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên sản phẩm")
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá")
    quantity_in_stock = models.PositiveIntegerField(default=0, verbose_name="Tồn kho")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")

    def __str__(self):
        return f"{self.name} - {self.price:,.0f}đ"

class GiftCard(models.Model):
    name = models.CharField(max_length=100, verbose_name="Tên thẻ")
    value = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Giá trị")
    is_active = models.BooleanField(default=True, verbose_name="Hoạt động")

    def __str__(self):
        return f"{self.name} - {self.value:,.0f}đ"

class Invoice(models.Model):
    STATUS_CHOICES = [('unpaid', 'Chưa thanh toán'), ('paid', 'Đã thanh toán'), ('cancelled', 'Đã hủy'),]
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='invoices', verbose_name="Khách hàng")
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoices_created', verbose_name="Nhân viên")
    sub_total = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Tạm tính")
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Thành tiền")
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="Đã thanh toán")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='unpaid', verbose_name="Trạng thái")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Ngày tạo")

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

class PackageUsageHistory(models.Model):
    invoice_detail = models.ForeignKey(InvoiceDetail, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    used_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True, null=True)

class Payment(models.Model):
    PAYMENT_CHOICES = [('cash', 'Tiền mặt'), ('card', 'Thẻ'), ('transfer', 'Chuyển khoản'), ('credit', 'Tín dụng tích điểm')]
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES)
    payment_time = models.DateTimeField(default=timezone.now)

class Appointment(models.Model):
    STATUS_CHOICES = [('scheduled', 'Đã lên lịch'), ('completed', 'Đã hoàn thành'), ('cancelled', 'Đã hủy'),]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.SET_NULL, null=True, blank=True)
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    notes = models.TextField(blank=True, null=True)