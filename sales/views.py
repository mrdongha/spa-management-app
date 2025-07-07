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
        form = AppointmentForm()
    context = {'form': form}
    return render(request, 'sales/add_appointment.html', context)
    
@login_required
def create_invoice_view(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                customer_data = form.cleaned_data['customer']
                staff_data = form.cleaned_data['staff']
                customer_to_update = Customer.objects.select_for_update().get(pk=customer_data.pk)
                products = form.cleaned_data['products']
                services = form.cleaned_data['services']
                packages = form.cleaned_data['packages']
                gift_card_payment = form.cleaned_data['gift_card']
                final_amount = sum(p.price for p in products) + sum(s.price for s in services) + sum(pkg.price for pkg in packages)
                
                amount_paid_from_credit = min(customer_to_update.credit_balance, final_amount)
                payment_for_gift_card = gift_card_payment.value if gift_card_payment else Decimal('0')
                paid_amount = amount_paid_from_credit + payment_for_gift_card

                invoice = Invoice.objects.create(
                    customer=customer_to_update,
                    staff=staff_data,
                    sub_total=final_amount,
                    final_amount=final_amount,
                    paid_amount=paid_amount,
                    status='paid' if paid_amount >= final_amount else 'unpaid'
                )

                for item in list(products) + list(services) + list(packages):
                    item_type = ''
                    if isinstance(item, Product): item_type = 'product'
                    elif isinstance(item, Service): item_type = 'service'
                    elif isinstance(item, ServicePackage): item_type = 'package'
                    InvoiceDetail.objects.create(invoice=invoice, product=item if item_type == 'product' else None, service=item if item_type == 'service' else None, service_package=item if item_type == 'package' else None, item_type=item_type, quantity=1, unit_price=item.price)

                if amount_paid_from_credit > 0:
                    customer_to_update.credit_balance -= amount_paid_from_credit
                    Payment.objects.create(invoice=invoice, amount_paid=amount_paid_from_credit, payment_method='credit')

                if gift_card_payment:
                    overpayment = payment_for_gift_card
                    if paid_amount > final_amount:
                        overpayment = payment_for_gift_card - (final_amount - amount_paid_from_credit)
                    customer_to_update.credit_balance += overpayment
                
                customer_to_update.save()
                return redirect('invoice_detail', invoice_id=invoice.id)
    else:
        form = InvoiceForm()
    
    context = {'page_title': 'Tạo hóa đơn mới', 'form': form}
    return render(request, 'sales/create_invoice.html', context)
    
@login_required
def record_payment_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    customer = invoice.customer

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            credit_to_use = form.cleaned_data.get('use_credit') or Decimal('0')
            other_payment_amount = form.cleaned_data.get('amount_paid') or Decimal('0')
            other_payment_method = form.cleaned_data.get('payment_method')

            with transaction.atomic():
                customer_to_update = Customer.objects.select_for_update().get(pk=customer.pk)
                amount_due = invoice.amount_due
                
                actual_credit_paid = min(credit_to_use, customer_to_update.credit_balance, amount_due)
                if actual_credit_paid > 0:
                    customer_to_update.credit_balance -= actual_credit_paid
                    invoice.paid_amount += actual_credit_paid
                    Payment.objects.create(invoice=invoice, amount_paid=actual_credit_paid, payment_method='credit')

                if other_payment_amount > 0:
                    invoice.paid_amount += other_payment_amount
                    Payment.objects.create(invoice=invoice, amount_paid=other_payment_amount, payment_method=other_payment_method)
                
                if invoice.paid_amount > invoice.final_amount:
                    overpayment = invoice.paid_amount - invoice.final_amount
                    customer_to_update.credit_balance += overpayment
                    invoice.paid_amount = invoice.final_amount
                
                if invoice.paid_amount >= invoice.final_amount:
                    invoice.status = 'paid'
                
                customer_to_update.save()
                invoice.save()
            
            return redirect('invoice_detail', invoice_id=invoice.id)
    else:
        form = PaymentForm(initial={'amount_paid': 0, 'use_credit': 0})
    
    context = {'form': form, 'invoice': invoice, 'customer': customer}
    return render(request, 'sales/record_payment.html', context)

@login_required
def invoice_detail_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    context = {'page_title': f'Chi tiết hóa đơn #{invoice.id}', 'invoice': invoice}
    return render(request, 'sales/invoice_detail.html', context)
    
@login_required
def use_package_view(request, invoice_detail_id):
    invoice_detail = get_object_or_404(InvoiceDetail, id=invoice_detail_id)
    customer = invoice_detail.invoice.customer
    if request.method == 'POST':
        PackageUsageHistory.objects.create(
            invoice_detail=invoice_detail,
            customer=customer,
            notes=request.POST.get('notes', '')
        )
        return redirect('customer_detail', customer_id=customer.id)
    return redirect('customer_detail', customer_id=customer.id)

# ==============================================================================
# CÁC HÀM VIEW CHO API
# ==============================================================================

def all_appointments_json(request):
    appointments = Appointment.objects.all().select_related('customer', 'service')
    data = []
    for appointment in appointments:
        service_name = appointment.service.name if appointment.service else "Dịch vụ đã xóa"
        data.append({'title': f"{appointment.customer.full_name} - {service_name}", 'start': appointment.start_time.isoformat(), 'end': appointment.end_time.isoformat(), 'id': appointment.id})
    return JsonResponse(data, safe=False)

def appointment_form_content(request):
    form = ModalAppointmentForm()
    return render(request, 'sales/partials/appointment_form_modal.html', {'form': form})
    
@login_required
def create_appointment_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            customer = Customer.objects.get(id=data.get('customer'))
            service = Service.objects.get(id=data.get('service'))
            appointment = Appointment.objects.create(customer=customer, service=service, start_time=data.get('start_time'), end_time=data.get('end_time'), notes=data.get('notes', ''), status='scheduled')
            return JsonResponse({'status': 'success', 'message': 'Lịch hẹn đã được tạo thành công!', 'appointment_id': appointment.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    
@login_required
def apply_voucher_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            voucher_code = data.get('voucher_code')
            sub_total = Decimal(data.get('sub_total', '0'))
            if not voucher_code:
                return JsonResponse({'status':