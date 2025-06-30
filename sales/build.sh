#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

# Lệnh này sẽ đọc các biến môi trường bạn vừa cài đặt ở trên và tạo user
echo "Creating superuser..."
python manage.py createsuperuser --no-input || echo "Superuser already exists."