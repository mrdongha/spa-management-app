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

# ==============================================================================
# CÁC HÀM VIEW CHÍNH CHO CÁC TRANG
# ==============================================================================

def dashboard_view(request):
    context = {'page_title': 'Trang tổng quan'}
    return render(request, 'sales/dashboard.html', context)

# --- Quản lý Khách hàng ---
def customer_list_view(request):
    customer_list = Customer.objects.order_by('-created_at')
    paginator = Paginator(customer_list, 20) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_title': 'Danh sách Khách hàng', 'customers': page_obj}
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
    context = {'invoices': paid_invoices, 'total_revenue': total_revenue, 'invoice_count': paid_invoices.count()}
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
        form = InvoiceForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                customer = form.cleaned_data['customer']
                products = form.cleaned_data['products']
                services = form.cleaned_data['services']
                packages = form.cleaned_data['packages']
                gift_card_payment = form.cleaned_data['gift_card']
                sub_total = sum(p.price for p in products)
                sub_total += sum(s.price for s in services)
                sub_total += sum(pkg.price for pkg in packages)
                final_amount = sub_total
                paid_amount = gift_card_payment.value if gift_card_payment else Decimal('0')
                invoice = Invoice.objects.create(
                    customer=customer,
                    sub_total=sub_total,
                    final_amount=final_amount,
                    paid_amount=paid_amount,
                    status='paid' if paid_amount >= final_amount else 'unpaid'
                )
                for item in list(products) + list(services) + list(packages):
                    item_type = ''
                    if isinstance(item, Product): item_type = 'product'
                    elif isinstance(item, Service): item_type = 'service'
                    elif isinstance(item, ServicePackage): item_type = 'package'
                    InvoiceDetail.objects.create(
                        invoice=invoice,
                        product=item if item_type == 'product' else None,
                        service=item if item_type == 'service' else None,
                        service_package=item if item_type == 'package' else None,
                        item_type=item_type,
                        quantity=1,
                        unit_price=item.price
                    )
                if paid_amount > final_amount:
                    overpayment = paid_amount - final_amount
                    customer.credit_balance += overpayment
                    customer.save()
                return redirect('invoice_detail', invoice_id=invoice.id)
    else:
        form = InvoiceForm()
    context = {'page_title': 'Tạo hóa đơn mới', 'form': form}
    return render(request, 'sales/create_invoice.html', context)
    
def record_payment_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            paid_this_transaction = form.cleaned_data.get('amount_paid', Decimal('0'))
            
            with transaction.atomic():
                # Lấy số tiền còn nợ TRƯỚC khi thực hiện bất kỳ thay đổi nào
                amount_due_before_payment = invoice.amount_due
                
                # Chỉ xử lý nếu có thanh toán
                if paid_this_transaction > 0:
                    # Tạo bản ghi thanh toán
                    Payment.objects.create(
                        invoice=invoice,
                        amount_paid=paid_this_transaction,
                        payment_method=form.cleaned_data['payment_method']
                    )
                    
                    # Cập nhật số tiền đã trả của hóa đơn
                    invoice.paid_amount += paid_this_transaction
                    
                    # Xử lý tiền thừa và cộng vào tín dụng
                    if paid_this_transaction > amount_due_before_payment:
                        overpayment = paid_this_transaction - amount_due_before_payment
                        
                        # Lấy lại đối tượng khách hàng từ DB để đảm bảo dữ liệu mới nhất
                        # và khóa lại để tránh xung đột
                        customer_to_update = Customer.objects.select_for_update().get(pk=invoice.customer.pk)
                        customer_to_update.credit_balance += overpayment
                        customer_to_update.save()

                # Cập nhật trạng thái hóa đơn sau cùng
                if invoice.paid_amount >= invoice.final_amount:
                    invoice.status = 'paid'
                
                invoice.save()
            
            return redirect('invoice_detail', invoice_id=invoice.id)
    else:
        form = PaymentForm(initial={'amount_paid': invoice.amount_due})
    
    context = {'form': form, 'invoice': invoice}
    return render(request, 'sales/record_payment.html', context)

def invoice_detail_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    context = {'page_title': f'Chi tiết hóa đơn #{invoice.id}', 'invoice': invoice}
    return render(request, 'sales/invoice_detail.html', context)
    
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
            return JsonResponse({'status': 'success', 'message': 'Áp dụng voucher thành công!', 'discount_amount': str(discount_amount), 'final_amount': str(final_amount)})
        except Voucher.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Mã voucher không hợp lệ hoặc đã hết hạn.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Có lỗi xảy ra: ' + str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)