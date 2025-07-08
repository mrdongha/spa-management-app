# sales/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),

    # Invoice
    path('invoices/<int:invoice_id>/', views.invoice_detail_view, name='invoice_detail'),

    # Customers
    path('customers/', views.customer_list_view, name='customer_list'),
    path('customers/add/', views.add_customer_view, name='add_customer'),
    path('customers/<int:customer_id>/', views.customer_detail_view, name='customer_detail'),

    # Services
    path('services/', views.service_list_view, name='service_list'),
    path('services/add/', views.add_service_view, name='add_service'),
    path('services/<int:service_id>/edit/', views.edit_service_view, name='edit_service'),

    # Products
    path('products/', views.product_list_view, name='product_list'),
    path('products/add/', views.add_product_view, name='add_product'),
    path('products/<int:product_id>/edit/', views.edit_product_view, name='edit_product'),

    # Appointments
    path('appointments/add/', views.add_appointment_view, name='add_appointment'),
    path('calendar/', views.calendar_view, name='calendar'),

    # Reports
    path('reports/', views.report_view, name='report'),
    path('reports/staff/', view
