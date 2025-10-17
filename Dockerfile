FROM python:3.11.14-alpine3.21

RUN apk add --no-cache gcc musl-dev libpq-dev

WORKDIR /InfraUAZ
COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]