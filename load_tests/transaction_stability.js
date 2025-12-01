import http from "k6/http";
import { check, sleep } from "k6";
import { SharedArray } from "k6/data";

// BASE_URL=https://example.com
// JWT_TOKEN=eyJhbGciOi...
// PRODUCT_IDS=1,2,3

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const TOKEN = __ENV.JWT_TOKEN || "";
const PRODUCT_IDS = new SharedArray("products", () =>
  (__ENV.PRODUCT_IDS || "1").split(",").map((id) => Number(id.trim())),
);

export let options = {
  scenarios: {
    orders: {
      executor: "constant-vus",
      vus: 30,
      duration: "90s",
      exec: "createOrder",
    },
    stock_updates: {
      executor: "constant-vus",
      vus: 10,
      duration: "90s",
      exec: "updateStock",
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.03"],
    http_req_duration: ["p(95)<1200"],
  },
};

const headers = { "Content-Type": "application/json", Authorization: `Bearer ${TOKEN}` };

export function createOrder() {
  const productId = PRODUCT_IDS[Math.floor(Math.random() * PRODUCT_IDS.length)];
  const res = http.post(
    `${BASE_URL}/api/store/order-requests/`,
    JSON.stringify({
      user: 1,
      full_name: "Txn User",
      phone: "+100000000",
      email: "txn@example.com",
      delivery_type: "pickup",
      pickup_point: 1,
      payment_method: "card_now",
      cart_snapshot: [{ product_id: productId, name: "Test", quantity: 1, price: 20.0 }],
      total_amount: 20.0,
      status: "new",
      accept_terms: true,
    }),
    { headers },
  );
  check(res, { "order 201": (r) => r.status === 201 });
  sleep(0.3);
}

export function updateStock() {
  const productId = PRODUCT_IDS[Math.floor(Math.random() * PRODUCT_IDS.length)];
  // Простое изменение остатков (PATCH/PUT). При необходимости заменить на реальный ID склада.
  const res = http.post(
    `${BASE_URL}/api/store/stocks/`,
    JSON.stringify({ product: productId, warehouse: 1, quantity: Math.floor(Math.random() * 50) + 1 }),
    { headers },
  );
  check(res, { "stock 201/200": (r) => r.status === 201 || r.status === 200 });
  sleep(0.5);
}
