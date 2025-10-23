#!/bin/sh

function await_db() {
    echo "Conectándose a la base de datos ($DB_HOST:$DB_PORT)..."
    while ! nc -z $DB_HOST $DB_PORT; do
        sleep 1
    done
    echo "Base de datos disponible"
}

function run_migrations() {
    echo "Ejecutando migraciones..."
    python manage.py makemigrations
    python manage.py migrate
}

# Procesar las banderas pasadas al script
while [[ $# -gt 0 ]]; do
  case "$1" in
    --await-db)
      await_db
      shift
      ;;
    --migrate)
      run_migrations
      shift
      ;;
    *)
      shift
      ;;
  esac
done

# Iniciar el servidor (usualmente gunicorn o runserver)
echo "Iniciando servidor..."

exec python manage.py runserver 0.0.0.0:8000