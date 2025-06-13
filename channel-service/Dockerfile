FROM python:3.11-slim 

WORKDIR /app 

RUN apt-get update && apt-get install -y netcat-openbsd

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt 

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh 

EXPOSE 8001

ENTRYPOINT ["/entrypoint.sh"]

CMD ["python", "manage.py", "runserver", "0.0.0.0:8001"]
