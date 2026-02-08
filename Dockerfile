# Используем официальный Python образ
FROM python:3.12-slim

# Устанавливаем переменные окружения
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV STATIC_ROOT=/app/static

# Устанавливаем рабочую директорию
WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
        curl \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt
COPY requirements.txt /app/

# Устанавливаем зависимости Python
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Копируем проект
COPY . /app/

# Копируем entrypoint
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Создаем пользователя без привилегий
RUN adduser --disabled-password --gecos '' django-user \
    && chown -R django-user:django-user /app

# Переключаемся на пользователя
USER django-user

# Entrypoint вместо CMD
ENTRYPOINT ["/app/entrypoint.sh"]
