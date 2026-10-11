import http from 'k6/http';
import { check, sleep } from 'k6';
export const options = {
  stages: [{duration: '10s', target: 5}, {duration: '30s', target: 10}, {duration: '10s', target: 0}],
  thresholds: {http_req_failed: ['rate<0.01'], http_req_duration: ['p(95)<300'], checks: ['rate>0.99']},
};
export default function () {
  const response = http.post(`${__ENV.BASE_URL || 'http://api:8000'}/api/calculate`, JSON.stringify({a: 2, b: 3}), {headers: {'Content-Type': 'application/json'}});
  check(response, {'200 e soma correta': r => r.status === 200 && r.json('result') === 5});
  sleep(0.1);
}
