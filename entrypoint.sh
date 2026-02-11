#!/bin/bash
set -e

echo "Ожидание готовности БД..."
until PGPASSWORD=mypassword psql -h db -U myuser -d django_db -c '\q' 2>/dev/null; do
    echo "База данных еще не готова, ждем..."
    sleep 2
done
echo "База данных готова!"

echo "Применение миграций..."
python manage.py migrate

echo "Настройка прав для статики..."
mkdir -p /app/static_collected
chmod -R 755 /app/static_collected || true

chown -R django-user:django-user /app/static_collected || true

echo "Сбор статических файлов..."
export DEBUG=1
python manage.py collectstatic --noinput --clear

echo "Запуск Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 cafeteria.wsgi:application