# config/urls.py
from django.contrib import admin
from django.urls import path, include

# Lỗi xảy ra vì biến urlpatterns này bị rỗng.
# Phiên bản đúng phải có 2 dòng path bên dưới.
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sales.urls')),
]