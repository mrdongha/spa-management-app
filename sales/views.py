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
from django.contrib.auth.decorators import login_required

# ... (Toàn bộ các hàm view đã được cung cấp ở các bước trước sẽ nằm ở đây, 
# đảm bảo hàm create_invoice_view lấy staff từ form.cleaned_data['staff']) ...

# Ví dụ hàm create_invoice_view đã được sửa:
@login_required
def create_invoice_view(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                staff_data = form.cleaned_data['staff']
                # ... (phần còn lại của logic) ...
                invoice = Invoice.objects.create(
                    # ...
                    staff=staff_data, 
                    # ...
                )
                # ... (phần còn lại của logic) ...
                return redirect('invoice_detail', invoice_id=invoice.id)
    else:
        form = InvoiceForm()
    context = {'page_title': 'Tạo hóa đơn mới', 'form': form}
    return render(request, 'sales/create_invoice.html', context)
# Lưu ý: Đây chỉ là ví dụ, bạn hãy dùng file views.py hoàn chỉnh đã được cung cấp.