# syntax=docker/dockerfile
FROM python:3.13.0-alpine

WORKDIR /app

RUN apk upgrade
RUN pip install --upgrade pip

COPY requirements.txt /app
RUN pip3 install --no-cache-dir -r requirements.txt
COPY ./server /app

ENV FLASK_APP=app

EXPOSE 5000

CMD ["python", "./main.py"]
