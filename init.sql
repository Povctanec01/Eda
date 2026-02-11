DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'myuser') THEN
        CREATE USER myuser WITH PASSWORD 'mypassword';
    END IF;
END
$$;

SELECT 'CREATE DATABASE django_db OWNER myuser'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'django_db')\gexec


GRANT ALL PRIVILEGES ON DATABASE django_db TO myuser;
ALTER DATABASE django_db OWNER TO myuser;
