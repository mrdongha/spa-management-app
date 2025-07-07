# sales/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import (
    Customer, Appointment, Invoice, Service, Voucher, Product, 
    Payment, InvoiceDetail, PackageUsageHistory, ServicePackage, GiftCard
)
from .forms import (
    CustomerForm, AppointmentForm, ModalAppointmentForm, PaymentForm, 
    ProductForm, ServiceForm, InvoiceForm
)
from django.utils import timezone
from decimal import Decimal
import json
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

# ... (Toàn bộ các hàm view khác giữ nguyên)

# === HÀM MỚI ĐỂ XEM CHI TIẾT HÓA ĐƠN ===
@login_required
def invoice_detail_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    context = {
        'page_title': f'Chi tiết hóa đơn #{invoice.id}',
        'invoice': invoice
    }
    return render(request, 'sales/invoice_detail.html', context)

# ... (Toàn bộ các hàm view khác phải được giữ nguyên như phiên bản hoàn chỉnh trước đó)