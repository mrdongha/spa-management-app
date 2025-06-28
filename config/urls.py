# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views # ✅ THÊM DÒNG NÀY

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # ✅ THÊM CÁC ĐƯỜNG DẪN NÀY
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # Đường dẫn đến ứng dụng sales vẫn giữ nguyên
    path('', include('sales.urls')),
]