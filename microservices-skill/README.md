# Microservices Skill

**Production-grade microservices architecture & implementation skill for coding agents.**

## Status
✅ **Complete & Ready to Use** (April 20, 2026)

## What This Skill Does

Enables AI coding agents to:
- **Architect** microservices systems (service decomposition, communication patterns)
- **Implement** services in TypeScript/Node.js (NestJS) or Python (FastAPI)
- **Add resilience** (circuit breaker, retry, timeout, idempotency)
- **Set up observability** (logging, tracing, metrics)
- **Generate tests** (unit, integration, contract, E2E)
- **Deploy to Kubernetes** (Dockerfile, manifests, CI/CD)

## Quick Start

### For Agents
1. Read: `microservices-quick-reference.md` (15 min overview)
2. Reference: `microservices-skill.md` (comprehensive guide)
3. Implement: Use `microservices-skill-implementation.md` (execution flow)

### For Users
```bash
/microservices-skill architecture      # Design services
/microservices-skill implementation typescript   # Build a service
/microservices-skill observability     # Add monitoring
/microservices-skill testing           # Generate tests
/microservices-skill deployment        # Deploy to K8s
```

## Files

| File | Size | Purpose |
|---|---|---|
| `microservices-skill.md` | 47KB | Complete skill definition with code templates |
| `microservices-skill-implementation.md` | 25KB | How agents should execute the skill |
| `microservices-quick-reference.md` | 13KB | Quick lookup guide & cheat sheet |
| `MICROSERVICES_SKILL_SUMMARY.md` | 16KB | Overview & getting started |

## Key Features

✅ **14 core patterns** — All documented with working code  
✅ **2 languages** — TypeScript/NestJS + Python/FastAPI  
✅ **Resilience built-in** — Circuit breaker, retry, timeout, idempotency  
✅ **Production-grade** — Health checks, graceful shutdown, secrets management  
✅ **Observability included** — Structured logging, distributed tracing, metrics  
✅ **Testing templates** — Unit (60%) + Integration (25%) + E2E (15%)  
✅ **Deployment ready** — Dockerfile, Kubernetes, CI/CD  
✅ **O'Reilly-backed** — All patterns verified against authoritative sources  

## Research Sources

- Building Microservices 2nd Ed (Sam Newman)
- Microservices Patterns (Chris Richardson)
- Designing Data-Intensive Applications 2nd Ed (Martin Kleppmann)
- Fundamentals of Software Architecture 2nd Ed (Richards, Ford)

## Success Metrics

In 30-50 minutes, this skill enables agents to:
- Design a complete microservices architecture (ADR + specs)
- Implement a fully working service with resilience patterns
- Generate comprehensive test suites
- Create production-ready deployment configs

## 10 Key Principles (Always Enforced)

1. Each service owns its data
2. All external calls have timeout (5-30s)
3. All mutations are idempotent
4. Structured JSON logging everywhere
5. Distributed tracing (OpenTelemetry)
6. Circuit breaker on all cross-service calls
7. Health checks (/health/ready, /health/live)
8. No secrets in code
9. Tests at unit + integration level
10. Graceful shutdown (15-30s grace period)

## Technology Stack

**TypeScript/Node.js:**
- NestJS (framework)
- TypeORM (database)
- Opossum (circuit breaker)
- Pino (logging)
- OpenTelemetry (tracing)
- Jest (testing)

**Python:**
- FastAPI (framework)
- SQLAlchemy (database)
- pybreaker (circuit breaker)
- structlog (logging)
- OpenTelemetry (tracing)
- pytest (testing)

## Limitations

- No event sourcing (Priority 3)
- No CQRS pattern (Priority 3)
- No service mesh config (can add post-impl)
- Limited to 2 languages (TypeScript/Python)
- No GraphQL support (REST + events only)

## Future Enhancements (v2.0)

- [ ] Event sourcing pattern
- [ ] CQRS implementation
- [ ] Service mesh (Istio/Linkerd)
- [ ] Additional languages
- [ ] Cost optimization recommendations
- [ ] Chaos engineering templates

## Support

**Questions?** See the appropriate file:
- Quick answers → `microservices-quick-reference.md`
- Comprehensive guide → `microservices-skill.md`
- How agents implement → `microservices-skill-implementation.md`
- Overview & getting started → `MICROSERVICES_SKILL_SUMMARY.md`

## License

CC-BY-4.0 (Anthropic)

---

**Created:** April 20, 2026  
**Research:** O'Reilly Learning Platform  
**Status:** Production Ready ✅
