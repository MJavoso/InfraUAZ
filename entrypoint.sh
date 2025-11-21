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
      echo "Ejecutando migración para $app"
      python manage.py makemigrations "$app"
    done
  fi
}

function run_migrations() {
    echo "Ejecutando migraciones..."
    python manage.py migrate
}

function all_fixtures() {
    fixture_names="edificios estadosDenuncia tiposDenuncia tiposLugarReferencia programasAcademicos lugaresReferencia"
    for fixture in $fixture_names; do
        if [ -f /var/log/fixtures_loaded.log ] && grep -q "^$fixture$" /var/log/fixtures_loaded.log; then
            echo "Fixture $fixture ya cargado, omitiendo..."
            continue
        fi
        echo "Cargando fixture: $fixture"
        python manage.py loaddata "$fixture"
        echo "$fixture" >> /var/log/fixtures_loaded.log
    done
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
    --fixtures=*)
      FIXTURES="${1#--migrations=}"
      FIXTURES=$(echo "$FIXTURES" | tr -d '"')
      echo "Ejecutando fixtures para $FIXTURES"
      for fixture in $MIGRATIONS_APPS; do
        python manage.py loaddata "$fixture"
      done
      shift
      ;;
    --migrations=*)
      MIGRATIONS_APPS="${1#--migrations=}"
      MIGRATIONS_APPS=$(echo "$MIGRATIONS_APPS" | tr -d '"')
      echo "Ejecutando migraciones para $MIGRATIONS_APPS"
      for app in $MIGRATIONS_APPS; do
        make_migrations "$app"
      done
      shift
      ;;
    --migrations)
      make_migrations  # si no se pasó argumento, ejecuta global
      shift
      ;;
    --reset-admin)
      echo "Restaurando la contraseña del administrador por defecto (infrauaz@uaz.edu.mx)..."
      exec python reset_admin.py
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
    python manage.py crontab remove
    python manage.py crontab add
    python manage.py crontab show

     # Iniciar el demonio 'cron' en segundo plano. E
    echo "Iniciando el demonio cron (crond)..."
 
    # redirige los logs del cron al stdout del contenedor, así ves la ejecución de tus jobs.
    crond -f -L /dev/stdout &
    
    # Iniciar el servidor (proceso principal)
    echo "Iniciando servidor Django..."
    exec python manage.py runserver 0.0.0.0:8000
    
fi