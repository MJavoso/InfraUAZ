#!/bin/sh

echo "Conectandose a la base de datos ($DB_HOST:$DB_PORT)..."
sleep 10

echo "Ejecutando migraciones"

python manage.py migrate

echo "Iniciando servidor..."
exec "$@"