FROM python:3.11-slim

WORKDIR /app 

RUN apt-get update && apt-get install -y netcat-openbsd

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt 

COPY . .

COPY start.sh /start.sh 

RUN chmod +x /start.sh 

EXPOSE 8003

CMD ["/start.sh"]
