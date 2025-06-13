#!/bin/bash 

set -e 

# wait for rabbitmq
echo "Waiting for RabbitMQ to be ready..."

while ! nc -z rabbitmq 5672; do
  sleep 1
done

echo "RabbitMQ is up — executing command"

#wait for postgres 
echo "Waiting for postgres to be ready..."

while ! nc -z postgres 5432; do
  sleep 1 
done 

python main.py &
python consumer.py 

exec "$@"
