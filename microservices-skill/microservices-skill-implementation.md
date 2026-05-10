# Microservices Skill — Implementation Guide for Agents

**This document describes HOW coding agents should implement microservices using the skill framework.**

---

## Agent Implementation Flow

When a user invokes the microservices skill, follow this decision tree:

### Flow 1: Architecture (Design Phase)

```
User: "Help me design microservices for X"
  ↓
Agent: [CLARIFY] Ask 5 discovery questions
  ↓
User: [ANSWERS]
  ↓
Agent: [ANALYZE] Map answers → service boundaries
  ↓
Agent: [GENERATE ADR]
  - Service inventory (table)
  - Communication matrix
  - Saga flows (if distributed transactions needed)
  - Data consistency model
  ↓
Agent: [VALIDATE] Run anti-pattern checks
  ↓
Agent: [OUTPUT ADR + API SPECS]
```

### Flow 2: Implementation (Coding Phase)

```
User: "Implement the Order Service in TypeScript"
  ↓
Agent: [CHECK] Does this service exist in prior ADR?
  ↓
Agent: [GENERATE]
  1. Directory structure (exact layout)
  2. Configuration & setup files
  3. Core domain logic (service + repository)
  4. HTTP handlers (controller)
  5. Resilience patterns (HTTP client, circuit breaker)
  6. Observability (logging middleware, tracing)
  7. Database migrations
  8. Unit & integration tests
  ↓
Agent: [VALIDATE]
  - No shared databases
  - All external calls have timeouts
  - All mutations are idempotent
  - Tests cover happy path + error cases
  ↓
Agent: [OUTPUT] Full working service
```

### Flow 3: Operations (Deploy Phase)

```
User: "Generate Kubernetes configs for this service"
  ↓
Agent: [EXTRACT] Service name, port, language from code
  ↓
Agent: [GENERATE]
  1. Dockerfile (multi-stage, secure, minimal)
  2. K8s Deployment (probes, resources, env)
  3. K8s Service (ClusterIP or NodePort)
  4. ConfigMap (non-secret config)
  5. Secret template (placeholder for secrets)
  ↓
Agent: [OUTPUT] Complete deploy-ready configs
```

---

## Detailed Implementation Steps

### Step 1: Clarification Questions (Architecture)

**When to ask:** User mentions "design", "architecture", "decompose", "how should I structure", etc.

**Ask in this order (don't skip):**

```markdown
# Architecture Discovery

I'll help you design a microservices architecture. Let me ask clarifying questions:

## 1️⃣ Domain & Scope
- **What is the primary business domain?** (e.g., e-commerce, SaaS, social media)
- **What are the main user-facing features?** (List top 5-10)
- **Expected scale in 2 years?**
  - Users: ?
  - Requests/sec: ?
  - Data volume: ? GB/TB

## 2️⃣ Latency & Consistency
- **Are there strict latency SLAs?** (e.g., API must respond in <500ms p99)
- **What data MUST be strongly consistent?** (e.g., payments, inventory counts)
- **What can be eventually consistent?** (e.g., user recommendations, stats)
- **Any regulatory/compliance constraints?** (GDPR, PCI-DSS, HIPAA, etc.)

## 3️⃣ Team Structure
- **How many teams will own services?** (1 team, 3 teams, 10+ teams?)
- **Are teams distributed/remote?**
- **Language preferences?** (TS, Python, Go, Java?)

## 4️⃣ Operations
- **Where will this run?** (Kubernetes, Docker Compose, Serverless?)
- **Database preference?** (SQL, NoSQL, hybrid?)
- **Existing observability setup?** (Datadog, ELK, CloudWatch, none?)
- **CI/CD maturity?** (Can deploy 10x/day? Once a week?)

## 5️⃣ Non-Functional
- **Disaster recovery RTO/RPO?** (e.g., 1 hour / 15 minutes)
- **API Security?** (Internal only? Public? Both?)

---

**Please answer these questions so I can design the right architecture.**
```

**Wait for all answers before proceeding.**

### Step 2: Analyze Answers & Map Service Boundaries

**Algorithm:**

1. **Identify Core Domains** from features list
   - Order Management
   - Payment Processing
   - User Management
   - Notification
   - etc.

2. **Apply Decomposition Rules:**
   - Each domain → separate service (if team will own it)
   - Services should support **independent deployment** (team autonomy)
   - Services should have **clear responsibility** (single reason to change)
   - Avoid nanoservices (combine if <100 LOC per operation)

3. **Identify Data** each service owns
   - User Service owns: users, authentication
   - Order Service owns: orders, order_items
   - Payment Service owns: payments, transaction_log
   - Notification Service owns: notifications (can be ephemeral)

4. **Map Communication Patterns**
   - User requests → Order Service (REST)
   - Order Service → Payment Service (REST + idempotent)
   - Payment Service publishes: payment.completed event
   - Notification Service subscribes to events

### Step 3: Generate ADR (Architectural Decision Record)

**Template:**

```markdown
# ADR-001: Microservices Decomposition Strategy

## Status
PROPOSED (awaiting approval) | ACCEPTED | SUPERSEDED BY #XXX

## Context
[Summarize: business domain, scale, team structure, constraints from Q&A]

### Discovered Requirements
| Requirement | Impact |
|---|---|
| 3 independent teams | Service boundaries must align with team ownership |
| <500ms p99 latency | No service should call 3+ other services in critical path |
| PCI-DSS compliance | Payment data must be isolated; Payment Service separate |
| Eventual consistency acceptable for analytics | Use event-driven for stats, not REST queries |

## Decision
Decompose into 5 services, owned by 3 teams, using REST + event-driven communication.

### Service Inventory

| Service | Owner | Responsibility | Tech | Data Store |
|---|---|---|---|---|
| User Service | Platform | Authentication, user profiles, roles | TS/NestJS | PostgreSQL |
| Order Service | Commerce | Order creation, status tracking | TS/NestJS | PostgreSQL |
| Payment Service | Finance | Payment processing, reconciliation | Python/FastAPI | PostgreSQL + Redis (cache) |
| Inventory Service | Warehouse | Stock levels, reservations | Python/FastAPI | PostgreSQL |
| Notification Service | Platform | Email, SMS, push notifications | TS/NestJS | MongoDB (logs only) |

### Communication Matrix

```
User Service
  → Order Service (REST: GET orders)
  
Order Service
  → User Service (REST: validate user)
  → Inventory Service (REST: reserve stock)
  → Payment Service (REST: charge payment)
  ↓ publishes: order.created, order.confirmed, order.failed
  
Payment Service
  ↓ publishes: payment.completed, payment.failed
  
Inventory Service
  → Payment Service (NO direct call - decoupled via events)
  
Notification Service
  ← subscribes to: order.created, payment.completed, etc.
```

### Saga Flow: Order Processing

```
User creates Order
  ↓
Order Service creates order (status: pending)
  ↓ publishes order.created
  ↓
Payment Service receives event
  → charges credit card
  → if success: publishes payment.completed
  → if fail: publishes payment.failed (Order Service will compensate)
  ↓
Order Service receives payment.completed
  → calls Inventory Service to reserve stock
  → if fail: calls Payment Service to refund (compensation)
  ↓
Order Service publishes order.confirmed
  ↓
Notification Service sends confirmation email
```

### Data Consistency Model

| Data | Consistency | Reason |
|---|---|---|
| Order + Payment | Strong (via saga) | Must not lose money; saga coordinates the workflow with compensations; use idempotency/deduplication for safe retries |
| User profiles | Strong | Immediate visibility needed |
| Inventory counts | Strong | Must not oversell |
| Analytics/stats | Eventual (15-60s) | Can be out-of-date briefly |
| Notifications | Eventual | Can arrive out-of-order; at-least-once delivery OK |

## Tradeoffs

### Chosen: REST + Events (Hybrid)
✅ REST for query operations (immediate response)
✅ Events for notifications (loose coupling)
⚠️ Complexity: need saga pattern for transactions
⚠️ Debugging: distributed transactions are harder to trace

### Rejected: Full RPC (gRPC everywhere)
❌ Would require all services to call each other synchronously
❌ Latency compounds: Order → Payment → Bank API = slow
❌ Tight coupling: cannot upgrade services independently

### Rejected: Full Event-Driven (no REST)
❌ No immediate response to queries (user must poll)
❌ Eventual consistency confuses users (order status unclear)

## Implementation Risks & Mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| Saga/distributed transaction bugs | High | Write comprehensive integration tests; implement idempotency keys |
| Call chain latency (A→B→C) | Medium | Monitor critical path; cache results; set per-service timeouts |
| Secrets/credentials leaked | High | Use Kubernetes Secrets; sealed-secrets for Git; rotate regularly |
| Cascading failure (one service down) | High | Circuit breaker on all external calls; health checks; alert on circuit open |
| Database schema changes break other services | Medium | Use DB migrations with backward compatibility; services handle old + new schema |

## Prerequisites (Before Implementation)

- [ ] All 5 teams agree to service boundaries
- [ ] Kubernetes or Docker Compose available for deployment
- [ ] Observability infrastructure (ELK/Datadog or will set up OpenTelemetry)
- [ ] CI/CD pipeline capable of deploying services independently
- [ ] Database (PostgreSQL, MongoDB) available

## Next Steps

1. **Generate API Specifications** — OpenAPI specs for all REST endpoints
2. **Design Event Schemas** — Define structure of published events
3. **Implement Service Skeletons** — Generate NestJS (TS) + FastAPI (Python) boilerplate
4. **Implement Integration Tests** — Test saga flows with real services
5. **Deploy to Dev/Staging** — Verify on Kubernetes
6. **Production Launch** — Gradual rollout with monitoring
```

### Step 4: Generate API Specifications

For each service, generate OpenAPI spec:

```yaml
# openapi/order-service.yaml
openapi: 3.0.0
info:
  title: Order Service API
  version: 1.0.0

servers:
  - url: http://order-service

paths:
  /orders:
    post:
      summary: Create a new order
      operationId: createOrder
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                user_id:
                  type: string
                items:
                  type: array
                  items:
                    $ref: '#/components/schemas/OrderItem'
              required: [user_id, items]
      responses:
        '201':
          description: Order created successfully
          headers:
            X-Idempotency-Key:
              schema:
                type: string
              description: Include in retry requests for idempotency
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Order'
        '400':
          description: Invalid request
        '500':
          description: Internal server error

    get:
      summary: List user's orders
      parameters:
        - name: user_id
          in: query
          required: true
          schema:
            type: string
      responses:
        '200':
          description: List of orders
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Order'

  /orders/{id}:
    get:
      summary: Get order by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Order details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Order'
        '404':
          description: Order not found

components:
  schemas:
    Order:
      type: object
      properties:
        id:
          type: string
        user_id:
          type: string
        items:
          type: array
          items:
            $ref: '#/components/schemas/OrderItem'
        total:
          type: number
        status:
          type: string
          enum: [pending, confirmed, shipped, delivered, cancelled]
        created_at:
          type: string
          format: date-time

    OrderItem:
      type: object
      properties:
        product_id:
          type: string
        quantity:
          type: integer
          minimum: 1
        price:
          type: number
          minimum: 0
      required: [product_id, quantity, price]
```

### Step 5: Design Event Schemas

```yaml
# events/order-events.yaml
events:
  order.created:
    description: Published when a new order is created
    schema:
      type: object
      properties:
        order_id:
          type: string
        user_id:
          type: string
        total:
          type: number
        items:
          type: array
        timestamp:
          type: string
          format: date-time
      required: [order_id, user_id, total, timestamp]

  order.payment_requested:
    description: Published when Order Service requests payment
    schema:
      type: object
      properties:
        order_id:
          type: string
        payment_id:
          type: string
        amount:
          type: number
        idempotency_key:
          type: string
      required: [order_id, payment_id, amount, idempotency_key]

  payment.completed:
    description: Published when payment succeeds
    schema:
      type: object
      properties:
        payment_id:
          type: string
        order_id:
          type: string
        amount:
          type: number
        timestamp:
          type: string
          format: date-time
      required: [payment_id, order_id, amount, timestamp]

  payment.failed:
    description: Published when payment fails
    schema:
      type: object
      properties:
        payment_id:
          type: string
        order_id:
          type: string
        reason:
          type: string  # "insufficient_funds", "card_declined", etc.
        timestamp:
          type: string
          format: date-time
      required: [payment_id, order_id, reason, timestamp]
```

### Step 6: Generate Service Skeleton

When user asks to implement a service:

**Agent asks 3 quick questions (if not clear from prior context):**

```
1. Language preference? (TypeScript/NestJS or Python/FastAPI)
2. Does this service have external dependencies? (payment gateway, email service, etc.)
3. Any specific database? (PostgreSQL, MongoDB, etc.)
```

**Then generate:**

1. **Directory structure** (copy-paste into project)
2. **package.json** or **pyproject.toml** with dependencies
3. **Configuration** (config.ts / config.py)
4. **Main entry point** (main.ts / main.py)
5. **Domain modules** (service + repository + controller)
6. **Resilience** (HTTP client with circuit breaker)
7. **Observability** (logging, tracing)
8. **Tests** (unit + integration)

### Step 7: Generate Tests

**For TypeScript:**
- Jest configuration
- Unit test template (mocked dependencies)
- Integration test template (real database)
- Fixture setup (database seeding)

**For Python:**
- pytest configuration  
- Unit test template (mocked dependencies)
- Integration test template (real database)
- Fixture setup (database seeding)

**Test coverage guidelines:**
- Unit tests: 70%+ (business logic)
- Integration tests: 20%+ (API + database)
- E2E tests: 10%+ (critical flows)

### Step 8: Generate Deployment Configs

When user asks to deploy:

**Generate:**

1. **Dockerfile** (multi-stage, non-root user)
2. **docker-compose.yml** (for local dev)
3. **k8s/deployment.yaml** (Kubernetes)
4. **k8s/service.yaml** (expose service)
5. **k8s/configmap.yaml** (non-secret config)
6. **k8s/secret.yaml** (template for secrets)
7. **.github/workflows/deploy.yml** (CI/CD)

### Step 9: Validation & Anti-Pattern Detection

Before outputting code, run this checklist:

```
✅ Checklist before generating service code:

Data & Boundaries
[ ] Service has sole ownership of its data (no shared tables)
[ ] All data access outside service goes through API/events
[ ] No hardcoded service URLs (use service discovery)

Resilience
[ ] All external HTTP calls have timeout (5-30s)
[ ] All external HTTP calls have retry logic (3 attempts, exponential backoff)
[ ] All external calls have circuit breaker
[ ] All mutations are idempotent (idempotency key in request)

Observability
[ ] Structured JSON logging everywhere
[ ] OpenTelemetry tracing on entry points
[ ] Prometheus metrics on HTTP endpoints
[ ] Health checks (/health/ready, /health/live)

Security
[ ] No secrets in code
[ ] Credentials from environment variables
[ ] CORS configured (if API is public)
[ ] Input validation with schemas

Testing
[ ] Unit tests for business logic (60%)
[ ] Integration tests with real services (25%)
[ ] Tests for error paths (happy path + failure)
[ ] Database migration tests

Deployment
[ ] Dockerfile with multi-stage build
[ ] Non-root user in container
[ ] Health checks in K8s manifests
[ ] Resource limits set
[ ] Graceful shutdown (preStop hook)

If any ❌ items exist: STOP, explain issue, ask user how to proceed.
If all ✅: Generate code.
```

---

## Prompt Templates for Agents

### Template 1: Architecture Design

```
User asked: "Design microservices for [domain]"

Step 1: Send Discovery Questions
[Ask 5 questions - wait for answers]

Step 2: Analyze Answers
- Extract: scale, team count, latency requirements, consistency needs
- Map to services: [list]
- Identify saga patterns: [list]

Step 3: Generate ADR
- Service inventory table
- Communication matrix
- Saga flows
- Tradeoff analysis

Step 4: Validate
- Run anti-pattern checks
- If errors: STOP, explain
- If warnings: mention but continue

Step 5: Output
- Full ADR (markdown)
- OpenAPI specs for each service
- Event schemas
```

### Template 2: Service Implementation

```
User asked: "Implement [service name] in [language]"

Step 1: Verify Context
- Is this service in the ADR? If not: ask clarification
- What dependencies does it have?
- Is it part of a saga? (if yes, note idempotency requirements)

Step 2: Validate Readiness
- Language clear? (TypeScript or Python)
- Database decided? (PostgreSQL, MongoDB, etc.)
- Any external integrations? (payment API, email service, etc.)

Step 3: Generate Skeleton
- Directory structure (exact paths)
- Configuration file
- Main entry point

Step 4: Generate Core
- Domain service (business logic)
- Repository (database access)
- Controller/Routes (HTTP handlers)

Step 5: Add Resilience
- HTTP client with circuit breaker
- Retry logic with exponential backoff
- Timeout configuration

Step 6: Add Observability
- Logger middleware
- Tracer setup
- Metrics export

Step 7: Generate Tests
- Unit test skeleton (mocked)
- Integration test skeleton (real DB)
- Fixture setup

Step 8: Validate
- Check all external calls have timeouts
- Check all mutations are idempotent
- Check no hardcoded secrets

Step 9: Output
- Full working service (all files)
- README with setup instructions
- Test run command
```

### Template 3: Deployment

```
User asked: "Generate deployment configs for [service]"

Step 1: Extract Metadata
- Service name: [from code]
- Language: [TS/Python from code]
- Port: [from main.ts/main.py]
- Environment variables: [from config]

Step 2: Generate Dockerfile
- Multi-stage build (builder + runtime)
- Non-root user
- Health check
- Minimal base image

Step 3: Generate K8s Manifests
- Deployment (replicas, probes, resources, env)
- Service (ClusterIP)
- ConfigMap (non-secrets)
- Secret template (secrets stub)

Step 4: Generate CI/CD
- GitHub Actions workflow
- Build job (docker build + push)
- Deploy job (kubectl apply)
- Health check job (verify deployment)

Step 5: Output
- Dockerfile
- k8s/ directory with all manifests
- .github/workflows/ with deploy.yml
- Deployment guide (text)
```

---

## Common Patterns the Skill Implements

### Pattern 1: Saga for Distributed Transactions

**Use when:** Multiple services need to coordinate changes

**Implementation:**
```
Order Service (orchestrator)
  → 1. Create order (PENDING)
  → 2. Call Payment Service (idempotent)
       ↓ If fails: compensate (delete order)
  → 3. Call Inventory Service (idempotent)
       ↓ If fails: refund + compensate
  → 4. Update order status to CONFIRMED
```

**Agent guidance:**
- Idempotency keys are CRITICAL
- Each step must have a compensating transaction
- Each step must be independently testable

### Pattern 2: Event-Driven Notifications

**Use when:** Multiple services need to react to a single event

**Implementation:**
```
Order Service publishes: order.created
  ↓
Multiple subscribers:
  - Notification Service (sends email)
  - Analytics Service (logs event)
  - Recommendation Service (updates user profile)
  
All subscribers are independent:
  - If one fails, others still process
  - They can be added/removed without Order Service changing
```

**Agent guidance:**
- Events are immutable facts (past tense: "order.created", not "create_order")
- Publishers don't know subscribers
- Use topic/subscription or message queue

### Pattern 3: Circuit Breaker

**Use when:** Calling an external service that might fail

**Implementation:**
```
Service A calls Service B:
  - Normal: request succeeds, circuit stays CLOSED
  - Failures: 5 consecutive failures → circuit OPEN
  - Open: reject all requests immediately
  - Half-Open: test with single request after timeout
  - Success in Half-Open: circuit CLOSED
```

**Agent guidance:**
- Configure threshold per dependency (some services more stable than others)
- Return fallback response when OPEN (cached data, error message)
- Monitor circuit breaker state (alert when OPEN)

---

## Anti-Patterns to Detect & Prevent

### ❌ Anti-Pattern 1: Nanoservices

**What it is:** Too many small services (>15)

**Detection:** 
```
if (services.length > 15) {
  warn("Too many services. Each service handles <100 LOC per operation?")
}
```

**Fix:**
- Combine services with related responsibilities
- Ensure each service handles 500+ LOC

### ❌ Anti-Pattern 2: Shared Database

**What it is:** Multiple services write to same table

**Detection:**
```
if (service.database?.tables?.owned_by?.length > 1) {
  error("Multiple services own this table. This breaks service autonomy.")
}
```

**Fix:**
- One service writes; others read via API or replicated cache

### ❌ Anti-Pattern 3: No Timeouts

**What it is:** HTTP calls wait indefinitely

**Detection:**
```
if (httpCall.timeout === undefined) {
  error("All external calls MUST have timeout. Default 5s.")
}
```

**Fix:**
- Add timeout: 5-30s depending on SLA

### ❌ Anti-Pattern 4: Non-Idempotent Mutations

**What it is:** POST/PUT can't be safely retried

**Detection:**
```
if (route.method in [POST, PUT] && !route.idempotent) {
  warn("This mutation should be idempotent for safe retries.")
}
```

**Fix:**
- Use idempotency keys: client sends request ID, server deduplicates

### ❌ Anti-Pattern 5: Deeply Nested Service Calls

**What it is:** A → B → C → D (4+ hops)

**Detection:**
```
if (callDepth(service) > 4) {
  warn("Call chain depth is ${depth}. Latency will suffer.")
}
```

**Fix:**
- Cache results from B in A
- Combine related services
- Prefer async/events for non-critical operations

---

## When to Stop & Ask for Clarification

**Agent should STOP and ASK USER if:**

1. Service boundaries unclear
   - "I see 10 possible services, but I'm unsure which team owns which. Can you clarify team structure?"

2. Consistency requirements unclear
   - "Do orders need strong consistency with inventory? Or is <5min delay acceptable?"

3. Latency SLA unclear
   - "What's your p99 latency target? This affects service decomposition."

4. Technology unclear
   - "Should this be TypeScript or Python? This affects library choices."

5. External integration unclear
   - "Does Payment Service integrate with Stripe or internal payment processor?"

**Agent should NOT guess or assume.**

---

## Success Criteria

**User is satisfied when:**

✅ ADR is detailed, with clear service boundaries  
✅ Generated code compiles & runs immediately (no missing deps)  
✅ Tests pass without modification  
✅ Code follows all 10 key principles  
✅ Deployment configs are production-ready  
✅ Documentation is clear for other developers  

**Agent failed if:**

❌ Generated code has imports that don't exist  
❌ Tests fail  
❌ Security vulnerability present (hardcoded secrets)  
❌ Violates key principles (no timeout, shared database, etc.)  
❌ ADR is vague ("needs more services")  

---

**End of Implementation Guide**

Use this guide to implement any microservices request. Follow the decision tree; don't skip steps; validate at each stage.
