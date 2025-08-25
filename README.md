# Minimal FastAPI SaaS Skeleton

## Çalıştırma

1. `cp ops/.env.example ops/.env` (gerekirse DB portu çakışıyorsa 5433 yap)
2. `docker compose -f ops/docker-compose.yml up -d --build`
3. `docker compose -f ops/docker-compose.yml exec backend alembic upgrade head`
4. Login:
   `curl -s -X POST http://localhost:8000/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"admin@example.com","password":"ChangeMe123!"}'`
5. Token ile /auth/me:
   `TOKEN=<çıkan_access_token>`
   `curl -s http://localhost:8000/auth/me -H "Authorization: Bearer $TOKEN"`
6. Admin ile /users listeleme:
   `curl -s http://localhost:8000/users -H "Authorization: Bearer $TOKEN"`
7. Normal kullanıcı ile 403 örneği:
   `USER_TOKEN=<user_token>`
   `curl -i http://localhost:8000/users -H "Authorization: Bearer $USER_TOKEN"`

> Port çakışması notu: Lokal Postgres 5432 kullanıyorsa compose dosyasında `5432:5432` yerine `5433:5432` map et.

## Alembic Komut Örnekleri

- `docker compose -f ops/docker-compose.yml exec backend alembic upgrade head`
- `docker compose -f ops/docker-compose.yml exec backend alembic history`
