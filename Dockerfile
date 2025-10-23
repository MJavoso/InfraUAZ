FROM python:3.11.14-alpine3.21

RUN apk add --no-cache gcc musl-dev libpq-dev

WORKDIR /InfraUAZ
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

COPY entrypoint.sh /entrypoint.sh

RUN chmod 744 /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh", "--await-db", "--migrate", "--all-fixtures", "--runserver"]