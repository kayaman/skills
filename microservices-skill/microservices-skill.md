# Microservices Agent Skill

**Version:** 1.0.0  
**Status:** Production-Ready  
**Target:** Claude Code, Cursor, coding agents  
**Languages:** TypeScript/Node.js, Python  
**Scope:** Full-stack microservices architecture + implementation  

---

## Skill Overview

This skill enables AI coding agents to **architect and implement production-grade microservices systems** in TypeScript (Node.js/NestJS) and Python (FastAPI).

**What this skill does:**
- ✅ Decomposes systems into well-bounded microservices
- ✅ Generates architectural decision records with tradeoff analysis
- ✅ Creates resilient, observable production code
- ✅ Generates tests (unit, integration, contract)
- ✅ Outputs Kubernetes + deployment configs
- ✅ Enforces 14 core patterns from O'Reilly research
- ✅ Detects and warns against anti-patterns

**Use cases:**
1. **"Help me design a microservices architecture for X"** → Gets ADR + service boundaries
2. **"Implement the payment service in TypeScript"** → Gets full NestJS app with resilience patterns
3. **"I have a monolith; help me migrate to microservices"** → Gets decomposition strategy + migration plan
4. **"Set up observability for my microservices"** → Gets OpenTelemetry + Prometheus config

---

## Invocation Pattern

### For Users

```
/microservices-skill [problem-type] [language]

Problem Types:
  - architecture    : Design service boundaries & communication
  - implementation  : Build a specific service
  - resilience      : Add failure handling patterns
  - observability   : Add logging, tracing, metrics
  - testing         : Generate test templates
  - deployment      : K8s + Docker config
  - migration       : Monolith → microservices strategy
  - security        : Auth, secrets, TLS setup

Languages:
  - typescript (default)
  - python
  - both
```

### Example Invocations

```
/microservices-skill architecture        # Design phase
/microservices-skill implementation typescript   # Build payment service
/microservices-skill observability both   # Add observability to TS + Python services
/microservices-skill testing python       # Generate pytest templates
```

---

## Skill Implementation

### Part 1: Architecture Phase

When user invokes with `architecture` or asks "how should I design...":

#### Step 1: Clarifying Questions
Ask exactly these questions (even if some seem obvious):

```
ARCHITECTURE DISCOVERY QUESTIONNAIRE
=====================================

1. DOMAIN & SCOPE
   • What is the primary business domain? (e.g., e-commerce, SaaS, analytics)
   • How many user-facing features are there?
   • What's the expected scale? (users, requests/sec, data volume)

2. LATENCY & CONSISTENCY REQUIREMENTS
   • Are there strict latency SLAs? (e.g., <500ms p99)
   • What data MUST be strongly consistent? (e.g., payments, inventory)
   • What can be eventually consistent? (e.g., recommendations, analytics)
   • Are there regulatory constraints? (e.g., GDPR, compliance)

3. TEAM STRUCTURE
   • How many teams will own services? (affects service boundaries)
   • Are teams distributed/remote? (affects deployment autonomy)
   • What's the team skill distribution? (TS vs Python vs other)

4. OPERATIONAL CONSTRAINTS
   • Will this run on Kubernetes or traditional servers?
   • What's the database strategy? (SQL, NoSQL, hybrid)
   • Do you have observability infrastructure? (ELK, Datadog, etc.)
   • What's the CI/CD maturity? (can deploy 10x/day per team?)

5. NON-FUNCTIONAL REQUIREMENTS
   • Disaster recovery RTO/RPO?
   • Security requirements? (internal only? public API?)
   • Compliance? (SOC2, GDPR, HIPAA, etc.)
```

Wait for answers. Don't proceed without them — they determine the architecture.

#### Step 2: Generate Architectural Decision Record (ADR)

Based on answers, output structured ADR:

```markdown
# ADR-001: Microservices Decomposition

## Status: Accepted

## Context
[Summary of domain + scale + constraints from Q&A]

## Decision
We will decompose the system into X services with Y communication pattern because:
- [Reasoning based on team structure]
- [Reasoning based on SLA requirements]
- [Reasoning based on consistency needs]

## Service Boundaries

| Service | Responsibility | Tech Stack | Owner | Data Store |
|---------|---|---|---|---|
| User Service | Authentication, profiles | TypeScript/NestJS | Team A | PostgreSQL |
| Order Service | Order processing | Python/FastAPI | Team B | PostgreSQL |
| Payment Service | Payment processing | TypeScript/NestJS | Team A | PostgreSQL + Redis |
| Notification Service | Email/SMS | Python/FastAPI | Team C | MongoDB |

## Communication Pattern
[Decision: sync REST + async events, with sagas for distributed transactions]

## Data Consistency Model
[Decision: strong consistency for X, eventual for Y]

## Deployment Model
[Decision: Kubernetes with Helm charts]

## Tradeoffs

### Selected Approach
✅ Benefit: Independent team deployments
✅ Benefit: Technology flexibility (TS + Python)
⚠️ Tradeoff: Complexity of distributed transactions
⚠️ Tradeoff: Need for strong observability

### Alternatives Considered
1. Monolithic Approach
   ❌ Rejected: Blocks team autonomy; single point of failure

2. Nanoservices (15+ services)
   ❌ Rejected: Overhead exceeds benefits; latency compounds

## Implementation Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Service A calls B calls C (latency) | Cache results; prefer async; SLA requirements guide service size |
| Distributed transactions fail | Implement saga pattern; idempotent operations |
| Secrets management complexity | Use Kubernetes Secrets + sealed-secrets |

## Next Steps
1. Generate service skeletons (TS: NestJS, Python: FastAPI)
2. Define API contracts (OpenAPI)
3. Design event schemas
4. Implement integration test suite
```

#### Step 3: Service Interface Specifications

For each service, generate OpenAPI/event schema:

```typescript
// Service: Payment Service (TypeScript/NestJS)

/**
 * POST /payments
 * Process a payment for an order
 */
request: {
  order_id: string;
  amount: Decimal;
  currency: string; // "USD", "EUR", etc.
  idempotency_key: string; // CRITICAL: enables safe retries
}

response: 201 Created {
  payment_id: string;
  order_id: string;
  status: "pending" | "completed" | "failed";
  created_at: ISO8601;
}

// Service publishes events
event: payment.completed {
  payment_id: string;
  order_id: string;
  amount: Decimal;
  timestamp: ISO8601;
}

event: payment.failed {
  payment_id: string;
  order_id: string;
  reason: string;
  timestamp: ISO8601;
}
```

---

### Part 2: Implementation Phase

When user invokes with `implementation [language]` or asks to "build the X service":

#### Step 1: Validate Architecture
Before implementing, verify:
- [ ] Is this service in the ADR? (if not, clarify boundaries)
- [ ] What are its dependencies? (other services it calls)
- [ ] What data does it own?
- [ ] Is there a saga pattern it participates in?

#### Step 2: Generate Service Skeleton

**For TypeScript/NestJS:**

```bash
# Directory structure
src/
├── main.ts                      # Entry point
├── app.module.ts                # Root module
├── config/
│   ├── configuration.ts         # Env vars
│   └── database.config.ts       # DB connection
├── common/
│   ├── middleware/
│   │   ├── logger.middleware.ts
│   │   └── request-id.middleware.ts
│   ├── filters/
│   │   └── exception.filter.ts
│   └── decorators/
│       └── is-idempotent.decorator.ts
├── domains/
│   ├── order/
│   │   ├── order.module.ts
│   │   ├── order.controller.ts      # HTTP endpoints
│   │   ├── order.service.ts         # Business logic
│   │   ├── order.repository.ts      # DB access
│   │   ├── dto/
│   │   │   ├── create-order.dto.ts
│   │   │   └── order.response.dto.ts
│   │   └── entities/
│   │       └── order.entity.ts
│   └── payment/
│       ├── payment.module.ts
│       ├── payment.controller.ts
│       ├── payment.service.ts
│       ├── payment.repository.ts
│       ├── dto/
│       └── entities/
├── infrastructure/
│   ├── database/
│   │   ├── typeorm.config.ts
│   │   └── migrations/
│   ├── event-bus/
│   │   ├── event-bus.module.ts
│   │   ├── event-bus.service.ts    # Publish events
│   │   └── event-handlers/
│   │       └── payment-completed.handler.ts
│   ├── http-client/
│   │   ├── http-client.module.ts
│   │   └── http-client.service.ts  # With resilience
│   └── observability/
│       ├── logger.service.ts
│       ├── tracer.service.ts
│       └── metrics.service.ts
└── test/
    ├── unit/
    │   └── order.service.spec.ts
    ├── integration/
    │   └── order.controller.integration.spec.ts
    └── fixtures/
        └── test-database.service.ts
```

**NestJS app.module.ts Template:**

```typescript
import { Module } from '@nestjs/common';
import { ConfigModule } from '@nestjs/config';
import { TypeOrmModule } from '@nestjs/typeorm';
import { TerminusModule } from '@nestjs/terminus';

import configuration from './config/configuration';
import { typeOrmConfig } from './config/database.config';
import { OrderModule } from './domains/order/order.module';
import { PaymentModule } from './domains/payment/payment.module';
import { InfrastructureModule } from './infrastructure/infrastructure.module';
import { LoggerMiddleware } from './common/middleware/logger.middleware';
import { RequestIdMiddleware } from './common/middleware/request-id.middleware';

@Module({
  imports: [
    // Configuration
    ConfigModule.forRoot({
      load: [configuration],
      isGlobal: true,
    }),

    // Database
    TypeOrmModule.forRoot(typeOrmConfig),

    // Health checks
    TerminusModule,

    // Infrastructure (observability, event bus, HTTP client)
    InfrastructureModule,

    // Domain modules
    OrderModule,
    PaymentModule,
  ],
})
export class AppModule {
  configure(consumer: MiddlewareConsumer) {
    consumer
      .apply(RequestIdMiddleware, LoggerMiddleware)
      .forRoutes('*');
  }
}
```

**For Python/FastAPI:**

```bash
# Directory structure
src/
├── main.py                      # FastAPI app + startup
├── config.py                    # Settings from env
├── database.py                  # SQLAlchemy setup
├── domains/
│   ├── order/
│   │   ├── routes.py            # FastAPI routes
│   │   ├── schemas.py           # Pydantic models
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── service.py           # Business logic
│   │   └── repository.py        # DB queries
│   └── payment/
│       ├── routes.py
│       ├── schemas.py
│       ├── models.py
│       ├── service.py
│       └── repository.py
├── infrastructure/
│   ├── event_bus.py             # Publish events
│   ├── http_client.py           # HTTP with resilience
│   ├── database.py              # DB connection
│   ├── logger.py                # Structured logging
│   └── tracer.py                # OpenTelemetry
├── middleware/
│   ├── request_id.py
│   ├── logging.py
│   └── exception_handlers.py
└── tests/
    ├── unit/
    │   └── test_order_service.py
    ├── integration/
    │   └── test_order_routes.py
    └── fixtures/
        └── test_database.py
```

**FastAPI main.py Template:**

```python
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
import structlog
from datetime import datetime

from config import settings
from infrastructure.logger import logger, setup_logging
from infrastructure.database import init_db
from infrastructure.event_bus import event_bus
from infrastructure.tracer import tracer_provider
from middleware.request_id import RequestIdMiddleware
from domains.order.routes import router as order_router
from domains.payment.routes import router as payment_router

# Setup logging at startup
setup_logging()
log = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    log.info("startup", timestamp=datetime.utcnow().isoformat())
    await init_db()
    await event_bus.connect()
    
    yield
    
    # Shutdown
    log.info("shutdown", timestamp=datetime.utcnow().isoformat())
    await event_bus.disconnect()

app = FastAPI(
    title=settings.SERVICE_NAME,
    version="1.0.0",
    lifespan=lifespan
)

# Middleware
app.add_middleware(RequestIdMiddleware)

# Routes
app.include_router(order_router, prefix="/orders", tags=["orders"])
app.include_router(payment_router, prefix="/payments", tags=["payments"])

# Health checks
@app.get("/health/ready")
async def readiness():
    """Kubernetes readiness probe: Can this service accept traffic?"""
    # Check DB, event bus, etc.
    return {"status": "ready"}

@app.get("/health/live")
async def liveness():
    """Kubernetes liveness probe: Is this service alive?"""
    return {"status": "alive"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return {}  # populated by prometheus_client

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### Step 3: Generate Core Components

**TypeScript: Order Service Example**

```typescript
// order.controller.ts
import {
  Controller,
  Post,
  Get,
  Body,
  Param,
  Inject,
  HttpCode,
  HttpStatus,
} from '@nestjs/common';
import { OrderService } from './order.service';
import { CreateOrderDto } from './dto/create-order.dto';
import { RequestId } from '../../common/decorators/request-id.decorator';

@Controller('orders')
export class OrderController {
  constructor(private readonly orderService: OrderService) {}

  @Post()
  @HttpCode(HttpStatus.CREATED)
  async create(
    @Body() createOrderDto: CreateOrderDto,
    @RequestId() requestId: string,
  ) {
    const order = await this.orderService.create(createOrderDto, requestId);
    return order;
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    return this.orderService.findById(id);
  }
}

// order.service.ts
import { Injectable, Logger } from '@nestjs/common';
import { OrderRepository } from './order.repository';
import { EventBusService } from '../../infrastructure/event-bus/event-bus.service';
import { HttpClientService } from '../../infrastructure/http-client/http-client.service';

@Injectable()
export class OrderService {
  private readonly logger = new Logger(OrderService.name);

  constructor(
    private readonly orderRepository: OrderRepository,
    private readonly eventBus: EventBusService,
    private readonly httpClient: HttpClientService,
  ) {}

  async create(createOrderDto: CreateOrderDto, requestId: string) {
    this.logger.debug('Creating order', {
      requestId,
      items: createOrderDto.items.length,
    });

    try {
      // 1. Create order in DB
      const order = await this.orderRepository.create({
        ...createOrderDto,
        status: 'pending',
        created_at: new Date(),
      });

      this.logger.info('Order created', {
        requestId,
        order_id: order.id,
      });

      // 2. Publish event (other services will react)
      await this.eventBus.publish('order.created', {
        order_id: order.id,
        user_id: order.user_id,
        total: order.total,
        items: order.items,
      });

      return order;
    } catch (error) {
      this.logger.error('Failed to create order', {
        requestId,
        error: error.message,
      });
      throw error;
    }
  }
}

// order.repository.ts (Data access)
import { Injectable } from '@nestjs/common';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Order } from './entities/order.entity';

@Injectable()
export class OrderRepository {
  constructor(
    @InjectRepository(Order)
    private readonly repository: Repository<Order>,
  ) {}

  async create(data: Partial<Order>): Promise<Order> {
    const order = this.repository.create(data);
    return this.repository.save(order);
  }

  async findById(id: string): Promise<Order> {
    return this.repository.findOneOrFail({ where: { id } });
  }

  async updateStatus(id: string, status: string): Promise<Order> {
    await this.repository.update({ id }, { status });
    return this.findById(id);
  }
}
```

**Python: Order Service Example**

```python
# routes.py
from fastapi import APIRouter, HTTPException, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import structlog

from .schemas import CreateOrderRequest, OrderResponse
from .service import OrderService
from .repository import OrderRepository
from database import get_db

log = structlog.get_logger()
router = APIRouter()

@router.post("", response_model=OrderResponse, status_code=201)
async def create_order(
    request: Request,
    order_request: CreateOrderRequest,
    db: AsyncSession = Depends(get_db),
):
    request_id = request.headers.get("X-Request-ID")
    
    log.info("create_order_start", request_id=request_id, items=len(order_request.items))
    
    try:
        repo = OrderRepository(db)
        service = OrderService(repo)
        order = await service.create(order_request, request_id)
        
        log.info("create_order_success", 
                 request_id=request_id, 
                 order_id=str(order.id))
        
        return OrderResponse.from_orm(order)
    
    except Exception as e:
        log.error("create_order_failed",
                  request_id=request_id,
                  error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create order")

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(
    order_id: str,
    db: AsyncSession = Depends(get_db),
):
    repo = OrderRepository(db)
    order = await repo.find_by_id(order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return OrderResponse.from_orm(order)

# schemas.py
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import List
from datetime import datetime

class OrderItemRequest(BaseModel):
    product_id: str
    quantity: int = Field(..., gt=0)
    price: Decimal = Field(..., gt=0)

class CreateOrderRequest(BaseModel):
    user_id: str
    items: List[OrderItemRequest]
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": "user-123",
                "items": [
                    {"product_id": "prod-1", "quantity": 2, "price": 29.99}
                ]
            }
        }

class OrderResponse(BaseModel):
    id: str
    user_id: str
    total: Decimal
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# service.py
import structlog
from decimal import Decimal
from datetime import datetime

from .repository import OrderRepository
from .models import Order
from infrastructure.event_bus import event_bus

log = structlog.get_logger()

class OrderService:
    def __init__(self, repository: OrderRepository):
        self.repo = repository
    
    async def create(self, order_request, request_id: str) -> Order:
        """Create an order and publish event"""
        
        # 1. Calculate total
        total = sum(
            item.price * item.quantity 
            for item in order_request.items
        )
        
        # 2. Create order in DB
        order = await self.repo.create({
            "user_id": order_request.user_id,
            "items": order_request.items,
            "total": total,
            "status": "pending",
            "created_at": datetime.utcnow(),
        })
        
        log.info("order_created",
                 request_id=request_id,
                 order_id=str(order.id),
                 total=float(total))
        
        # 3. Publish event (saga pattern: Payment Service will react)
        await event_bus.publish("order.created", {
            "order_id": str(order.id),
            "user_id": order.user_id,
            "total": float(total),
            "items": order_request.items,
        })
        
        return order

# repository.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .models import Order

class OrderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create(self, data: dict) -> Order:
        order = Order(**data)
        self.db.add(order)
        await self.db.commit()
        await self.db.refresh(order)
        return order
    
    async def find_by_id(self, order_id: str) -> Order | None:
        result = await self.db.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalars().first()
    
    async def update_status(self, order_id: str, status: str) -> Order:
        order = await self.find_by_id(order_id)
        order.status = status
        await self.db.commit()
        await self.db.refresh(order)
        return order
```

#### Step 4: Add Resilience Patterns

**TypeScript: HTTP Client with Circuit Breaker**

```typescript
// http-client.service.ts
import { Injectable, Logger } from '@nestjs/common';
import axios, { AxiosInstance } from 'axios';
import axiosRetry from 'axios-retry';
import CircuitBreaker from 'opossum';

@Injectable()
export class HttpClientService {
  private readonly logger = new Logger(HttpClientService.name);
  private readonly httpClient: AxiosInstance;
  private readonly breakers = new Map<string, CircuitBreaker>();

  constructor() {
    this.httpClient = axios.create({
      timeout: 5000, // 5 second timeout
    });

    // Retry configuration: exponential backoff
    axiosRetry(this.httpClient, {
      retries: 3,
      retryDelay: (retryCount) => {
        // Exponential backoff: 100ms * 2^(attempt-1) + random jitter
        const delay = 100 * Math.pow(2, retryCount - 1);
        const jitter = Math.random() * delay * 0.1;
        return delay + jitter;
      },
      retryCondition: (error) => {
        // Retry on 5xx and timeouts; NOT on 4xx (client errors)
        return (
          axiosRetry.isNetworkOrIdempotentRPCError(error) ||
          (error.response?.status >= 500)
        );
      },
    });
  }

  async get<T>(url: string, serviceName: string): Promise<T> {
    const breaker = this.getOrCreateBreaker(serviceName);

    return breaker.fire(async () => {
      try {
        const response = await this.httpClient.get<T>(url);
        return response.data;
      } catch (error) {
        this.logger.error('HTTP request failed', {
          serviceName,
          url,
          error: error.message,
        });
        throw error;
      }
    });
  }

  private getOrCreateBreaker(serviceName: string): CircuitBreaker {
    if (!this.breakers.has(serviceName)) {
      const breaker = new CircuitBreaker(
        async (fn) => fn(),
        {
          timeout: 30000, // 30 second timeout
          errorThresholdPercentage: 50, // Open if 50%+ fail
          resetTimeout: 30000, // Try again after 30s
          name: serviceName,
        }
      );

      breaker.fallback(() => {
        this.logger.warn('Circuit breaker open', { serviceName });
        throw new Error(`${serviceName} is temporarily unavailable`);
      });

      this.breakers.set(serviceName, breaker);
    }

    return this.breakers.get(serviceName)!;
  }
}
```

**Python: HTTP Client with Circuit Breaker**

```python
# infrastructure/http_client.py
import httpx
import asyncio
from datetime import datetime, timedelta
import structlog
from enum import Enum

log = structlog.get_logger()

class CircuitBreakerState(str, Enum):
    CLOSED = "closed"       # Normal operation
    OPEN = "open"          # Rejecting requests
    HALF_OPEN = "half_open"  # Testing recovery

class CircuitBreaker:
    def __init__(
        self,
        name: str,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
    ):
        self.name = name
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time: datetime | None = None
    
    async def call(self, fn, *args, **kwargs):
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                log.info("circuit_breaker_half_open", name=self.name)
            else:
                raise Exception(f"{self.name} circuit breaker is OPEN")
        
        try:
            result = await fn(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        if self.state == CircuitBreakerState.HALF_OPEN:
            self.state = CircuitBreakerState.CLOSED
            self.failure_count = 0
            log.info("circuit_breaker_closed", name=self.name)
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            log.error("circuit_breaker_open",
                     name=self.name,
                     failures=self.failure_count)
    
    def _should_attempt_reset(self) -> bool:
        if not self.last_failure_time:
            return False
        
        elapsed = (datetime.utcnow() - self.last_failure_time).total_seconds()
        return elapsed >= self.recovery_timeout

class HttpClient:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=5.0)
        self.breakers = {}
    
    def _get_breaker(self, service_name: str) -> CircuitBreaker:
        if service_name not in self.breakers:
            self.breakers[service_name] = CircuitBreaker(service_name)
        return self.breakers[service_name]
    
    async def get(self, url: str, service_name: str, **kwargs):
        breaker = self._get_breaker(service_name)
        
        async def request():
            response = await self.client.get(url, **kwargs)
            response.raise_for_status()
            return response.json()
        
        try:
            return await breaker.call(request)
        except httpx.HTTPStatusError as e:
            # Don't retry 4xx errors
            if 400 <= e.response.status_code < 500:
                raise
            # Retry 5xx with exponential backoff
            for attempt in range(3):
                await asyncio.sleep(100 * (2 ** attempt) / 1000)  # Exponential backoff
                try:
                    return await self.client.get(url, **kwargs).json()
                except Exception:
                    if attempt == 2:
                        raise

http_client = HttpClient()
```

#### Step 5: Add Observability

**TypeScript: Logger Middleware**

```typescript
// common/middleware/logger.middleware.ts
import { Injectable, NestMiddleware, Logger } from '@nestjs/common';
import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class LoggerMiddleware implements NestMiddleware {
  private readonly logger = new Logger(LoggerMiddleware.name);

  use(req: Request, res: Response, next: NextFunction) {
    const requestId = req.headers['x-request-id'] as string || uuidv4();
    req['requestId'] = requestId;

    const startTime = Date.now();

    // Log request
    this.logger.debug('incoming_request', {
      request_id: requestId,
      method: req.method,
      path: req.path,
      query: req.query,
      timestamp: new Date().toISOString(),
    });

    // Log response when finished
    res.on('finish', () => {
      const duration = Date.now() - startTime;

      this.logger.info('request_completed', {
        request_id: requestId,
        method: req.method,
        path: req.path,
        status: res.statusCode,
        duration_ms: duration,
        timestamp: new Date().toISOString(),
      });
    });

    next();
  }
}
```

**Python: Structured Logging**

```python
# infrastructure/logger.py
import structlog
import logging
from pythonjsonlogger import jsonlogger
import sys

def setup_logging():
    """Configure structured JSON logging"""
    
    # JSON formatter
    json_formatter = jsonlogger.JsonFormatter(
        fmt="%(timestamp)s %(level)s %(name)s %(message)s %(request_id)s",
        timestamp=True
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Handler
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(json_formatter)
    root_logger.addHandler(handler)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

# Usage in code
log = structlog.get_logger()

log.info(
    "order_created",
    request_id="req-123",
    order_id="order-456",
    total=99.99
)
# Output: {"timestamp": "2026-04-20T...", "message": "order_created", "request_id": "req-123", ...}
```

---

### Part 3: Testing Phase

When user invokes with `testing [language]`:

**TypeScript: Test Templates**

```typescript
// test/unit/order.service.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { OrderService } from '../../domains/order/order.service';
import { OrderRepository } from '../../domains/order/order.repository';
import { EventBusService } from '../../infrastructure/event-bus/event-bus.service';

describe('OrderService', () => {
  let service: OrderService;
  let repository: OrderRepository;
  let eventBus: EventBusService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        OrderService,
        {
          provide: OrderRepository,
          useValue: {
            create: jest.fn(),
          },
        },
        {
          provide: EventBusService,
          useValue: {
            publish: jest.fn(),
          },
        },
      ],
    }).compile();

    service = module.get<OrderService>(OrderService);
    repository = module.get<OrderRepository>(OrderRepository);
    eventBus = module.get<EventBusService>(EventBusService);
  });

  describe('create', () => {
    it('should create order and publish event', async () => {
      const createOrderDto = {
        user_id: 'user-123',
        items: [{ product_id: 'prod-1', quantity: 2, price: 29.99 }],
      };

      const mockOrder = { id: 'order-1', ...createOrderDto, status: 'pending' };
      jest.spyOn(repository, 'create').mockResolvedValue(mockOrder);
      jest.spyOn(eventBus, 'publish').mockResolvedValue(undefined);

      const result = await service.create(createOrderDto, 'req-123');

      expect(result).toEqual(mockOrder);
      expect(repository.create).toHaveBeenCalledWith(
        expect.objectContaining({
          user_id: 'user-123',
          status: 'pending',
        })
      );
      expect(eventBus.publish).toHaveBeenCalledWith(
        'order.created',
        expect.any(Object)
      );
    });

    it('should handle repository error', async () => {
      jest
        .spyOn(repository, 'create')
        .mockRejectedValue(new Error('DB error'));

      await expect(
        service.create({ user_id: 'user-123', items: [] }, 'req-123')
      ).rejects.toThrow('DB error');
    });
  });
});

// test/integration/order.controller.integration.spec.ts
import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../../app.module';
import { getRepositoryToken } from '@nestjs/typeorm';
import { Order } from '../../domains/order/entities/order.entity';
import { Repository } from 'typeorm';

describe('OrderController (Integration)', () => {
  let app: INestApplication;
  let orderRepository: Repository<Order>;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();

    orderRepository = moduleFixture.get<Repository<Order>>(
      getRepositoryToken(Order)
    );
  });

  afterEach(async () => {
    // Clean database after each test
    await orderRepository.clear();
  });

  describe('POST /orders', () => {
    it('should create order with valid data', async () => {
      const response = await request(app.getHttpServer())
        .post('/orders')
        .send({
          user_id: 'user-123',
          items: [{ product_id: 'prod-1', quantity: 2, price: 29.99 }],
        })
        .expect(201);

      expect(response.body).toHaveProperty('id');
      expect(response.body.status).toBe('pending');

      // Verify persisted in DB
      const savedOrder = await orderRepository.findOne({
        where: { id: response.body.id },
      });
      expect(savedOrder).toBeDefined();
    });

    it('should reject invalid data', async () => {
      await request(app.getHttpServer())
        .post('/orders')
        .send({
          user_id: 'user-123',
          items: [], // Empty items
        })
        .expect(400);
    });
  });

  afterAll(async () => {
    await app.close();
  });
});
```

**Python: Test Templates**

```python
# tests/unit/test_order_service.py
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal

from domains.order.service import OrderService
from domains.order.schemas import CreateOrderRequest, OrderItemRequest

@pytest.mark.asyncio
async def test_create_order():
    """Test order creation"""
    
    # Setup mocks
    mock_repo = AsyncMock()
    mock_event_bus = AsyncMock()
    
    mock_order = {
        "id": "order-123",
        "user_id": "user-123",
        "total": Decimal("59.98"),
        "status": "pending",
    }
    mock_repo.create.return_value = mock_order
    
    # Create service with mocked dependencies
    service = OrderService(mock_repo)
    service.event_bus = mock_event_bus
    
    # Execute
    request = CreateOrderRequest(
        user_id="user-123",
        items=[
            OrderItemRequest(product_id="prod-1", quantity=2, price=Decimal("29.99"))
        ]
    )
    
    result = await service.create(request, "req-123")
    
    # Verify
    assert result["id"] == "order-123"
    mock_repo.create.assert_called_once()
    mock_event_bus.publish.assert_called_once_with(
        "order.created",
        {
            "order_id": "order-123",
            "user_id": "user-123",
            "total": 59.98,
        }
    )

# tests/integration/test_order_routes.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from main import app
from database import get_db, async_session_maker

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def db_session():
    async with async_session_maker() as session:
        yield session

@pytest.mark.asyncio
async def test_create_order_integration(client: AsyncClient):
    """Test order creation via HTTP"""
    
    response = await client.post(
        "/orders",
        json={
            "user_id": "user-123",
            "items": [
                {"product_id": "prod-1", "quantity": 2, "price": 29.99}
            ]
        }
    )
    
    assert response.status_code == 201
    body = response.json()
    assert body["user_id"] == "user-123"
    assert body["status"] == "pending"
    assert body["total"] == "59.98"

@pytest.mark.asyncio
async def test_get_order_not_found(client: AsyncClient):
    """Test getting non-existent order"""
    
    response = await client.get("/orders/nonexistent")
    
    assert response.status_code == 404
```

---

### Part 4: Deployment & Operations

When user invokes with `deployment [language]`:

**Dockerfile (TypeScript/NestJS)**

```dockerfile
# Multi-stage build

# Stage 1: Build
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci

# Build
COPY . .
RUN npm run build

# Stage 2: Runtime
FROM node:20-alpine

WORKDIR /app

# Install only production dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy built app from builder
COPY --from=builder /app/dist ./dist

# Non-root user for security
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nodejs -u 1001
USER nodejs

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3000/health/live', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

EXPOSE 3000

CMD ["node", "dist/main.js"]
```

**Dockerfile (Python/FastAPI)**

```dockerfile
# Multi-stage build

# Stage 1: Build
FROM python:3.11-slim AS builder

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir uv
COPY pyproject.toml uv.lock ./
RUN uv venv /opt/venv
RUN /opt/venv/bin/uv pip install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copy venv from builder
COPY --from=builder /opt/venv /opt/venv

# Copy app code
COPY src ./src

# Non-root user
RUN useradd -m -u 1001 appuser
USER appuser

# Environment
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health/live || exit 1

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Kubernetes Deployment (both languages)**

```yaml
# k8s/order-service-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: order-service
  labels:
    app: order-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: order-service
  template:
    metadata:
      labels:
        app: order-service
    spec:
      serviceAccountName: order-service
      
      containers:
      - name: order-service
        image: myregistry.azurecr.io/order-service:1.0.0
        imagePullPolicy: IfNotPresent
        
        ports:
        - name: http
          containerPort: 3000  # or 8000 for Python
          protocol: TCP
        - name: metrics
          containerPort: 9090
          protocol: TCP
        
        env:
        - name: NODE_ENV  # or ENVIRONMENT for Python
          value: production
        - name: SERVICE_NAME
          value: order-service
        - name: LOG_LEVEL
          value: info
        - name: DB_HOST
          valueFrom:
            configMapKeyRef:
              name: order-service-config
              key: db_host
        - name: DB_PASSWORD
          valueFrom:
            secretKeyRef:
              name: order-service-secrets
              key: db_password
        
        # Readiness probe: Can this pod accept traffic?
        readinessProbe:
          httpGet:
            path: /health/ready
            port: http
          initialDelaySeconds: 10
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        
        # Liveness probe: Is this pod alive?
        livenessProbe:
          httpGet:
            path: /health/live
            port: http
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        
        # Resource limits
        resources:
          requests:
            memory: "256Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        
        # Graceful shutdown
        lifecycle:
          preStop:
            exec:
              command: ["/bin/sh", "-c", "sleep 5"]

---
apiVersion: v1
kind: Service
metadata:
  name: order-service
spec:
  type: ClusterIP
  selector:
    app: order-service
  ports:
  - name: http
    port: 80
    targetPort: http
    protocol: TCP

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: order-service-config
data:
  db_host: "postgres.default.svc.cluster.local"

---
apiVersion: v1
kind: Secret
metadata:
  name: order-service-secrets
type: Opaque
stringData:
  db_password: "set-via-sealed-secrets-in-production"
```

---

### Part 5: Validation & Anti-Pattern Detection

When generating code/architecture, ALWAYS validate:

```typescript
// Validation function the agent uses

function validateMicroservicesArchitecture(architecture: Architecture) {
  const warnings: string[] = [];
  const errors: string[] = [];

  // 1. Service Granularity Check
  if (architecture.services.length > 15) {
    warnings.push(
      "⚠️ More than 15 services detected. May be approaching nanoservice anti-pattern. " +
      "Verify each service has clear responsibility and owns data."
    );
  }

  if (architecture.services.length < 2) {
    errors.push(
      "❌ Fewer than 2 services. This is not microservices; it's a monolith. " +
      "Consider if decomposition is actually needed."
    );
  }

  // 2. Shared Database Check
  const sharedDatabases = architecture.services.filter(
    s => s.database?.shared === true
  );
  if (sharedDatabases.length > 0) {
    errors.push(
      `❌ Shared database detected in services: ${sharedDatabases.map(s => s.name).join(", ")}. ` +
      "Each service must own its schema. Use APIs or CDC for cross-service data access."
    );
  }

  // 3. Call Chain Depth Check
  architecture.services.forEach(service => {
    const depth = calculateCallDepth(service, architecture);
    if (depth > 4) {
      warnings.push(
        `⚠️ Service '${service.name}' has call chain depth ${depth}. ` +
        "This will cause latency issues. Consider caching or combining services."
      );
    }
  });

  // 4. Idempotency Check
  architecture.services.forEach(service => {
    service.endpoints?.forEach(endpoint => {
      if (
        (endpoint.method === "POST" || endpoint.method === "PUT") &&
        !endpoint.idempotent
      ) {
        warnings.push(
          `⚠️ Endpoint ${endpoint.path} (${endpoint.method}) is not marked idempotent. ` +
          "This will cause issues with retries."
        );
      }
    });
  });

  // 5. Resilience Check
  architecture.services.forEach(service => {
    service.dependencies?.forEach(dep => {
      if (!dep.hasCircuitBreaker) {
        warnings.push(
          `⚠️ ${service.name} → ${dep.name} has no circuit breaker. ` +
          "Add circuit breaker to prevent cascading failures."
        );
      }
      if (!dep.hasTimeout) {
        errors.push(
          `❌ ${service.name} → ${dep.name} has no timeout. ` +
          "ALL external calls must have timeouts."
        );
      }
    });
  });

  // 6. Observability Check
  if (!architecture.hasDistributedTracing) {
    warnings.push(
      "⚠️ No distributed tracing configured. Add OpenTelemetry for production."
    );
  }

  if (!architecture.hasStructuredLogging) {
    errors.push(
      "❌ No structured logging (JSON) configured. This is required for production."
    );
  }

  return { errors, warnings };
}
```

---

## Skill Usage Examples

### Example 1: Design Order Processing System

```
User: /microservices-skill architecture

Agent: [Asks clarifying questions about scale, SLAs, team structure]

User: [Answers questions]

Agent: [Generates ADR with 4 services: Order, Payment, Inventory, Notification]
       [Generates API specs, event schemas, saga flow for distributed transactions]
       [Generates validation: No errors, 0 warnings - ready to implement]
```

### Example 2: Implement Payment Service

```
User: /microservices-skill implementation typescript

Agent: [Assumes Payment Service from prior ADR]
       [Generates full NestJS app structure]
       [Generates PaymentController + PaymentService + PaymentRepository]
       [Adds circuit breaker for external payment gateway]
       [Adds OpenTelemetry tracing]
       [Generates Jest unit tests + integration tests]
```

### Example 3: Add Observability

```
User: /microservices-skill observability both

Agent: [Generates structured logging (pino + structlog)]
       [Generates OpenTelemetry tracer setup]
       [Generates Prometheus metrics]
       [Generates docker-compose with Jaeger + Prometheus]
```

---

## Key Principles the Skill Enforces

1. **Every service has own data** — Shared databases forbidden
2. **Every external call has timeout** — Default 5s, configurable
3. **Idempotency everywhere** — POST/PUT must be idempotent
4. **Circuit breaker mandatory** — For every cross-service call
5. **Structured logging + tracing** — JSON logs, distributed traces
6. **Tests mandatory** — Unit (mocked) + Integration (real infra)
7. **Health checks required** — Readiness + Liveness probes
8. **Graceful shutdown** — 10-30s grace period before SIGKILL
9. **No secrets in code** — All env vars; use Secrets Manager
10. **Backward compatibility** — APIs versioned; old clients still work

---

## When to Use This Skill

✅ **Use this skill when:**
- Designing a new microservices system
- Adding a new service to existing microservices architecture
- Migrating from monolith to microservices
- Setting up observability/resilience for existing services
- Reviewing microservices code for anti-patterns

❌ **Don't use this skill for:**
- Single monolithic applications (overkill)
- CLI tools or batch scripts
- Libraries or SDKs
- Simple REST APIs without service interdependencies

---

## Citing the Research

All guidance in this skill is backed by O'Reilly authority:
- Building Microservices 2nd Ed (Sam Newman)
- Microservices Patterns (Chris Richardson)
- Designing Data-Intensive Applications 2nd Ed (Martin Kleppmann)

When using generated code, include this in documentation:

```
This microservices implementation follows patterns from O'Reilly authority sources:
- Sam Newman's "Building Microservices" for service decomposition
- Chris Richardson's "Microservices Patterns" for resilience patterns
- Martin Kleppmann's "Designing Data-Intensive Applications" for data consistency
```

---

## Future Enhancements

Potential additions to this skill (v2.0):
- [ ] Event sourcing pattern implementation
- [ ] CQRS (Command-Query Responsibility Segregation)
- [ ] Service mesh configuration (Istio, Linkerd)
- [ ] Multi-language support (Go, Rust, Java)
- [ ] AI-powered code review for microservices
- [ ] Cost optimization recommendations
- [ ] Security hardening checklist
- [ ] Chaos engineering test templates

---

**Last Updated:** April 20, 2026  
**Created by:** Agent Skill Builder (O'Reilly-curated)  
**License:** CC0-1.0
