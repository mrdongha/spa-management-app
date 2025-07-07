# config/settings.py
import os, dj_database_url
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-your-default-local-key-for-dev')
DEBUG = 'RENDER' not in os.environ
ALLOWED_HOSTS = []
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'sales',
]
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'config.urls'
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
WSGI_APPLICATION = 'config.wsgi.application'
DATABASES = {'default': dj_database_url.config(default=f'sqlite:///{BASE_DIR / "db.sqlite3"}', conn_max_age=600)}
AUTH_PASSWORD_VALIDATORS = [{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',}, {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',}, {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',}, {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},]
LANGUAGE_CODE = 'vi'
TIME_ZONE = 'Asia/Ho_Chi_Minh'
USE_I18N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
## Bước 2: File sales/views.py (Hoàn chỉnh)
Xóa toàn bộ nội dung file và thay thế bằng code sau:

Python

# sales/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .models import *
from .forms import *
from django.utils import timezone
from decimal import Decimal
import json
from django.db import transaction
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.db.models.functions import TruncDate, TruncMonth
from django.contrib.auth.decorators import login_required

@login_required
def dashboard_view(request):
    context = {'page_title': 'Trang tổng quan'}
    return render(request, 'sales/dashboard.html', context)

@login_required
def customer_list_view(request):
    customer_list = Customer.objects.annotate(
        total_spent=Sum('invoices__final_amount', filter=Q(invoices__status='paid'))
    ).order_by('-created_at')
    paginator = Paginator(customer_list, 20) 
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_title': 'Danh sách Khách hàng', 'customers': page_obj}
    return render(request, 'sales/customer_list.html', context)

@login_required
def customer_detail_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    usage_history = PackageUsageHistory.objects.filter(customer=customer).select_related('invoice_detail__service_package').order_by('-used_at')
    context = {
        'page_title': f'Chi tiết: {customer.full_name}', 
        'customer': customer,
        'usage_history': usage_history
    }
    return render(request, 'sales/customer_detail.html', context)

# ... (Toàn bộ các hàm view khác của bạn đều chính xác, hãy đảm bảo chúng được giữ nguyên)
# Ví dụ hàm report_view:
@login_required
def report_view(request):
    paid_invoices = Invoice.objects.filter(status='paid')
    total_revenue = paid_invoices.aggregate(total=Sum('final_amount'))['total'] or 0
    invoice_count = paid_invoices.count()
    daily_revenue = paid_invoices.annotate(day=TruncDate('created_at')).values('day').annotate(daily_total=Sum('final_amount')).order_by('-day')
    monthly_revenue = paid_invoices.annotate(month=TruncMonth('created_at')).values('month').annotate(monthly_total=Sum('final_amount')).order_by('-month')
    context = {
        'page_title': 'Báo cáo & Thống kê',
        'total_revenue': total_revenue,
        'invoice_count': invoice_count,
        'daily_revenue': daily_revenue,
        'monthly_revenue': monthly_revenue,
    }
    return render(request, 'sales/reports.html', context)
# Và các hàm khác...