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

# ==============================================================================
# CÁC HÀM VIEW CHÍNH CHO CÁC TRANG
# ==============================================================================

@login_required
def dashboard_view(request):
    context = {'page_title': 'Trang tổng quan'}
    return render(request, 'sales/dashboard.html', context)

# --- Quản lý Khách hàng ---
@login_required
def customer_list_view(request):
    customer_list = Customer.objects.annotate(
        total_spent=Sum('invoices__final_amount', filter=Q(invoices__status='paid'))
    ).order_by('-created_at')
    
    paginator = Paginator(customer_list, 20) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_title': 'Danh sách Khách hàng', 
        'customers': page_obj
    }
    return render(request, 'sales/customer_list.html', context)

@login_required
def add_customer_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    context = {'form': form, 'page_title': 'Thêm khách hàng mới'}
    return render(request, 'sales/add_customer.html', context)

@login_required
def customer_detail_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    usage_history = PackageUsageHistory.objects.filter(customer=customer).order_by('-used_at')
    context = {
        'page_title': f'Chi tiết: {customer.full_name}', 
        'customer': customer,
        'usage_history': usage_history
    }
    return render(request, 'sales/customer_detail.html', context)

# --- Quản lý Dịch vụ ---
@login_required
def service_list_view(request):
    services = Service.objects.order_by('name')
    context = {'page_title': 'Danh sách Dịch vụ', 'services': services}
    return render(request, 'sales/service_list.html', context)

@login_required
def add_service_view(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('service_list')
    else:
        form = ServiceForm()
    context = {'form': form, 'page_title': 'Thêm Dịch vụ mới'}
    return render(request, 'sales/add_service.html', context)

@login_required
def edit_service_view(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('service_list')
    else:
        form = ServiceForm(instance=service)
    context = {'form': form, 'page_title': f'Sửa Dịch vụ: {service.name}'}
    return render(request, 'sales/edit_service.html', context)
    
# --- Quản lý Sản phẩm ---
@login_required
def product_list_view(request):
    products = Product.objects.filter(is_active=True).order_by('name')
    context = { 'page_title': 'Danh sách sản phẩm', 'products': products }
    return render(request, 'sales/product_list.html', context)

@login_required
def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    context = { 'form': form, 'page_title': 'Thêm sản phẩm mới' }
    return render(request, 'sales/add_product.html', context)

@login_required
def edit_product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm(instance=product)
    context = { 'form': form, 'page_title': f'Sửa sản phẩm: {product.name}' }
    return render(request, 'sales/edit_product.html', context)
    
# --- Các trang chức năng khác ---
@login_required
def calendar_view(request):
    context = {'page_title': 'Lịch hẹn'}
    return render(request, 'sales/calendar.html', context)

@login_required
def report_view(request):
    paid_invoices = Invoice.objects.filter(status='paid')
    
    total_revenue = paid_invoices.aggregate(total=Sum('final_amount'))['total'] or 0
    invoice_count = paid_invoices.count()

    daily_revenue = paid_invoices.annotate(day=TruncDate('created_at')) \
                                 .values('day') \
                                 .annotate(daily_total=Sum('final_amount')) \
                                 .order_by('-day')

    monthly_revenue = paid_invoices.annotate(month=TruncMonth('created_at')) \
                                   .values('month') \
                                   .annotate(monthly_total=Sum('final_amount')) \
                                   .order_by('-month')

    context = {
        'page_title': 'Báo cáo & Thống kê',
        'total_revenue': total_revenue,
        'invoice_count': invoice_count,
        'daily_revenue': daily_revenue,
        'monthly_revenue': monthly_revenue,
    }
    return render(request, 'sales/reports.html', context)
    
@login_required
def staff_report_view(request):
    staff_revenue = User.objects.annotate(
        total_revenue=Sum('invoices_created__final_amount', filter=Q(invoices_created__status='paid'))
    ).filter(total_revenue__gt=0).order_by('-total_revenue')
    
    context = {
        'page_title': 'Báo cáo doanh thu theo nhân viên',
        'staff_revenue': staff_revenue
    }
    return render(request, 'sales/staff_report.html', context)

@login_required
def add_appointment_view(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard_view')
    else: