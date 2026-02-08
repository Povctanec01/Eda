#!/bin/bash
set -e

echo "Ожидание готовности БД..."
# Используем psql для проверки готовности БД
until PGPASSWORD=mypassword psql -h db -U myuser -d django_db -c '\q' 2>/dev/null; do
    echo "База данных еще не готова, ждем..."
    sleep 2
done
echo "База данных готова!"

echo "Применение миграций..."
python manage.py migrate

echo "Настройка прав для статики..."
# Создаем папку для статики с правильными правами
mkdir -p /app/static
chmod 755 /app/static || true

echo "Сбор статических файлов..."
# Пропускаем collectstatic если не получается
python manage.py collectstatic --noinput --clear 2>/dev/null || \
    echo "ВНИМАНИЕ: Не удалось собрать статику, продолжаем без неё"

echo "Запуск Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 Test_docker.wsgi:application
