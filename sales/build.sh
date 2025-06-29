#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# ✅ DÒNG MỚI: Tự động tạo superuser bằng các biến môi trường đã thêm ở trên
# Lệnh này sẽ chỉ có tác dụng trong lần deploy này
python manage.py createsuperuser --no-input