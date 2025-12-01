import http from "k6/http";
import { check, sleep } from "k6";

// BASE_URL=https://example.com
// JWT_TOKEN=eyJhbGciOi...
// PRODUCT_ID=1

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const TOKEN = __ENV.JWT_TOKEN || "";
const PRODUCT_ID = __ENV.PRODUCT_ID || 1;

export let options = {
  scenarios: {
    catalog_read: {
      executor: "constant-vus",
      vus: 20,
      duration: "2m",
      exec: "getCatalog",
    },
    order_create: {
      executor: "ramping-arrival-rate",
      startRate: 5,
      timeUnit: "1s",
      preAllocatedVUs: 50,
      maxVUs: 200,
      stages: [
        { duration: "30s", target: 10 },
        { duration: "1m", target: 20 },
        { duration: "30s", target: 0 },
      ],
      exec: "postOrder",
    },
  },
  thresholds: {
    http_req_failed: ["rate<0.02"],
    http_req_duration: ["p(95)<800", "p(99)<1200"],
  },
};

export function getCatalog() {
  const res = http.get(`${BASE_URL}/api/store/products/?limit=20&offset=0&search=test`);
  check(res, { "catalog 200": (r) => r.status === 200 });
  sleep(1);
}

export function postOrder() {
  const headers = { "Content-Type": "application/json", Authorization: `Bearer ${TOKEN}` };
  const res = http.post(
    `${BASE_URL}/api/store/order-requests/`,
    JSON.stringify({
      user: 1,
      full_name: "Load Mix User",
      phone: "+100000000",
      email: "mix@example.com",
      delivery_type: "pickup",
      pickup_point: 1,
      payment_method: "card_now",
      cart_snapshot: [{ product_id: Number(PRODUCT_ID), name: "Test", quantity: 1, price: 50.0 }],
      total_amount: 50.0,
      status: "new",
      accept_terms: true,
    }),
    { headers },
  );
  check(res, { "order 201": (r) => r.status === 201 });
  sleep(0.5);
}
