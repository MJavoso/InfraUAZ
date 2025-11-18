# InfraUAZ

##  Construcción y Ejecución

> [!IMPORTANT]
> Para construir el proyecto, es necesario tener instalado Docker y Docker Compose.

### Desarrollo

> [!NOTE]
> Si te encuentras en Windows, la alternativa del comando `./dc-dev` es `dc-dev.ps1`.
>
> Si al ejecutar el comando te da la siguiente salida:
> ```
> dc-dev.ps1: No se puede cargar el archivo C:\ruta\dc-dev.ps1 porque la ejecución de scripts está deshabilitada en este sistema.
> ```
> Entonces abre una terminal de PowerShell en modo administrador desde el menú de Windows, y ejecuta: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`.
>
> Luego cierra todas las terminales del IDE y abre una nueva terminal de Powershell. Ejecuta el siguiente comando:
> ```
> Get-ExecutionPolicy
> ```
> Y debería de darte como resultado: `RemoteSigned`

Ubicarse en la carpeta raíz del proyecto. Una vez ahí, ejecutar el comando:
```
./dc-dev up -d
```

Con eso, el servidor estará disponible en `http://localhost:8000`.

Para volver a construir el contenedor desde cero, agrega la opción `--build` o `--force-recreate`.

Para dejar de correr el servidor, puedes ejecutar:
```
./dc-dev down
```

Con esto, se destruirán los contenedores y la red. Para borrar también los volumenes usados, agrega la opción `-v` al final del comando.

Alternativamente, puedes usar el comando:
```
./dc-dev stop
```

Si tienes problemas al ejecutar el script, los 2 siguientes comandos son el equivalente del script y pueden reemplazarse para cualquier instrucción explicada anteriormente:
```
docker compose -f docker-compose.dev.yaml # argumentos restantes
docker-compose -f docker-compose.dev.yaml # argumentos restantes
```

### Producción
> [!NOTE]
> El archivo para editar las configuraciones de producción es `docker-compose.yaml`

Ubicarse en la carpeta raíz del proyecto. Una vez ahí, ejecutar el comando:
```
docker compose up -d
```

> [!NOTE]
> Si no te funciona `docker compose`, puedes usar la variante `docker-compose`

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
docker compose stop nginx
docker network rm infrauaz_default
docker volume rm infrauaz_db
```