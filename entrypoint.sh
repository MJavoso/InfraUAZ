#!/bin/sh

RUN_SERVER=false

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

function all_fixtures() {
    python manage.py loaddata edificios
    python manage.py loaddata estadosDenuncia
    python manage.py loaddata tiposDenuncia
    python manage.py loaddata tiposLugarReferencia
    python manage.py loaddata programasAcademicos
    python manage.py loaddata lugaresReferencia
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
    --all-fixtures)
      all_fixtures
      shift
      ;;
    --runserver)
      RUN_SERVER=true
      shift
      ;;
    *)
      shift
      ;;
  esac
done

if [ "$RUN_SERVER" = true ] ; then
    # Iniciar el servidor (usualmente gunicorn o runserver)
    echo "Iniciando servidor..."
    exec python manage.py runserver 0.0.0.0:8000
fi