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

# 