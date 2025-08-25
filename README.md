# Minimal FastAPI SaaS Skeleton

## Çalıştırma

1. `cp ops/.env.example ops/.env` (gerekirse DB portu çakışıyorsa 5433 yap)
2. `docker compose -f ops/docker-compose.yml up -d --build`
3. Sağlık: `curl http://localhost:8000/health` -> `{"status":"ok","db":"ok","version":"0.1.0"}`
4. Migration: `docker compose -f ops/docker-compose.yml exec backend alembic upgrade head`

> Port çakışması notu: Lokal Postgres 5432 kullanıyorsa compose dosyasında `5432:5432` yerine `5433:5432` map et.

## Alembic Komut Örnekleri

- `docker compose -f ops/docker-compose.yml exec backend alembic upgrade head`
- `docker compose -f ops/docker-compose.yml exec backend alembic history`
