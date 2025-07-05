# sales/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.db import transaction
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from .models import Customer, Invoice, InvoiceDetail, Service, ServicePackage, Product, Payment, Voucher, Appointment, PackageUsageHistory
from .forms import CustomerForm, PaymentForm, ProductForm, AppointmentForm, ModalAppointmentForm
import json
from django.http import JsonResponse
from django.template.loader import render_to_string

class CustomLoginView(LoginView):
    template_name = 'sales/login.html'
    redirect_authenticated_user = True
    next_url = reverse_lazy('dashboard')

@login_required
def dashboard_view(request):
    total_customers = Customer.objects.count()
    
    today = timezone.now().date()
    start_of_month = today.replace(day=1)
    
    total_revenue = Payment.objects.aggregate(total=Sum('amount'))['total'] or 0
    today_revenue = Payment.objects.filter(payment_time__date=today).aggregate(total=Sum('amount'))['total'] or 0
    new_customers_month = Customer.objects.filter(created_at__gte=start_of_month).count()

    thirty_days_ago = today - timedelta(days=30)
    daily_revenue = Payment.objects.filter(payment_time__date__gte=thirty_days_ago) \
        .values('payment_time__date') \
        .annotate(daily_total=Sum('amount')) \
        .order_by('payment_time__date')

    labels = [(thirty_days_ago + timedelta(days=i)).strftime('%d/%m') for i in range(31)]
    revenue_data = [0] * 31
    for item in daily_revenue:
        day_index = (item['payment_time__date'] - thirty_days_ago).days
        if 0 <= day_index < 31:
            revenue_data[day_index] = float(item['daily_total'])

    top_services = InvoiceDetail.objects.exclude(service__isnull=True) \
        .values('service__name') \
        .annotate(count=Count('id')) \
        .order_by('-count')[:5]

    context = {
        'total_customers': total_customers,
        'total_revenue': total_revenue,
        'today_revenue': today_revenue,
        'new_customers_month': new_customers_month,
        'chart_labels': json.dumps(labels),
        'chart_data': json.dumps(revenue_data),
        'top_services': top_services,
    }
    return render(request, 'sales/dashboard.html', context)

@login_required
@permission_required('sales.view_customer', raise_exception=True)
def customer_list_view(request):
    customers = Customer.objects.all().order_by('-created_at')
    return render(request, 'sales/customer_list.html', {'customers': customers})

@login_required
@permission_required('sales.add_customer', raise_exception=True)
def add_customer_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'sales/add_customer.html', {'form': form})

@login_required
@permission_required('sales.view_customer', raise_exception=True)
def customer_detail_view(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    invoices = customer.invoices.all().order_by('-created_at')
    customer_invoice_details_packages = InvoiceDetail.objects.filter(
        invoice__customer=customer, item_type='package'
    ).annotate(
        times_used=Count('packageusagehistory'),
        sessions_left=F('service_package__total_sessions') - Count('packageusagehistory')
    )
    return render(request, 'sales/customer_detail.html', {
        'customer': customer,
        'invoices': invoices,
        'customer_invoice_details_packages': customer_invoice_details_packages
    })

@login_required
@permission_required('sales.add_invoice', raise_exception=True)
def create_invoice_view(request):
    services = Service.objects.filter(is_active=True)
    packages = ServicePackage.objects.filter(is_active=True)
    products = Product.objects.filter(is_active=True)
    customers = Customer.objects.all()

    if request.method == 'POST':
        data = json.loads(request.body)
        customer_id = data.get('customer_id')
        items = data.get('items', [])
        voucher_code = data.get('voucher_code', '')

        if not customer_id or not items:
            return JsonResponse({'status': 'error', 'message': 'Thiếu thông tin khách hàng hoặc dịch vụ.'}, status=400)

        customer = get_object_or_404(Customer, id=customer_id)
        
        try:
            with transaction.atomic():
                sub_total = 0
                invoice_details_to_create = []

                for item in items:
                    item_id = item.get('id')
                    item_type = item.get('type')
                    quantity = int(item.get('quantity', 1))
                    
                    if item_type == 'service':
                        obj = get_object_or_404(Service, id=item_id)
                        unit_price = obj.price
                        detail = InvoiceDetail(item_type='service', service=obj, quantity=quantity, unit_price=unit_price)
                    elif item_type == 'package':
                        obj = get_object_or_404(ServicePackage, id=item_id)
                        unit_price = obj.price
                        detail = InvoiceDetail(item_type='package', service_package=obj, quantity=quantity, unit_price=unit_price)
                    elif item_type == 'product':
                        obj = get_object_or_404(Product, id=item_id)
                        if obj.quantity_in_stock < quantity:
                            raise Exception(f"Sản phẩm '{obj.name}' không đủ tồn kho.")
                        unit_price = obj.price
                        obj.quantity_in_stock -= quantity
                        obj.save()
                        detail = InvoiceDetail(item_type='product', product=obj, quantity=quantity, unit_price=unit_price)
                    else:
                        continue
                    
                    sub_total += unit_price * quantity
                    invoice_details_to_create.append(detail)

                discount_amount = 0
                voucher = None
                if voucher_code:
                    try:
                        voucher = Voucher.objects.get(code__iexact=voucher_code, is_active=True, valid_from__lte=timezone.now())
                        if voucher.valid_to and voucher.valid_to < timezone.now():
                            raise Voucher.DoesNotExist
                        
                        if voucher.discount_type == 'percentage':
                            discount_amount = (sub_total * voucher.value) / 100
                        else: # fixed amount
                            discount_amount = voucher.value
                        
                        if discount_amount > sub_total:
                            discount_amount = sub_total

                    except Voucher.DoesNotExist:
                        return JsonResponse({'status': 'error', 'message': 'Voucher không hợp lệ.'}, status=400)

                final_amount = sub_total - discount_amount

                new_invoice = Invoice.objects.create(
                    customer=customer,
                    voucher_applied=voucher,
                    sub_total=sub_total,
                    discount_amount=discount_amount,
                    final_amount=final_amount
                )

                for detail in invoice_details_to_create:
                    detail.invoice = new_invoice
                InvoiceDetail.objects.bulk_create(invoice_details_to_create)

                return JsonResponse({'status': 'success', 'invoice_id': new_invoice.id})
        
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    context = {
        'services': services,
        'packages': packages,
        'products': products,
        'customers': customers
    }
    return render(request, 'sales/create_invoice.html', context)

# ✅ HÀM NÀY SẼ SỬA LỖI 500
@login_required
@permission_required('sales.add_payment', raise_exception=True)
def record_payment_view(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    payment = form.save(commit=False)
                    payment.invoice = invoice
                    
                    # Kiểm tra thanh toán không vượt quá số tiền còn nợ
                    amount_due_before_payment = invoice.amount_due
                    if payment.amount > amount_due_before_payment:
                        form.add_error('amount', f"Số tiền thanh toán không được lớn hơn số tiền còn lại ({amount_due_before_payment:,.0f}đ).")
                    else:
                        payment.save()
                        
                        # Cập nhật lại hóa đơn
                        invoice.paid_amount = F('paid_amount') + payment.amount
                        invoice.save()
                        invoice.refresh_from_db() # Lấy lại dữ liệu mới nhất từ DB
                        
                        # Cập nhật trạng thái hóa đơn
                        if invoice.amount_due <= 0:
                            invoice.status = 'paid'
                            invoice.save()
                            
                        return redirect('customer_detail', pk=invoice.customer.pk)

            except Exception as e:
                # Có thể thêm log lỗi ở đây
                form.add_error(None, "Đã có lỗi xảy ra trong quá trình xử lý. Vui lòng thử lại.")

    else:
        # Gợi ý số tiền cần thanh toán
        initial_data = {'amount': invoice.amount_due}
        form = PaymentForm(initial=initial_data)

    return render(request, 'sales/record_payment.html', {'form': form, 'invoice': invoice})

@login_required
@permission_required('sales.view_product', raise_exception=True)
def product_list_view(request):
    products = Product.objects.all().order_by('name')
    return render(request, 'sales/product_list.html', {'products': products})

@login_required
@permission_required('sales.add_product', raise_exception=True)
def add_product_view(request):
    if request.method == 'POST':
        form = ProductForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_list')
    else:
        form = ProductForm()
    return render(request, 'sales/add_product.html', {'form': form})

# ... (các hàm còn lại giữ nguyên) ...
@login_required
@permission_required('sales.add_appointment', raise_exception=True)
def add_appointment_view(request, customer_id):
    customer = get_object_or_404(Customer, pk=customer_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.customer = customer
            appointment.save()
            return redirect('customer_detail', pk=customer.id)
    else:
        form = AppointmentForm()
    return render(request, 'sales/add_appointment.html', {'form': form, 'customer': customer})

@login_required
@permission_required('sales.add_packageusagehistory', raise_exception=True)
def use_package_view(request, detail_id):
    invoice_detail = get_object_or_404(InvoiceDetail, pk=detail_id, item_type='package')
    if request.method == 'POST':
        sessions_left = invoice_detail.service_package.total_sessions - invoice_detail.packageusagehistory.count()
        if sessions_left > 0:
            PackageUsageHistory.objects.create(
                invoice_detail=invoice_detail,
                customer=invoice_detail.invoice.customer
            )
    return redirect('customer_detail', pk=invoice_detail.invoice.customer.id)

@login_required
def calendar_view(request):
    return render(request, 'sales/calendar.html')

@login_required
def get_appointments_api(request):
    start = request.GET.get('start')
    end = request.GET.get('end')
    appointments = Appointment.objects.filter(start_time__range=[start, end])
    events = []
    for appt in appointments:
        events.append({
            'title': f"{appt.customer.full_name} - {appt.service.name}",
            'start': appt.start_time.isoformat(),
            'end': appt.end_time.isoformat(),
            'id': appt.id,
            'extendedProps': {
                'staff': appt.staff.username if appt.staff else 'N/A'
            }
        })
    return JsonResponse(events, safe=False)

@login_required
def appointment_form_content(request):
    form = ModalAppointmentForm()
    html_form = render_to_string('sales/partials/appointment_form_partial.html', {'form': form}, request=request)
    return JsonResponse({'html_form': html_form})

@login_required
@permission_required('sales.add_appointment', raise_exception=True)
def create_appointment_from_calendar(request):
    if request.method == 'POST':
        form = ModalAppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success'})
        else:
            html_form = render_to_string('sales/partials/appointment_form_partial.html', {'form': form}, request=request)
            return JsonResponse({'status': 'error', 'html_form': html_form}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)

@login_required
def apply_voucher_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        voucher_code = data.get('voucher_code')
        sub_total = data.get('sub_total', 0)
        sub_total = float(sub_total)

        try:
            voucher = Voucher.objects.get(code__iexact=voucher_code, is_active=True, valid_from__lte=timezone.now())
            if voucher.valid_to and voucher.valid_to < timezone.now():
                raise Voucher.DoesNotExist

            discount_amount = 0
            if voucher.discount_type == 'percentage':
                discount_amount = (sub_total * float(voucher.value)) / 100
            else: # fixed
                discount_amount = float(voucher.value)

            if discount_amount > sub_total:
                discount_amount = sub_total
            
            final_amount = sub_total - discount_amount

            return JsonResponse({
                'status': 'success',
                'discount_amount': discount_amount,
                'final_amount': final_amount
            })
        except Voucher.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Voucher không hợp lệ hoặc đã hết hạn.'}, status=400)
        # sales/views.py

# ... (giữ nguyên tất cả các dòng import và các hàm đã có) ...

from django.shortcuts import render
from .models import Invoice

# ... (giữ nguyên các hàm view khác của bạn) ...

# DÁN HÀM MỚI NÀY VÀO CUỐI FILE
def report_view(request):
    paid_invoices = Invoice.objects.filter(status='paid').order_by('-created_at')
    total_revenue = sum(invoice.final_amount for invoice in paid_invoices)
    
    context = {
        'invoices': paid_invoices,
        'total_revenue': total_revenue,
        'invoice_count': paid_invoices.count()
    }
    return render(request, 'sales/reports.html', context)