import http from "k6/http";
import { check, sleep } from "k6";
import { Trend, Rate } from "k6/metrics";

// Env:
// BASE_URL=https://example.com
// JWT_TOKEN=eyJhbGciOi...
// USER_ID=1
// PRODUCT_ID=1
// PICKUP_ID=1

const BASE_URL = __ENV.BASE_URL || "http://localhost:8000";
const TOKEN = __ENV.JWT_TOKEN || "";
const USER_ID = __ENV.USER_ID || 1;
const PRODUCT_ID = __ENV.PRODUCT_ID || 1;
const PICKUP_ID = __ENV.PICKUP_ID || null;

export let options = {
  stages: [
    { duration: "30s", target: 10 },
    { duration: "1m", target: 30 },
    { duration: "1m", target: 60 },
    { duration: "30s", target: 0 },
  ],
  thresholds: {
    http_req_duration: ["p(95)<800"],
    http_req_failed: ["rate<0.01"],
  },
};

const createOrderTrend = new Trend("order_create_duration");
const orderFailRate = new Rate("order_create_fail_rate");

export default function () {
  const payload = JSON.stringify({
    user: Number(USER_ID),
    full_name: "Load Test User",
    phone: "+100000000",
    email: "load@example.com",
    delivery_type: "pickup",
    pickup_point: PICKUP_ID,
    payment_method: "card_now",
    cart_snapshot: [
      { product_id: Number(PRODUCT_ID), name: "Test product", quantity: 1, price: 100.0 },
    ],
    total_amount: 100.0,
    status: "new",
    accept_terms: true,
  });

  const headers = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${TOKEN}`,
  };

  const res = http.post(`${BASE_URL}/api/store/order-requests/`, payload, { headers });
  createOrderTrend.add(res.timings.duration);
  orderFailRate.add(res.status >= 400);

  check(res, {
    "status is 201": (r) => r.status === 201,
  });

  sleep(0.5);
}
