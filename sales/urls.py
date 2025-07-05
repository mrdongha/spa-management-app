# sales/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Trang chính
    path('', views.dashboard_view, name='dashboard'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('reports/', views.report_view, name='reports'),

    # Quản lý khách hàng
    path('customers/', views.customer_list_view, name='customer_list'),
    path('customers/add/', views.add_customer_view, name='add_customer'),
    path('customers/<int:customer_id>/', views.customer_detail_view, name='customer_detail'),

    # Quản lý sản phẩm
    path('products/', views.product_list_view, name='product_list'),
    path('products/add/', views.add_product_view, name='add_product'),
    path('products/<int:product_id>/edit/', views.edit_product_view, name='edit_product'),

    # Quản lý hóa đơn và thanh toán
    path('invoices/create/', views.create_invoice_view, name='create_invoice'),
    path('invoices/<int:invoice_id>/pay/', views.record_payment_view, name='record_payment'),
    
    # Quản lý gói dịch vụ
    path('packages/<int:invoice_detail_id>/use/', views.use_package_view, name='use_package'),

    # Các đường dẫn API
    path('api/all-appointments/', views.all_appointments_json, name='all_appointments_json'),
    path('api/appointment-form/', views.appointment_form_content, name='appointment_form_content'),
    path('api/create-appointment/', views.create_appointment_api, name='create_appointment_api'),
    path('api/apply-voucher/', views.apply_voucher_api, name='apply_voucher_api'),
]