# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from decimal import Decimal
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.contrib.auth.models import User
import json

from .models import (
    Customer, Appointment, Invoice, Service, Voucher, Product,
    Payment, InvoiceDetail, PackageUsageHistory, ServicePackage, GiftCard
)
from .forms import (
    CustomerForm, AppointmentForm, ModalAppointmentForm, PaymentForm,
    ProductForm, ServiceForm, InvoiceForm
)

@login_required
def invoice_detail_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    details = InvoiceDetail.objects.filter(invoice=invoice)

    context = {
        'page_title': f'Chi tiết hóa đơn #{invoice.id}',
        'invoice': invoice,
        'details': details
    }
    return render(request, 'sales/invoice_detail.html', context)

# invoice_detail.html
"""
{% extends 'sales/base.html' %}
{% block title %}{{ page_title }}{% endblock %}
{% block content %}
<style>
    .invoice-box {
        max-width: 800px;
        margin: auto;
        padding: 30px;
        border: 1px solid #eee;
        box-shadow: 0 0 10px rgba(0, 0, 0, 0.15);
        font-size: 16px;
        line-height: 24px;
        font-family: 'Helvetica Neue', 'Helvetica', Helvetica, Arial, sans-serif;
        color: #555;
    }
    @media print {
        body > nav.no-print, .no-print { display: none !important; }
        .invoice-box { box-shadow: none; border: none; margin: 0; padding: 0; }
    }
</style>

<div class="no-print d-flex justify-content-end mb-3">
    <button onclick="window.print()" class="btn btn-sm btn-outline-secondary">🖨️ In hóa đơn</button>
</div>

<div class="invoice-box">
    <div class="text-center mb-4">
        <h2 class="fw-bold">SHINE BEAM</h2>
        <p class="mb-0">Địa chỉ: [73A Nguyễn Thị Minh Khai, P. Bến Thành, TP.HCM]</p>
        <p class="mb-0">Điện thoại: [1900 636 849]</p>
    </div>
    <hr>
    <h3 class="text-center mb-4">HÓA ĐƠN THANH TOÁN</h3>

    <table class="table table-borderless table-sm mb-4">
        <tbody>
            <tr>
                <td><strong>Khách hàng:</strong></td>
                <td>{{ invoice.customer.full_name|default:"(Không có thông tin)" }}</td>
                <td><strong>Hóa đơn số:</strong></td>
                <td>#{{ invoice.id }}</td>
            </tr>
            <tr>
                <td><strong>Nhân viên:</strong></td>
                <td>{{ invoice.staff.username|default:"(Không rõ)" }}</td>
                <td><strong>Ngày tạo:</strong></td>
                <td>{{ invoice.created_at|date:"d/m/Y H:i" }}</td>
            </tr>
            <tr>
                <td><strong>Số dư tín dụng:</strong></td>
                <td class="fw-bold text-primary">
                    {{ invoice.customer.credit_balance|default_if_none:0|floatformat:0|intcomma }}đ
                </td>
                <td><strong>Trạng thái:</strong></td>
                <td>
                    {% if invoice.status == 'paid' %}
                        <span class="badge bg-success">Đã thanh toán</span>
                    {% elif invoice.status == 'unpaid' %}
                        <span class="badge bg-warning text-dark">Chưa thanh toán</span>
                    {% else %}
                        <span class="badge bg-danger">Đã hủy</span>
                    {% endif %}
                </td>
            </tr>
        </tbody>
    </table>

    <table class="table">
        <thead class="table-light">
            <tr>
                <th>Sản phẩm/Dịch vụ</th>
                <th class="text-end">Đơn giá</th>
            </tr>
        </thead>
        <tbody>
            {% for detail in details %}
            <tr>
                <td>
                    {% if detail.product %}{{ detail.product.name }}{% endif %}
                    {% if detail.service %}{{ detail.service.name }}{% endif %}
                    {% if detail.service_package %}{{ detail.service_package.name }}{% endif %}
                </td>
                <td class="text-end">{{ detail.unit_price|floatformat:0|intcomma }}đ</td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="2">Không có sản phẩm hoặc dịch vụ.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    <div class="d-flex justify-content-end mt-4">
        <div class="w-50">
            <div class="d-flex justify-content-between">
                <strong class="me-3">Tạm tính:</strong> <span>{{ invoice.sub_total|floatformat:0|intcomma }}đ</span>
            </div>
            <div class="d-flex justify-content-between text-danger">
                <strong class="me-3">Giảm giá:</strong> 
                <span>-{{ invoice.discount_amount|default_if_none:0|floatformat:0|intcomma }}đ</span>
            </div>
            <hr>
            <div class="d-flex justify-content-between fs-5 fw-bold">
                <strong class="me-3">Thành tiền:</strong> <span>{{ invoice.final_amount|floatformat:0|intcomma }}đ</span>
            </div>
            <div class="d-flex justify-content-between fs-5 fw-bold text-success">
                <strong class="me-3">Đã thanh toán:</strong> <span>{{ invoice.paid_amount|floatformat:0|intcomma }}đ</span>
            </div>
            <div class="d-flex justify-content-between fs-5 fw-bold text-danger">
                <strong class="me-3">Cần thanh toán thêm:</strong> 
                <span>
                    {% if invoice.amount_due > 0 %}
                        {{ invoice.amount_due|floatformat:0|intcomma }}đ
                    {% else %}0đ
                    {% endif %}
                </span>
            </div>
        </div>
    </div>
</div>
{% endblock %}
"""

# models.py (chỉ đoạn cần chỉnh sửa - nếu cần dùng invoice.details.all)
# class InvoiceDetail(models.Model):
#     invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='details')
#     ...
