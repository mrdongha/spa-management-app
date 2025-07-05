# sales/forms.py

from django import forms
from .models import Customer, Payment, Product, Appointment, Service

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        # Thêm 'profile_code' vào đây
        fields = ['profile_code', 'full_name', 'phone_number', 'email']
        widgets = {
            # Thêm widget cho 'profile_code'
            'profile_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập mã hồ sơ (nếu có)'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập họ và tên'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập số điện thoại'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Nhập email (không bắt buộc)'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount_paid', 'payment_method']
        widgets = {
            'amount_paid': forms.NumberInput(attrs={'class': 'form-control'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'price']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
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
            'customer': forms.HiddenInput(),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'service': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.HiddenInput(),
        }