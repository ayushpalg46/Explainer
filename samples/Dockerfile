# Multi-stage Dockerfile for CloudSphere Engine
FROM python:3.12-slim AS builder

WORKDIR /app
COPY server.py .

RUN pip install --no-cache-dir pydantic

FROM python:3.12-alpine AS production

WORKDIR /app
COPY --from=builder /app /app
COPY deploy.sh .

RUN chmod +x deploy.sh

EXPOSE 8000
ENTRYPOINT ["./deploy.sh"]
