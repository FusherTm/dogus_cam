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
8. Ürün CRUD örnekleri:
   `curl -s -X POST http://localhost:8000/products \\
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \\
     -d '{"name":"Sample","sku":"SKU123","price":9.99}'`
   `curl -s http://localhost:8000/products -H "Authorization: Bearer $TOKEN"`
   `PROD_ID=<dönen_id>`
   `curl -s http://localhost:8000/products/$PROD_ID -H "Authorization: Bearer $TOKEN"`
   `curl -s -X PUT http://localhost:8000/products/$PROD_ID \\
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \\
     -d '{"price":19.99}'`
   `curl -s -X DELETE http://localhost:8000/products/$PROD_ID -H "Authorization: Bearer $TOKEN"`
9. Kategori CRUD örnekleri:
   `curl -s -X POST http://localhost:8000/categories \\
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \\
     -d '{"name":"Electronics","code":"ELEC"}'`
   `curl -s http://localhost:8000/categories -H "Authorization: Bearer $TOKEN"`
   `CAT_ID=<dönen_id>`
   `curl -s http://localhost:8000/categories/$CAT_ID -H "Authorization: Bearer $TOKEN"`
   `curl -s -X PUT http://localhost:8000/categories/$CAT_ID \\
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \\
     -d '{"name":"NewName"}'`
   `curl -s -X DELETE http://localhost:8000/categories/$CAT_ID -H "Authorization: Bearer $TOKEN"`

10. Depo ve stok hareketi örnekleri:
   `curl -s -X POST http://localhost:8000/warehouses \\
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \\
     -d '{"name":"Main","code":"MAIN"}'`
   `curl -s http://localhost:8000/warehouses -H "Authorization: Bearer $TOKEN"`
   `WH_ID=<dönen_id>`
   `PROD_ID=<önceden_oluşturulan_urun_id>`
   `curl -s -X POST http://localhost:8000/stock-movements \\
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \\
     -d '{"product_id":"'$PROD_ID'","warehouse_id":"'$WH_ID'","direction":"IN","quantity":5}'`
   `curl -s -X POST http://localhost:8000/stock-movements \\
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \\
     -d '{"product_id":"'$PROD_ID'","warehouse_id":"'$WH_ID'","direction":"OUT","quantity":2}'`
   `curl -i -X POST http://localhost:8000/stock-movements \\
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \\
     -d '{"product_id":"'$PROD_ID'","warehouse_id":"'$WH_ID'","direction":"OUT","quantity":99}'`
   `curl -s http://localhost:8000/stock/product/$PROD_ID -H "Authorization: Bearer $TOKEN"`

11. Partner CRUD örnekleri:
   `curl -s -X POST http://localhost:8000/partners \\
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \\
     -d '{"name":"Acme","type":"customer","tax_number":"TN123"}'`
   `curl -s http://localhost:8000/partners -H "Authorization: Bearer $TOKEN"`
   `PART_ID=<dönen_id>`
   `curl -s http://localhost:8000/partners/$PART_ID -H "Authorization: Bearer $TOKEN"`
   `curl -s -X PUT http://localhost:8000/partners/$PART_ID \\
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \\
     -d '{"phone":"555-0000"}'`
   `curl -s -X DELETE http://localhost:8000/partners/$PART_ID -H "Authorization: Bearer $TOKEN"`

12. Satış Teklifleri örnekleri:
   `QUOTE_PARTNER_ID=<önceden_oluşturulmuş_partner_id>`
   `QUOTE_PROD_ID=<önceden_oluşturulmuş_urun_id>`
   `curl -s -X POST http://localhost:8000/sales/quotes \\`
   `  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \\`
   `  -d '{"partner_id":"'$QUOTE_PARTNER_ID'","items":[{"product_id":"'$QUOTE_PROD_ID'","quantity":1,"unit_price":100}]}'`
   `curl -s http://localhost:8000/sales/quotes -H "Authorization: Bearer $TOKEN"`
   `QUOTE_ID=<dönen_id>`
   `curl -s -X POST http://localhost:8000/sales/quotes/$QUOTE_ID/status \\`
   `  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \\`
   `  -d '{"status":"SENT"}'`
13. Satış Siparişleri ve tekliften dönüşüm:
   `curl -s -X POST http://localhost:8000/sales/quotes/$QUOTE_ID/status \`
   `  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \`
   `  -d '{"status":"APPROVED"}'`
   `curl -s -X POST http://localhost:8000/sales/quotes/$QUOTE_ID/to-order \`
   `  -H "Authorization: Bearer $TOKEN"`
   `ORDER_ID=<dönen_id>`
   `curl -s -X POST http://localhost:8000/sales/orders/$ORDER_ID/status \`
   `  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \`
   `  -d '{"status":"CONFIRMED"}'`
   `curl -s -X POST http://localhost:8000/sales/orders/$ORDER_ID/status \`
   `  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \`
   `  -d '{"status":"FULFILLED"}'`
14. Satış Faturaları örnekleri:
   `INV_PARTNER_ID=<önceden_oluşturulmuş_partner_id>`
   `INV_PROD_ID=<önceden_oluşturulmuş_urun_id>`
   `curl -s -X POST http://localhost:8000/sales/invoices \\
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \\
     -d '{"partner_id":"'$INV_PARTNER_ID'","items":[{"product_id":"'$INV_PROD_ID'","quantity":1,"unit_price":100}]}'`
   `curl -s http://localhost:8000/sales/invoices -H "Authorization: Bearer $TOKEN"`
   `INV_ID=<dönen_id>`
   `curl -s -X POST http://localhost:8000/sales/invoices/$INV_ID/status \\
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \\
     -d '{"status":"ISSUED"}'`

15. Ürün restock_level güncelleme:
   `PROD_ID=<ürün_id>`
   `curl -s -X PUT http://localhost:8000/products/$PROD_ID \\
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \\
     -d '{"restock_level":10}'`

16. Dashboard özeti:
   `curl -s http://localhost:8000/dashboard/summary -H "Authorization: Bearer $TOKEN"`

## Cari Hesap Akışı

1. Fatura `ISSUED` olduğunda otomatik olarak `ar_entries` tablosuna borç kaydı düşer.
2. Tahsilatlar `POST /finance/ar/payments` ile kaydedilir ve FIFO mantığıyla açık faturalara dağıtılır.
3. `GET /finance/ar/balances/{partner_id}` uç noktası partner bazında bakiye ve fatura kırılımını döner.
4. Bir faturanın kalan bakiyesi sıfırlanınca `POST /sales/invoices/{id}/status` ile `PAID` yapılabilir.

> Port çakışması notu: Lokal Postgres 5432 kullanıyorsa compose dosyasında `5432:5432` yerine `5433:5432` map et.

> **Not:** Uygulama Postgres gerektirir. `DATABASE_URL` "postgresql" ile başlamıyorsa `RuntimeError("PostgreSQL required; run inside docker-compose")` fırlatır.

## Alembic Komut Örnekleri

- `docker compose -f ops/docker-compose.yml exec backend alembic upgrade head`
- `docker compose -f ops/docker-compose.yml exec backend alembic history`

## Test Çalıştırma

```
docker compose -f ops/docker-compose.yml up -d --build
docker compose -f ops/docker-compose.yml exec backend pytest -q
```

## Sadece container içinde çalıştır

Aşağıdaki komutları kendi makinenizde değil, mutlaka container içinde çalıştırın:

```
cp ops/.env.example ops/.env
docker compose -f ops/docker-compose.yml up -d --build
docker compose -f ops/docker-compose.yml exec backend alembic upgrade head
docker compose -f ops/docker-compose.yml exec backend pytest -q
```

Lokal makinede `alembic upgrade head` veya `pytest` çalıştırmayın.

## Web

1. `cd web && cp .env.example .env`
2. `.env` içindeki `VITE_API_BASE` değerini backend URL'ine göre düzenle
3. `npm install`
4. `npm run dev`
5. Login: `admin@example.com` / `ChangeMe123!`
6. Giriş yaptıktan sonra sidebar'dan **Products** linkine tıklayarak ürün listesini görüntüleyebilirsiniz. Admin rolünde olmayan kullanıcılar sadece listeyi görüntüler.
