# sales/forms.py
from django import forms
from .models import Customer, Payment, Appointment, Service, Product # Thêm Product
from django.contrib.auth.models import User

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['full_name', 'phone_number', 'email']
        widgets = {'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập họ và tên'}),'phone_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập số điện thoại'}),'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Nhập email (không bắt buộc)'}),}

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'payment_method']
        widgets = {'amount': forms.NumberInput(attrs={'class': 'form-control'}),'payment_method': forms.Select(choices=[('cash', 'Tiền mặt'), ('card', 'Thẻ'), ('transfer', 'Chuyển khoản')], attrs={'class': 'form-select'}),}
            
class AppointmentForm(forms.ModelForm):
    staff_queryset = User.objects.filter(is_superuser=False, is_active=True)
    service = forms.ModelChoiceField(queryset=Service.objects.filter(is_active=True), label="Dịch vụ", widget=forms.Select(attrs={'class': 'form-select'}))
    staff = forms.ModelChoiceField(queryset=staff_queryset, label="Nhân viên thực hiện", required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    start_time = forms.DateTimeField(label="Thời gian bắt đầu", widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}))
    end_time = forms.DateTimeField(label="Thời gian kết thúc", widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}))
    notes = forms.CharField(label="Ghi chú", required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    class Meta:
        model = Appointment
        fields = ['service', 'staff', 'start_time', 'end_time', 'notes']

class ModalAppointmentForm(forms.ModelForm):
    customer = forms.ModelChoiceField(queryset=Customer.objects.order_by('full_name'),label="Khách hàng",widget=forms.Select(attrs={'class': 'form-select'}))
    staff_queryset = User.objects.filter(is_superuser=False, is_active=True)
    service = forms.ModelChoiceField(queryset=Service.objects.filter(is_active=True), label="Dịch vụ", widget=forms.Select(attrs={'class': 'form-select'}))
    staff = forms.ModelChoiceField(queryset=staff_queryset, label="Nhân viên thực hiện", required=False, widget=forms.Select(attrs={'class': 'form-select'}))
    start_time = forms.DateTimeField(label="Thời gian bắt đầu", widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control', 'readonly': True}))
    end_time = forms.DateTimeField(label="Thời gian kết thúc", widget=forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}))
    notes = forms.CharField(label="Ghi chú", required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    class Meta:
        model = Appointment
        fields = ['customer', 'service', 'staff', 'start_time', 'end_time', 'notes']

# ✅ THÊM MỚI: Form cho Product
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