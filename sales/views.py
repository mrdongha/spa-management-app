# sales/views.py
from django.shortcuts import render, redirect, get_object_or_404
# ✅ THÊM CÁC DECORATOR BẢO VỆ
from django.contrib.auth.decorators import login_required, permission_required

# ... các dòng import khác giữ nguyên ...
from django.http import JsonResponse
from django.db import transaction
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from decimal import Decimal
import json
from .models import ( Customer, Service, Invoice, InvoiceDetail, ServicePackage, PackageUsageHistory, Payment, Appointment, Voucher, Product)
from .forms import CustomerForm, PaymentForm, AppointmentForm, ModalAppointmentForm, ProductForm


# ===================================================================
# CÁC VIEW CHÍNH (ĐÃ ĐƯỢC BẢO VỆ)
# ===================================================================
@login_required # Yêu cầu phải đăng nhập
def dashboard_view(request):
    total_customers = Customer.objects.count()
    context = {'total_customers': total_customers}
    return render(request, 'sales/dashboard.html', context)

@login_required
@permission_required('sales.view_payment', raise_exception=True) # Chỉ ai có quyền xem thanh toán (Manager) mới được vào
def report_view(request):
    # ... logic của report_view giữ nguyên ...
    total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0; today = timezone.now().date(); revenue_today = Payment.objects.filter(payment_time__date=today).aggregate(total=Sum('amount'))['total'] or 0; start_of_month = today.replace(day=1); new_customers_this_month = Customer.objects.filter(created_at__gte=start_of_month).count(); thirty_days_ago = today - timedelta(days=29); payments_last_30_days = Payment.objects.filter(payment_time__date__gte=thirty_days_ago); revenue_by_day = { (today - timedelta(days=i)).strftime("%d/%m"): 0 for i in range(30) };
    for payment in payments_last_30_days:
        day_str = payment.payment_time.strftime("%d/%m")
        if day_str in revenue_by_day: revenue_by_day[day_str] += payment.amount
    chart_labels = list(revenue_by_day.keys()); chart_labels.reverse(); chart_data = list(revenue_by_day.values()); chart_data.reverse(); top_services = InvoiceDetail.objects.filter(item_type='service').values('service__name').annotate(count=Count('id')).order_by('-count')[:5]
    context = {'total_revenue': total_revenue,'revenue_today': revenue_today, 'new_customers_this_month': new_customers_this_month, 'chart_labels': chart_labels, 'chart_data': chart_data, 'top_services': top_services}
    return render(request, 'sales/report.html', context)

@login_required
def calendar_view(request):
    return render(request, 'sales/calendar.html')

# ===================================================================
# API KHÔNG CẦN LOGIN VÌ NÓ CHỈ TRẢ VỀ DỮ LIỆU CHO CALENDAR
# SẼ CẦN CÁC BIỆN PHÁP BẢO MẬT KHÁC TRONG TƯƠNG LAI
# ===================================================================
def all_appointments_json(request):
    # ... logic giữ nguyên ...
    appointments = Appointment.objects.all(); events = []
    for appointment in appointments:
        staff_name = f" (NV: {appointment.staff.username})" if appointment.staff else ""
        events.append({'title': f"{appointment.customer.full_name} - {appointment.service.name}{staff_name}", 'start': appointment.start_time.isoformat(), 'end': appointment.end_time.isoformat(), 'url': f"/customers/{appointment.customer.id}/"})
    return JsonResponse(events, safe=False)

# ... Dán lại tất cả các view cũ khác và thêm @login_required vào ...
@login_required
def product_list_view(request):
    products = Product.objects.all(); context = {'products': products}
    return render(request, 'sales/product_list.html', context)
@login_required
@permission_required('sales.add_product', raise_exception=True)
def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST);
        if form.is_valid(): form.save(); return redirect('product_list')
    else: form = ProductForm()
    context = {'form': form, 'title': 'Thêm sản phẩm mới'}; return render(request, 'sales/product_form.html', context)
@login_required
@permission_required('sales.change_product', raise_exception=True)
def edit_product_view(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid(): form.save(); return redirect('product_list')
    else: form = ProductForm(instance=product)
    context = {'form': form, 'title': 'Chỉnh sửa sản phẩm'}; return render(request, 'sales/product_form.html', context)
@login_required
def customer_list_view(request):
    customers = Customer.objects.order_by('-created_at'); context = {'customers': customers}
    return render(request, 'sales/customer_list.html', context)
@login_required
@permission_required('sales.add_customer', raise_exception=True)
def add_customer_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid(): form.save(); return redirect('customer_list')
    else: form = CustomerForm()
    context = {'form': form}; return render(request, 'sales/add_customer.html', context)
@login_required
def customer_detail_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id); invoices = customer.invoices.order_by('-created_at'); package_details = InvoiceDetail.objects.filter(invoice__customer=customer, item_type='package')
    for detail in package_details:
        detail.times_used = PackageUsageHistory.objects.filter(invoice_detail=detail).count()
        detail.sessions_left = detail.service_package.total_sessions - detail.times_used
    context = {'customer': customer, 'invoices': invoices, 'customer_invoice_details_packages': package_details}
    return render(request, 'sales/customer_detail.html', context)
@login_required
@permission_required('sales.add_invoice', raise_exception=True)
def create_invoice_view(request):
    customers = Customer.objects.order_by('full_name'); services = Service.objects.filter(is_active=True).order_by('name'); packages = ServicePackage.objects.filter(is_active=True).order_by('name'); products = Product.objects.filter(is_active=True, quantity_in_stock__gt=0).order_by('name')
    if request.method == 'POST':
        customer_id = request.POST.get('customer'); service_ids = request.POST.getlist('services'); package_ids = request.POST.getlist('packages'); product_ids = request.POST.getlist('products'); voucher_code = request.POST.get('voucher_code_hidden')
        if not customer_id or (not service_ids and not package_ids and not product_ids): return redirect('create_invoice')
        customer = Customer.objects.get(id=customer_id); selected_services = Service.objects.filter(id__in=service_ids); selected_packages = ServicePackage.objects.filter(id__in=package_ids); selected_products = Product.objects.filter(id__in=product_ids)
        sub_total = sum(s.price for s in selected_services) + sum(p.price for p in selected_packages) + sum(pr.price for pr in selected_products); discount_amount = Decimal('0'); voucher_obj = None
        if voucher_code:
            try:
                voucher_obj = Voucher.objects.get(code__iexact=voucher_code, is_active=True)
                if not (voucher_obj.valid_to and voucher_obj.valid_to < timezone.now()):
                    if voucher_obj.discount_type == 'percentage': discount_amount = sub_total * (voucher_obj.value / 100)
                    else: discount_amount = voucher_obj.value
                    if discount_amount > sub_total: discount_amount = sub_total
            except Voucher.DoesNotExist: voucher_obj = None
        final_amount = sub_total - discount_amount
        try:
            with transaction.atomic():
                invoice = Invoice.objects.create(customer=customer, sub_total=sub_total, discount_amount=discount_amount, final_amount=final_amount, voucher_applied=voucher_obj, status='unpaid')
                for service in selected_services: InvoiceDetail.objects.create(invoice=invoice, service=service, item_type='service', unit_price=service.price)
                for package in selected_packages: InvoiceDetail.objects.create(invoice=invoice, service_package=package, item_type='package', unit_price=package.price)
                for product in selected_products:
                    InvoiceDetail.objects.create(invoice=invoice, product=product, item_type='product', unit_price=product.price)
                    product.quantity_in_stock = F('quantity_in_stock') - 1; product.save()
            return redirect('customer_detail', customer_id=customer.id)
        except Exception as e: print(e); return redirect('create_invoice')
    context = {'customers': customers, 'services': services, 'packages': packages, 'products': products}; return render(request, 'sales/create_invoice.html', context)
@login_required
@permission_required('sales.add_payment', raise_exception=True)
def record_payment_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, id=invoice_id)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            if not (payment.amount > invoice.amount_due):
                payment.invoice = invoice
                with transaction.atomic():
                    payment.save(); invoice.paid_amount += payment.amount
                    if invoice.paid_amount >= invoice.final_amount: invoice.status = 'paid'
                    invoice.save()
            return redirect('customer_detail', customer_id=invoice.customer.id)
    else: form = PaymentForm()
    context = {'form': form, 'invoice': invoice}; return render(request, 'sales/record_payment.html', context)
@login_required
@permission_required('sales.add_packageusagehistory', raise_exception=True)
def use_package_view(request, invoice_detail_id):
    if request.method == 'POST':
        invoice_detail = get_object_or_404(InvoiceDetail, id=invoice_detail_id, item_type='package'); customer = invoice_detail.invoice.customer
        times_used = PackageUsageHistory.objects.filter(invoice_detail=invoice_detail).count()
        if times_used < invoice_detail.service_package.total_sessions: PackageUsageHistory.objects.create(invoice_detail=invoice_detail, customer=customer)
        return redirect('customer_detail', customer_id=customer.id)
    return redirect('customer_list')
@login_required
@permission_required('sales.add_appointment', raise_exception=True)
def add_appointment_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid(): appointment = form.save(commit=False); appointment.customer = customer; appointment.save()
        return redirect('customer_detail', customer_id=customer.id)
    else: form = AppointmentForm()
    context = {'form': form, 'customer': customer}; return render(request, 'sales/add_appointment.html', context)
@login_required
def appointment_form_content(request):
    form = ModalAppointmentForm(); html_form = render_to_string('sales/partials/appointment_form_partial.html', {'form': form}, request=request)
    return JsonResponse({'html_form': html_form})
@login_required
@permission_required('sales.add_appointment', raise_exception=True)
def create_appointment_api(request):
    if request.method == 'POST':
        form = ModalAppointmentForm(request.POST)
        if form.is_valid(): form.save(); return JsonResponse({'status': 'success'})
        else: return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
@login_required
def apply_voucher_api(request):
    if request.method == 'POST':
        data = json.loads(request.body); code = data.get('code'); subtotal = Decimal(data.get('subtotal', 0))
        try:
            voucher = Voucher.objects.get(code__iexact=code, is_active=True)
            if voucher.valid_to and voucher.valid_to < timezone.now(): return JsonResponse({'success': False, 'message': 'Mã đã hết hạn.'})
            discount_amount = 0
            if voucher.discount_type == 'percentage': discount_amount = subtotal * (voucher.value / 100)
            else: discount_amount = voucher.value
            if discount_amount > subtotal: discount_amount = subtotal
            return JsonResponse({'success': True, 'message': f'Áp dụng thành công!', 'discount_amount': discount_amount})
        except Voucher.DoesNotExist: return JsonResponse({'success': False, 'message': 'Mã không hợp lệ.'})
    return JsonResponse({'success': False, 'message': 'Yêu cầu không hợp lệ.'})