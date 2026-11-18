# Lokaler Modus (stdio) für Verzeichnisse und Prüfdienste wie Glama: startet den MCP-Server ohne Netzwerk-Port.
# Der Live-Betrieb (HTTP, Caddy) nutzt deploy/Dockerfile.
FROM python:3.12-slim
WORKDIR /app
RUN pip install --no-cache-dir "mcp>=2.3,<3"
COPY pflichtwerk_server.py pflichten.json angebot.json server.json ./
ENV DUTYKIT_PROTOKOLL=0
RUN useradd -r -u 10001 dutykit
USER dutykit
CMD ["python", "pflichtwerk_server.py"]
