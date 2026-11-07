FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir "mcp>=2.3,<3" "uvicorn>=0.30"
COPY pflichtwerk_server.py app.py billing.py pflichten.json ./
RUN useradd -r -u 10001 dutykit && mkdir -p /data && chown dutykit /data
USER dutykit
ENV DUTYKIT_KEYS_DATEI=/data/keys.json DUTYKIT_PROTOKOLL_DATEI=/data/protokoll.jsonl
EXPOSE 8080
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers", "--forwarded-allow-ips", "*"]
