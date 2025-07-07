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

@login_required
def dashboard_view(request):
    return render(request, 'sales/dashboard.html', {'page_title': 'Trang tổng quan'})

@login_required
def customer_list_view(request):
    customer_list = Customer.objects.annotate(total_spent=Sum('invoices__final_amount', filter=Q(invoices__status='paid'))).order_by('-created_at')
    paginator = Paginator(customer_list, 20) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_title': 'Danh sách Khách hàng', 'customers': page_obj}
    return render(request, 'sales/customer_list.html', context)
    