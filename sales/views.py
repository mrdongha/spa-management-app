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

# ==============================================================================
# CÁC HÀM VIEW CHÍNH CHO CÁC TRANG
# ==============================================================================

def dashboard_view(request):
    context = {'page_title': 'Trang tổng quan'}
    return render(request, 'sales/dashboard.html', context)

# --- Quản lý Khách hàng ---
def customer_list_view(request):
    customers = Customer.objects.order_by('-created_at')
    context = {'page_title': 'Danh sách Khách hàng', 'customers': customers}
    return render(request, 'sales/customer_list.html', context)

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

def customer_detail_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    context = {'page_title': f'Chi tiết: {customer.full_name}', 'customer': customer}
    return render(request, 'sales/customer_detail.html', context)

# --- Quản lý Dịch vụ ---
def service_list_view(request):
    services = Service.objects.order_by('name')
    context = {'page_title': 'Danh sách Dịch vụ', 'services': services}
    return render(request, 'sales/service_list.html', context)

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
def product_list_view(request):
    products = Product.objects.filter(is_active=True).order_by('name')
    context = { 'page_title': 'Danh sách sản phẩm', 'products': products }
    return render(request, 'sales/product_list.html', context)

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
def calendar_view(request):
    context = {'page_title': 'Lịch hẹn'}
    return render(request, 'sales/calendar.html', context)

def report_view(request):
    paid_invoices = Invoice.objects.filter(status='paid').order_by('-created_at')
    total_revenue = sum(invoice.final_amount for invoice in paid_invoices)
    context = {'invoices': paid_invoices, 'total_revenue': total_revenue, 'invoice_