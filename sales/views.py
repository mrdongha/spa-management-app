# sales/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Customer, Appointment, Invoice, Service
from .forms import CustomerForm, AppointmentForm, ModalAppointmentForm
import json # <<< THÊM DÒNG NÀY VÀO ĐẦU FILE

# ==============================================================================
# CÁC HÀM VIEW CHÍNH CHO CÁC TRANG
# ==============================================================================

def dashboard_view(request):
    """
    Hàm ví dụ cho trang dashboard chính.
    """
    context = {
        'page_title': 'Trang tổng quan'
    }
    # Yêu cầu phải có file template tại: sales/templates/sales/dashboard.html
    return render(request, 'sales/dashboard.html', context)

def calendar_view(request):
    """
    Hàm này để hiển thị trang lịch hẹn.
    """
    context = {
        'page_title': 'Lịch hẹn'
    }
    # Yêu cầu phải có file template tại: sales/templates/sales/calendar.html
    return render(request, 'sales/calendar.html', context)

def report_view(request):
    """
    Hàm này để xử lý trang báo cáo.
    """
    paid_invoices = Invoice.objects.filter(status='paid').order_by('-created_at')
    total_revenue = sum(invoice.final_amount for invoice in paid_invoices)

    context = {
        'invoices': paid_invoices,
        'total_revenue': total_revenue,
        'invoice_count': paid_invoices.count()
    }
    # Yêu cầu phải có file template tại: sales/templates/sales/reports.html
    return render(request, 'sales/reports.html', context)

def add_appointment_view(request):
    """
    Hàm để thêm một lịch hẹn mới (dạng trang riêng).
    """
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard_view')
    else:
        form = AppointmentForm()

    context = {
        'form': form
    }
    # Yêu cầu phải có file template tại: sales/templates/sales/add_appointment.html
    return render(request, 'sales/add_appointment.html', context)

# ==============================================================================
# CÁC HÀM VIEW CHO API VÀ CÁC THÀNH PHẦN PHỤ
# ==============================================================================

def all_appointments_json(request):
    """
    Hàm này cung cấp dữ liệu lịch hẹn dưới dạng JSON cho calendar.
    """
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
    """
    Hàm này trả về nội dung HTML của form đặt lịch hẹn (ModalAppointmentForm).
    """
    form = ModalAppointmentForm()
    # Yêu cầu phải có file template tại: sales/templates/sales/partials/appointment_form_modal.html
    return render(request, 'sales/partials/appointment_form_modal.html', {'form': form})

def create_appointment_api(request):
    """
    Hàm API để tạo lịch hẹn từ form trong modal.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Giả định dữ liệu gửi lên có các key tương ứng với model Appointment
            # Cần xử lý và xác thực dữ liệu này cẩn thận hơn trong thực tế
            customer_id = data.get('customer')
            service_id = data.get('service')
            
            customer = Customer.objects.get(id=customer_id)
            service = Service.objects.get(id=service_id)

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