# sales/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
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

# ... (Toàn bộ các hàm view khác giữ nguyên) ...

@login_required
def apply_voucher_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            voucher_code = data.get('voucher_code')
            sub_total = Decimal(data.get('sub_total', '0'))

            if not voucher_code:
                return JsonResponse({'status': 'error', 'message': 'Vui lòng nhập mã voucher.'}, status=400)

            now = timezone.now()
            voucher = Voucher.objects.get(code__iexact=voucher_code, is_active=True, valid_from__lte=now)

            if voucher.valid_to and voucher.valid_to < now:
                raise Voucher.DoesNotExist

            discount_amount = Decimal('0')
            if voucher.discount_type == 'percentage':
                discount_amount = (sub_total * voucher.value) / 100
            elif voucher.discount_type == 'fixed':
                discount_amount = voucher.value
            
            final_amount = sub_total - discount_amount
            
            return JsonResponse({
                'status': 'success',
                'message': 'Áp dụng voucher thành công!',
                'discount_amount': discount_amount,
                'final_amount': final_amount,
            })

        except Voucher.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Mã voucher không hợp lệ hoặc đã hết hạn.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Có lỗi xảy ra: ' + str(e)}, status=400)
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)