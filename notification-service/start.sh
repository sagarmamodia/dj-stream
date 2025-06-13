#!/bin/bash 

set -e 

# wait for rabbitmq
echo "Waiting for RabbitMQ to be ready..."

while ! nc -z rabbitmq 5672; do
  sleep 1
done

echo "RabbitMQ is up — executing command"

#wait for redis 
echo "Waiting for redis to be ready..."

while ! nc -z redis 6379; do 
  sleep 1
done

echo "Redis is up - executing command"

python main.py &
python consumer.py 

exec "$@"
