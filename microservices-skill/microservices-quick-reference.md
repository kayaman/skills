# Microservices Skill — Quick Reference

**TL;DR for agents building microservices systems**

---

## When to Invoke This Skill

| User Says | Invoke With | What Agent Does |
|---|---|---|
| "Design microservices for X" | `/microservices-skill architecture` | Ask 5 questions → Generate ADR |
| "Build payment service in TS" | `/microservices-skill implementation typescript` | Full NestJS app |
| "Implement order service in Python" | `/microservices-skill implementation python` | Full FastAPI app |
| "Add monitoring/logging" | `/microservices-skill observability` | OpenTelemetry + structured logs |
| "How do I deploy this?" | `/microservices-skill deployment` | Dockerfile + K8s manifests |
| "Generate tests" | `/microservices-skill testing` | Unit + integration test templates |
| "Migrate from monolith" | `/microservices-skill migration` | Decomposition strategy |

---

## The 5 Discovery Questions

Always ask these **before** designing architecture:

1. **What's your domain & scale?** (users, requests/sec, data volume)
2. **What are your latency & consistency needs?** (p99 SLA, what must be strong vs. eventual)
3. **How many teams will own services?** (affects service boundaries)
4. **What's your deployment environment?** (Kubernetes, Docker Compose, Serverless?)
5. **Any compliance/security constraints?** (GDPR, PCI-DSS, HIPAA, etc.)

**Don't proceed without answers.**

---

## Service Decomposition Rules

| Rule | Reason |
|---|---|
| Each service owns its data | Prevents hidden dependencies |
| One team per service | Enables independent deployment |
| Service has clear responsibility | Easier to understand & test |
| Services are <15 total | Overhead exceeds benefits beyond that |
| Call chains <4 hops deep | Latency compounds with each hop |
| No shared databases | Breaks autonomy; creates tight coupling |

---

## Communication Patterns Quick Reference

### Synchronous (REST)

**When:** Query operations, immediate response needed

```typescript
// TypeScript example
const user = await http.get(`/user-service/users/${userId}`);
```

**Characteristics:**
- ✅ Fast feedback
- ✅ Simple to implement
- ⚠️ Tight coupling
- ⚠️ Latency compounds

**Requirements:**
- ✅ MUST have timeout (default 5s)
- ✅ MUST have retry logic
- ✅ MUST have circuit breaker
- ✅ MUST be idempotent

### Asynchronous (Events)

**When:** Notifications, loose coupling needed

```python
# Python example
await event_bus.publish("order.created", {
    "order_id": order.id,
    "user_id": user.id,
    "total": order.total
})
```

**Characteristics:**
- ✅ Loose coupling
- ✅ Scales well
- ✅ Services can fail independently
- ⚠️ Eventual consistency
- ⚠️ Harder to debug

**Requirements:**
- ✅ Events are immutable (past tense)
- ✅ Define event schema
- ✅ Publish before success response
- ✅ At-least-once delivery guarantee

### Saga Pattern (Distributed Transactions)

**When:** Multi-service operations that need to succeed/fail together

```
Order Service (orchestrator)
  → 1. Create order (PENDING)
  → 2. Call Payment Service
       If fails: compensate (delete order)
  → 3. Call Inventory Service
       If fails: refund + delete order
  → 4. Set status to CONFIRMED
```

**Requirements:**
- ✅ Idempotency keys on each call
- ✅ Compensating transaction for each step
- ✅ Timeout on each step
- ✅ Retry logic with exponential backoff

---

## Resilience Patterns

### Must Have: Timeout + Retry + Circuit Breaker

```typescript
// TypeScript with Opossum
const breaker = new CircuitBreaker(
  async () => http.get(url, { timeout: 5000 }),
  {
    threshold: 5,        // Open after 5 failures
    timeout: 30000,      // Reset after 30s
    name: "payment-service"
  }
);

try {
  return await breaker.fire();
} catch (err) {
  // Circuit is OPEN; use fallback
  return getCachedResult();
}
```

```python
# Python with pybreaker
breaker = CircuitBreaker(
    name="payment_service",
    fail_max=5,
    reset_timeout=30
)

try:
    result = await breaker.call(
        http.get,
        url,
        timeout=5
    )
except Exception:
    # Circuit OPEN; fallback
    return get_cached_result()
```

### Error Classification

| Status Code | Action |
|---|---|
| 2xx | Success |
| 4xx | Don't retry (client error) |
| 5xx | Retry with backoff |
| Timeout | Retry with exponential backoff |
| Network error | Retry with backoff |

### Exponential Backoff Formula

```
delay = baseDelay * (multiplier ^ attempt) + jitter

Examples:
  Attempt 1: 100ms + ±10%
  Attempt 2: 200ms + ±10%
  Attempt 3: 400ms + ±10%
  (stops after 3 attempts)
```

---

## Observability Checklist

### Logging (Structured JSON)

```typescript
// TypeScript
logger.info({
  event: "order_created",
  order_id: "order-123",
  user_id: "user-456",
  request_id: "req-789",  // CRITICAL: trace across services
  duration_ms: 125,
  timestamp: new Date().toISOString()
});
// Output: {"event": "order_created", ...}
```

```python
# Python
log.info(
    "order_created",
    order_id="order-123",
    user_id="user-456",
    request_id="req-789",
    duration_ms=125
)
```

### Tracing (Distributed)

```typescript
// OpenTelemetry (TypeScript)
const span = tracer.startSpan("order.create");
span.setAttribute("order_id", id);
span.setAttribute("user_id", userId);
try {
  const result = await service.create(order);
  return result;
} finally {
  span.end();
}
```

### Metrics (Prometheus)

```typescript
// TypeScript
const histogram = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request latency',
  labelNames: ['method', 'path']
});

const start = Date.now();
// ... request ...
histogram.labels('POST', '/orders').observe((Date.now() - start) / 1000);
```

### Health Checks

Every service **MUST** have:

```typescript
// TypeScript/NestJS
@Get('/health/ready')
async readiness() {
  // Can this pod accept traffic?
  const db = await database.ping();
  const cache = await redis.ping();
  
  if (!db || !cache) return { status: 'not_ready' };
  return { status: 'ready' };
}

@Get('/health/live')
async liveness() {
  // Is this pod alive?
  return { status: 'alive' };
}
```

```python
# Python/FastAPI
@app.get("/health/ready")
async def readiness():
    db_ok = await db.ping()
    cache_ok = await redis.ping()
    if not (db_ok and cache_ok):
        return {"status": "not_ready"}
    return {"status": "ready"}

@app.get("/health/live")
async def liveness():
    return {"status": "alive"}
```

---

## Security Checklist

| Item | Implementation | Example |
|---|---|---|
| Secrets | Environment variables, never in code | `DB_PASSWORD` from K8s Secret |
| Secrets rotation | Automated, regular | Rotate every 30-90 days |
| Authentication | JWT tokens | `Authorization: Bearer eyJ...` |
| Service-to-service | mTLS or API keys | Client certificate or shared secret |
| Input validation | Schema validation (Pydantic, zod) | `@IsEmail()`, `price > 0` |
| Rate limiting | Per-user rate limits | 100 req/min for public API |
| CORS | Restrict origins | `allowedOrigins: ["https://app.com"]` |
| HTTPS | TLS 1.3 | Enforced in production |

---

## Testing Pyramid

```
           /\       E2E Tests
          /  \      (1-5% coverage)
         /    \
        /______\     Integration Tests
       /        \    (20-30% coverage)
      /          \
     /____________\  Unit Tests
                      (60-70% coverage)
```

### Unit Tests (Mocked)

```typescript
// Mock dependencies
const mockRepo = jest.fn();
const service = new OrderService(mockRepo);

// Test business logic in isolation
expect(await service.create(order)).toEqual(createdOrder);
```

### Integration Tests (Real Infra)

```typescript
// Real database, event bus
const order = await service.create(orderDto);

// Verify database
const saved = await db.orders.findById(order.id);
expect(saved).toBeDefined();

// Verify events
expect(eventBus.published).toContain({
  type: 'order.created',
  order_id: order.id
});
```

### E2E Tests (User Flow)

```typescript
// Test complete flow via HTTP
const response = await http.post('/orders', orderData);
expect(response.status).toBe(201);

// Verify side effects
expect(await payment.wasCharged(amount)).toBe(true);
expect(await notification.wasEmailSent(user.email)).toBe(true);
```

---

## Deployment Checklist

### Docker

- [ ] Multi-stage build (small final image)
- [ ] Non-root user (security)
- [ ] Health check in Dockerfile
- [ ] Image size <500MB (ideally <200MB)
- [ ] No secrets in Dockerfile

### Kubernetes

- [ ] Deployment with 3+ replicas
- [ ] Readiness probe (can accept traffic?)
- [ ] Liveness probe (is it alive?)
- [ ] Resource requests set (CPU, memory)
- [ ] Resource limits set
- [ ] Graceful shutdown (preStop hook)
- [ ] ConfigMap for non-secrets
- [ ] Secret for sensitive data

### CI/CD

- [ ] Build Docker image
- [ ] Push to registry
- [ ] Run tests
- [ ] Deploy to staging
- [ ] Smoke tests
- [ ] Deploy to production (canary or blue-green)

---

## Common Mistakes & Fixes

| Mistake | Why It's Bad | Fix |
|---|---|---|
| No timeout on external calls | Service hangs indefinitely | Add `timeout: 5000` |
| No retries | Transient failures cause cascading failures | Add exponential backoff |
| No circuit breaker | One slow service blocks others | Use opossum (TS) or pybreaker (Python) |
| Shared database | Breaks service autonomy | Each service owns its schema |
| Hardcoded URLs | Can't deploy to different environments | Use service discovery or env vars |
| Non-idempotent mutations | Retries cause duplicates | Use idempotency keys |
| No logging request ID | Can't trace requests across services | Add X-Request-ID middleware |
| Secrets in code | Security breach | Use environment variables |
| No health checks | K8s doesn't know when service is ready | Implement readiness + liveness |
| No input validation | Garbage in, garbage out | Use Pydantic / class-validator |

---

## One-Page Cheat: Build a Service in 30 Min

```bash
# 1. Generate skeleton (5 min)
/microservices-skill implementation typescript
# Or: /microservices-skill implementation python

# 2. Read generated code (5 min)
# Understand structure, where to add logic

# 3. Implement domain logic (15 min)
# Copy service skeleton
# Fill in business logic
# Add HTTP handlers

# 4. Add tests (5 min)
# Run provided unit test template
# Copy integration test template

# 5. Run locally (5 min)
docker-compose up
curl -X POST http://localhost:3000/orders

# Done!
```

---

## Language Cheat Sheet

### TypeScript/NestJS

```typescript
// Install
npm install @nestjs/common @nestjs/core

// Main
import { NestFactory } from '@nestjs/core';
const app = await NestFactory.create(AppModule);
await app.listen(3000);

// Module
@Module({
  controllers: [OrderController],
  providers: [OrderService],
})
export class OrderModule {}

// Service
@Injectable()
export class OrderService {
  constructor(private repo: OrderRepository) {}
  
  async create(dto) { return this.repo.create(dto); }
}

// Controller
@Controller('orders')
export class OrderController {
  @Post()
  async create(@Body() dto) {
    return this.service.create(dto);
  }
}

// HTTP client with resilience
const breaker = new CircuitBreaker(() => http.get(url), { threshold: 5 });
return await breaker.fire();
```

### Python/FastAPI

```python
# Install
pip install fastapi uvicorn

# Main
from fastapi import FastAPI
app = FastAPI()

@app.get("/orders/{order_id}")
async def get_order(order_id: str):
    return {"order_id": order_id}

# Run: uvicorn main:app --reload

# Schemas (Pydantic)
from pydantic import BaseModel

class Order(BaseModel):
    user_id: str
    total: Decimal
    
    class Config:
        from_attributes = True

# Service
class OrderService:
    def __init__(self, repo):
        self.repo = repo
    
    async def create(self, order_dto):
        return await self.repo.create(order_dto)

# HTTP client with resilience
async def get_with_fallback(url):
    try:
        return await http_client.get(url, timeout=5)
    except Exception:
        return get_cached_result()
```

---

## When to Ask for Help

**Ask user clarifying questions if:**

- Service boundaries unclear
- Latency SLA not specified
- Consistency requirements vague
- Team structure unknown
- Technology choice unclear
- External integrations mentioned but not detailed

**Never guess. Always ask.**

---

## Success = Following These 10 Principles

1. ✅ Each service owns its data
2. ✅ Every external call has a timeout
3. ✅ Every mutation is idempotent
4. ✅ Structured JSON logging everywhere
5. ✅ Distributed tracing (OpenTelemetry)
6. ✅ Circuit breaker on external calls
7. ✅ Health checks (readiness + liveness)
8. ✅ No secrets in code
9. ✅ Tests at unit + integration level
10. ✅ Graceful shutdown (15-30s grace period)

**If any principle is violated → code is not production-ready.**

---

## Quick Reference Links

- O'Reilly Research: summarized in this quick reference: `microservices-skill/microservices-quick-reference.md`
- Full Skill Guide: `microservices-skill/microservices-skill.md`
- Implementation Guide: `microservices-skill/microservices-skill-implementation.md`
- Example Code: Look at generated TypeScript/Python above

---

**Last Updated:** April 20, 2026
