#!/bin/sh
set -e

echo "Waiting for postgres..."

while ! nc -z postgres 5432; do 
  sleep 1
done

echo "postgres is up - executing command"
python manage.py makemigrations
python manage.py migrate

exec "$@"
