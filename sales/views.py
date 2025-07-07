# sales/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import *
from .forms import *
from django.utils import timezone
from decimal import Decimal
import json
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.contrib.auth.decorators import login_required

# ... (Toàn bộ các hàm view khác giữ nguyên như file hoàn chỉnh tôi đã gửi cho bạn)

@login_required
def invoice_detail_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    context = {
        'page_title': f'Chi tiết hóa đơn #{invoice.id}',
        'invoice': invoice
    }
    # Thay đổi duy nhất là trỏ đến file template mới
    return render(request, 'sales/invoice_receipt.html', context)

# ... (Toàn bộ các hàm view khác giữ nguyên)