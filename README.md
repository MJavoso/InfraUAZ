# InfraUAZ

##  Construcción y Ejecución

> [!IMPORTANT]
> Para construir el proyecto, es necesario tener instalado Docker y Docker Compose.

Ubicarse en la carpeta raíz del proyecto. Una vez ahí, ejecutar el comando:
```
docker compose up -d
```

Para volver a construir el contenedor desde cero, agrega la opción `--build` o `--force-recreate`.

> [!NOTE]
> Si no te funciona `docker compose`, puedes usar la variante `docker-compose`

Con eso, el servidor estará disponible en `http://localhost:8000`.

Para dejar de correr el servidor, puedes ejecutar:
```
docker compose down
```

Con esto, se destruirán los contenedores y la red. Para borrar también los volumenes usados, agrega la opción `-v` al final del comando.

Alternativamente, puedes usar el comando:
```
docker compose stop
```

Con este comando, solo se detendrán los contenedores, pero no se eliminarán.

Para detener cada contenedor individual, y remover la red y el volumen de la base de datos manualmente, puedes usar alguno de los siguientes comandos:
```
docker compose stop web-app
docker compose stop db
docker network rm infrauaz_default
docker volume rm infrauaz_db
```