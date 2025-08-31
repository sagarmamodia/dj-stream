#!/bin/bash 

set -e 

# wait for rabbitmq
echo "Waiting for RabbitMQ to be ready..."

while ! nc -z rabbitmq 5672; do
  sleep 1
done

echo "RabbitMQ is up — executing command"

#wait for elasticsearch 
echo "Waiting for elasticsearch to be ready..."

while ! nc -z elasticsearch 9200; do
  sleep 1 
done 

echo "ElasticSearch is up — executing command"

python main.py &
python consumer.py 

exec "$@"
