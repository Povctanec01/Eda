-- init.sql - исправленная версия
-- Создаем пользователя и БД
-- ВНИМАНИЕ: Этот файл выполняется от имени пользователя postgres
-- и только при ПЕРВОЙ инициализации базы данных

-- Создаем пользователя (если еще не существует)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'myuser') THEN
        CREATE USER myuser WITH PASSWORD 'mypassword';
    END IF;
END
$$;

-- Создаем БД (если еще не существует)
SELECT 'CREATE DATABASE django_db OWNER myuser'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'django_db')\gexec

-- Подключаемся к новой БД (эта команда не работает в init скриптах)
-- Вместо этого даем права на публичную схему
GRANT ALL PRIVILEGES ON DATABASE django_db TO myuser;
ALTER DATABASE django_db OWNER TO myuser;
