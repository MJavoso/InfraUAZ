#!/bin/sh

RUN_SERVER=false

function await_db() {
    echo "Conectándose a la base de datos ($DB_HOST:$DB_PORT)..."
    while ! nc -z $DB_HOST $DB_PORT; do
        sleep 1
    done
    echo "Base de datos disponible"
}

function make_migrations() {
  # Si no se pasan argumentos, hace makemigrations global
  if [ $# -eq 0 ]; then
    python manage.py makemigrations
  else
    for app in "$@"; do
      python manage.py makemigrations "$app"
    done
  fi
}

function run_migrations() {
    echo "Ejecutando migraciones..."
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
    --migrations)
      # Espera argumento tipo --migrations="app1 app2"
      if [[ "$1" == *=* ]]; then
        MIGRATIONS_APPS="${1#*=}"
        MIGRATIONS_APPS=$(echo "$MIGRATIONS_APPS" | tr -d '"')
        for app in $MIGRATIONS_APPS; do
          make_migrations "$app"
        done
      else
        make_migrations  # si no se pasó argumento, ejecuta global
      fi
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
    python init_admin.py
    exec python manage.py runserver 0.0.0.0:8000
fi