# sales/forms.py

from django import forms
from .models import Customer, Payment, Product, Appointment, Service, ServicePackage, GiftCard

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['profile_code', 'full_name', 'phone_number', 'email']
        widgets = {
            'profile_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập mã hồ sơ (nếu có)'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập họ và tên'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập số điện thoại'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Nhập email (không bắt buộc)'}),
        }

class PaymentForm(forms.ModelForm):
    # Thêm một trường mới không thuộc model để nhập số tiền tín dụng muốn dùng
    use_credit = forms.DecimalField(
        max_digits=12, 
        decimal_places=2,
        label="Sử dụng từ Tín dụng", 
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Payment
        # amount_paid bây giờ sẽ là số tiền trả bằng các phương thức khác (tiền mặt, thẻ...)
        fields = ['amount_paid', 'payment_method']
        labels = {
            'amount_paid': 'Số tiền trả thêm (Tiền mặt/Thẻ/CK)'
        }
        widgets = {
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price', 'quantity_in_stock', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'quantity_in_stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        
class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'price', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['customer', 'start_time', 'end_time', 'service', 'status']
        widgets = {
            'customer': forms.Select(attrs={'class': 'form-control'}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }

class ModalAppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['customer', 'start_time', 'end_time', 'service', 'status']
        widgets = {