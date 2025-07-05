# sales/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import Customer, Appointment, Invoice, Service
from .forms import CustomerForm, AppointmentForm, ModalAppointmentForm

# ==============================================================================
# ĐÂY LÀ CÁC HÀM CÒN THIẾU GÂY RA LỖI
# ==============================================================================

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


def all_appointments_json(request):
    """
    Hàm này cung cấp dữ liệu lịch hẹn dưới dạng JSON cho calendar.
    """
    appointments = Appointment.objects.all().select_related('customer', 'service')
    data = []
    for appointment in appointments:
        # Kiểm tra xem dịch vụ có tồn tại không để tránh lỗi
        service_name = appointment.service.name if appointment.service else "Dịch vụ đã xóa"
        data.append({
            'title': f"{appointment.customer.full_name} - {service_name}",
            'start': appointment.start_time.isoformat(),
            'end': appointment.end_time.isoformat(),
            'id': appointment.id,
        })
    return JsonResponse(data, safe=False)

# ==============================================================================
# CÁC HÀM KHÁC CÓ THỂ BẠN ĐANG DÙNG (DỰA THEO GỢI Ý LỖI)
# ==============================================================================

def dashboard_view(request):
    """
    Một hàm ví dụ cho trang dashboard chính.
    Bạn có thể thay đổi nội dung hàm này cho phù hợp với dự án.
    """
    context = {
        'page_title': 'Trang tổng quan'
    }
    # Yêu cầu phải có file template tại: sales/templates/sales/dashboard.html
    return render(request, 'sales/dashboard.html', context)


def add_appointment_view(request):
    """
    Hàm để thêm một lịch hẹn mới.
    """
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard_view') # Chuyển hướng về trang dashboard sau khi lưu
    else:
        form = AppointmentForm()

    context = {
        'form': form
    }
    # Yêu cầu phải có file template tại: sales/templates/sales/add_appointment.html
    return render(request, 'sales/add_appointment.html', context)

# Thêm các hàm view khác của bạn ở đây nếu có...