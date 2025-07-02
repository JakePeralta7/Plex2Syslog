FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8080

ENV SYSLOG_HOST=localhost
ENV SYSLOG_PORT=514

CMD ["python", "app.py"]
