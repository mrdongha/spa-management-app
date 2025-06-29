# config/urls.py
from django.contrib import admin
from django.urls import path, include

# Biến này phải chứa ít nhất một đường dẫn.
# Lỗi của bạn xảy ra vì biến này đang bị rỗng.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sales.urls')),
]