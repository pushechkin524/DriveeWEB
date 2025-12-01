# Тестирование отказоустойчивости

## Имитация сбоя БД
- Остановить доступ к БД на короткое время (для локального Postgres, примеры):
  - `pg_ctl stop -D /usr/local/var/postgres` либо временно закрыть порт фаерволом.
- Во время простоя выполнить API-запросы (пример):
  - `curl -i -H "Authorization: Bearer $JWT" -H "Content-Type: application/json" -d '{"user":1,"full_name":"Test","phone":"+1","email":"a@a.a","delivery_type":"pickup","pickup_point":1,"payment_method":"card_now","cart_snapshot":[{"product_id":1,"name":"Test","quantity":1,"price":10.0}],"total_amount":10.0,"status":"new","accept_terms":true}' $BASE_URL/api/store/order-requests/`
- Ожидание: контролируемая ошибка (5xx/timeout) без частично записанных данных.
- Запустить БД и повторить тот же запрос — ожидание 201/200.

## Имитация сбоя приложения
- Перезапустить gunicorn/uvicorn/службу Django во время нагрузки.
- Проверить, что оставшиеся воркеры обслуживают запросы, после рестарта — сервис доступен и ответы корректны.

## Восстановление из бэкапа (Postgres)
1. Создать бэкап:
   - `pg_dump -h <host> -U <user> -d <db> -Fc -f backup.dump`
2. Внести тестовые изменения (создать пару заказов/товаров).
3. Восстановить:
   - `pg_restore -h <host> -U <user> -d <db> --clean --if-exists backup.dump`
4. Проверить целостность:
   - Выполнить миграции: `python manage.py migrate --check`
   - Прогнать health-check запросы:
     - `curl -i $BASE_URL/api/store/products/`
     - `curl -i $BASE_URL/api/store/order-requests/` (GET под токеном)
   - Убедиться, что критичные записи (пользователи, заказы) соответствуют состоянию на момент бэкапа.

## Мини-скрипт для health-check после сбоя/восстановления
```bash
#!/usr/bin/env bash
set -e

BASE_URL=${BASE_URL:-http://localhost:8000}
JWT=${JWT_TOKEN:?JWT_TOKEN required}

check() {
  local url=$1
  http_code=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $JWT" "$url")
  echo "$http_code $url"
}

check "$BASE_URL/api/store/products/"
check "$BASE_URL/api/store/order-requests/"
check "$BASE_URL/api/store/brands/"
```
Запуск: `JWT_TOKEN=<...> BASE_URL=http://localhost:8000 ./health_check.sh`
