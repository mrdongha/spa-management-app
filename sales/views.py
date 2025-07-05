# sales/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Customer, Appointment, Invoice, Service, Voucher, Product, Payment, InvoiceDetail, PackageUsageHistory
from .forms import CustomerForm, AppointmentForm, ModalAppointmentForm, PaymentForm
from django.utils import timezone
from decimal import Decimal
import json

# ==============================================================================
# CÁC HÀM VIEW CHÍNH CHO CÁC TRANG
# ==============================================================================

def dashboard_view(request):
    context = {'page_title': 'Trang tổng quan'}
    return render(request, 'sales/dashboard.html', context)

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

def product_list_view(request):
    """
    Hàm để hiển thị danh sách sản phẩm.
    """
    products = Product.objects.filter(is_active=True).order_by('name')
    context = {
        'page_title': 'Danh sách sản phẩm',
        'products': products
    }
    return render(request, 'sales/product_list.html', context)

def calendar_view(request):
    context = {'page_title': 'Lịch hẹn'}
    return render(request, 'sales/calendar.html', context)

def report_view(request):
    paid_invoices = Invoice.objects.filter(status='paid').order_by('-created_at')
    total_revenue = sum(invoice.final_amount for invoice in paid_invoices)
    context = {
        'invoices': paid_invoices,
        'total_revenue': total_revenue,
        'invoice_count': paid_invoices.count()
    }
    return render(request, 'sales/reports.html', context)

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

def create_invoice_view(request):
    if request.method == 'POST':
        pass # Xử lý logic tạo hóa đơn phức tạp ở đây
    context = {'page_title': 'Tạo hóa đơn mới'}
    return render(request, 'sales/create_invoice.html', context)

def record_payment_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.save()
            invoice.paid_amount += payment.amount_paid
            if invoice.paid_amount >= invoice.final_amount:
                invoice.status = 'paid'
            invoice.save()
            return redirect('invoice_detail', invoice_id=invoice.id)
    else:
        form = PaymentForm()
    context = {'form': form, 'invoice': invoice}
    return render(request, 'sales/record_payment.html', context)

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
# CÁC HÀM VIEW CHO API VÀ CÁC THÀNH PHẦN PHỤ
# ==============================================================================

def all_appointments_json(request):
    appointments = Appointment.objects.all().select_related('customer', 'service')
    data = []
    for appointment in appointments:
        service_name = appointment.service.name if appointment.service else "Dịch vụ đã xóa"
        data.append({
            'title': f"{appointment.customer.full_name} - {service_name}",
            'start': appointment.start_time.isoformat(),
            'end': appointment.end_time.isoformat(),
            'id': appointment.id,
        })
    return JsonResponse(data, safe=False)

def appointment_form_content(request):
    form = ModalAppointmentForm()
    return render(request, 'sales/partials/appointment_form_modal.html', {'form': form})

def create_appointment_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            customer = Customer.objects.get(id=data.get('customer'))
            service = Service.objects.get(id=data.get('service'))
            appointment = Appointment.objects.create(
                customer=customer,
                service=service,
                start_time=data.get('start_time'),
                end_time=data.get('end_time'),
                notes=data.get('notes', ''),
                status='scheduled'
            )
            return JsonResponse({'status': 'success', 'message': 'Lịch hẹn đã được tạo thành công!', 'appointment_id': appointment.id})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def apply_voucher_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            voucher_code = data.get('voucher_code')
            sub_total = Decimal(data.get('sub_total', '0'))
            if not voucher_code:
                return JsonResponse({'status': 'error', 'message': 'Vui lòng nhập mã voucher.'}, status=400)
            now = timezone.now()
            voucher = Voucher.objects.get(code__iexact=voucher_code, is_active=True, valid_from__lte=now)
            if voucher.valid_to and voucher.valid_to < now:
                raise Voucher.DoesNotExist
            discount_amount = Decimal('0')
            if voucher.discount_type == 'percentage':
                discount_amount = (sub_total * voucher.value) / 100
            elif voucher.discount_type == 'fixed':
                discount_amount = voucher.value
            final_amount = sub_total - discount_amount
            return JsonResponse({
                'status':