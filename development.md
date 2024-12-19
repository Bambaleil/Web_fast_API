# FastAPI Project - Development

## Docker Compose

* Запустить локальный стек с помощью Docker Compose:

```bash
docker compose watch
```
Backend, JSON based web API based on OpenAPI: http://localhost:8000

Автоматическое интерактивное документирование с помощью Swagger UI (from the OpenAPI backend): http://localhost:8000/docs

Adminer, database web administration: http://localhost:8080

Traefik UI, to see how the routes are being handled by the proxy: http://localhost:8090