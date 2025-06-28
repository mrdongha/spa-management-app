# config/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Đường dẫn cho trang admin
    path('admin/', admin.site.urls),

    # ✅ Dòng này chỉ định rằng khi người dùng truy cập vào trang chủ (ví dụ: https://ten-cua-ban.onrender.com/),
    # Django sẽ sử dụng các đường dẫn trong tệp 'sales.urls' để xử lý.
    path('', include('sales.urls')),
]