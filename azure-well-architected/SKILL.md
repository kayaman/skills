---
name: azure-well-architected
description: Enforces Azure Well-Architected Framework best practices across all five pillars (Reliability, Security, Cost Optimization, Operational Excellence, Performance Efficiency). Use when designing Azure or application architecture, writing infrastructure code (Bicep, ARM, Terraform), reviewing pull requests for cloud workloads, or making technology selection decisions. Provides both Azure-specific guidance and cloud-agnostic application and solutions architecture principles.
---

# Azure Well-Architected Framework

Reference: https://learn.microsoft.com/en-us/azure/well-architected/

## When to Apply

Apply this skill whenever:

- Proposing or reviewing Azure or application architecture decisions
- Writing or reviewing IaC (Bicep, ARM templates, Terraform)
- Reviewing pull requests that touch cloud infrastructure or Azure service integrations
- Selecting Azure services or making technology trade-off decisions
- Evaluating cost, performance, security, or reliability implications of a change
- Designing solutions that require general application or solutions architecture guidance

## General Architecture Principles

These cloud-agnostic principles apply across all pillars:

- Design for business requirements — align architecture with documented goals, constraints, and success criteria; avoid guesswork
- Treat infrastructure as code — define all resources in version-controlled templates
- Prefer managed services over self-managed to reduce operational burden
- Design for failure — assume components will fail; build resilience and fault isolation
- Adopt zero-trust security — verify explicitly, least privilege, assume breach
- Automate operations — deployments, scaling, remediation, and testing
- Make frequent, small, reversible changes; avoid large, risky releases
- Collect and act on observability data (metrics, logs, traces) at every layer
- Keep it simple — avoid overengineering; add components only when they achieve target business value

---

## Pillar 1: Reliability

**Focus:** Ensure the workload meets uptime and recovery targets by building redundancy and resiliency.

### Design Principles

- Design for business requirements — define clear, achievable goals negotiated with stakeholders
- Design for resilience — expect failures; build fault-tolerant systems that degrade gracefully
- Design for recovery — have tested, documented recovery plans aligned with RTO/RPO
- Design for operations — shift left; test failures early; build observable systems
- Keep it simple — avoid overengineering; minimize critical path components

### Rules

- MUST define and document RTO/RPO targets; MUST test recovery procedures regularly
- MUST design for multi-zone or multi-region deployments for stateful services in production
- MUST implement health checks and automatic replacement of unhealthy instances
- MUST use decoupling (queues, event buses) to absorb load spikes and isolate failures
- SHOULD use circuit breakers and retry logic with exponential backoff for service calls
- SHOULD simulate failures in pre-production and production; run chaos experiments

---

## Pillar 2: Security

**Focus:** Protect the workload from attacks; maintain confidentiality, integrity, and availability (CIA triad).

### Design Principles

- Plan security readiness — adopt security practices in design and operations with minimal friction
- Protect confidentiality — access controls, data classification, encryption, guard against exfiltration
- Protect integrity — prevent tampering of data, code, and operations; verify with cryptography
- Protect availability — prevent downtime from security incidents; balance security and access
- Sustain and evolve — continuously improve; assume attackers evolve; measure and enforce posture

### Rules

- MUST enforce least-privilege access; MUST NOT use wildcard or overly broad permissions in production
- MUST enable encryption at rest and in transit for all data stores and communication channels
- MUST classify data by sensitivity and apply appropriate protection per classification level
- MUST maintain an audit trail of access and modification activities
- MUST use Azure Key Vault or equivalent for secrets; MUST NOT hardcode credentials
- SHOULD align with Microsoft Zero Trust (verify explicitly, least privilege, assume breach)
- SHOULD define and maintain an incident response plan; SHOULD conduct threat modeling

---

## Pillar 3: Cost Optimization

**Focus:** Maximize return on investment; optimize usage, rate, and allocation within budget.

### Design Principles

- Develop cost-management discipline — budgets, accountability, reporting, cost tracking
- Design with cost-efficiency mindset — spend only on what is needed; establish cost baseline
- Design for usage optimization — maximize resource utilization; right-size and scale dynamically
- Design for rate optimization — leverage commitments, reservations, consumption models
- Monitor and optimize over time — right-size as workload evolves; decommission unused resources

### Rules

- MUST tag all Azure resources with at minimum `project`, `environment`, and `owner`
- MUST set budget alerts and cost thresholds for every workload and subscription
- MUST establish a cost model and baseline; MUST track expense at workload level
- SHOULD use Reserved Instances or Savings Plans for predictable, sustained workloads
- SHOULD use Spot VMs for fault-tolerant, batch, or stateless workloads where applicable
- MUST decommission underutilized, unused, or obsolete resources; delete unnecessary data

---

## Pillar 4: Operational Excellence

**Focus:** Build and run workloads correctly; minimize process variance and human error.

### Design Principles

- Embrace DevOps culture — collaboration, shared responsibility, continuous improvement
- Establish development standards — quality gates, source control, documentation, progress tracking
- Evolve operations with observability — visibility, insight, data-driven decisions; health modeling
- Automate for efficiency — replace repetitive manual tasks with automation
- Adopt safe deployment practices — guardrails, incremental updates, rollback capability

### Rules

- MUST implement structured logging, distributed tracing, and dashboards for every workload
- MUST use automated pipelines for all deployments across all environments
- MUST define operational KPIs tied to business outcomes, not just technical metrics
- MUST use Infrastructure as Code (Bicep, ARM, Terraform) for all infrastructure
- SHOULD prefer small, incremental updates over large releases
- SHOULD use deployment patterns that allow progressive exposure (blue-green, canary, slots)
- SHOULD hold post-incident reviews and feed learnings back into procedures

---

## Pillar 5: Performance Efficiency

**Focus:** Adapt to changing demands; scale effectively and sustain performance targets.

### Design Principles

- Negotiate realistic performance targets — align with business; define benchmarks and thresholds
- Design for capacity requirements — provide enough supply for anticipated demand
- Achieve and sustain performance — protect against degradation; test and monitor continuously
- Optimize for long-term improvement — reassess targets; adopt new technologies as appropriate

### Rules

- MUST define performance targets for critical flows; MUST align with business stakeholders
- MUST configure auto-scaling for compute resources to match demand
- MUST conduct performance testing before production and after significant changes
- MUST monitor end-to-end performance; MUST set alerts on regressions
- SHOULD right-size resources across the stack; SHOULD match services to access patterns
- SHOULD use caching and CDN where latency reduction is needed

---

## Architecture Review Checklist

Use this checklist when proposing or reviewing Azure or application architecture.

### Reliability
- [ ] RTO and RPO are defined; recovery procedures are tested and documented
- [ ] Workload is deployed across multiple zones or regions for production
- [ ] Health checks and auto-healing are configured
- [ ] Components are decoupled using queues or event buses
- [ ] Failure scenarios have been simulated (chaos, game days)

### Security
- [ ] All access follows least privilege; no wildcard permissions in production
- [ ] All data at rest and in transit is encrypted
- [ ] Secrets are managed via Key Vault or equivalent, not hardcoded
- [ ] Data is classified; protection matches classification level
- [ ] Incident response plan exists; threat modeling has been performed

### Cost Optimization
- [ ] All resources are tagged with `project`, `environment`, `owner`
- [ ] Budget alerts and cost thresholds are configured
- [ ] Cost model and baseline are established
- [ ] Idle or unused resources have been removed or scheduled
- [ ] Reservations or commitments evaluated for predictable workloads

### Operational Excellence
- [ ] Observability is defined: metrics, structured logs, and distributed traces
- [ ] Deployments are automated via CI/CD with rollback capability
- [ ] Infrastructure is defined as code (Bicep, ARM, or Terraform)
- [ ] Operational runbooks exist for known failure scenarios
- [ ] KPIs tied to business outcomes are identified and monitored

### Performance Efficiency
- [ ] Performance targets are defined for critical flows
- [ ] Auto-scaling is configured for compute resources
- [ ] Storage and database types match access patterns
- [ ] Load and performance testing has been performed
- [ ] Caching is applied where latency reduction is needed

---

## Trade-off Guidance

Common tensions between pillars and how to resolve them:

| Tension | Guidance |
|---------|----------|
| Security vs. Performance | Prefer TLS termination at load balancer; use regional endpoints to minimize latency; apply security controls without blocking legitimate users |
| Cost vs. Reliability | Use multi-zone for stateful tiers; accept single-zone for stateless compute only in non-critical environments |
| Cost vs. Performance | Use reserved capacity for baseline; consumption-based for burst; cache aggressively |
| Operational simplicity vs. Reliability | Prefer managed services even at higher unit cost; reduced operational burden outweighs marginal cost difference |
| Security vs. Reliability | Security controls can introduce points of failure; design compensating controls and avoid single points of failure in security layers |

---

## Additional Resources

For detailed per-pillar guidance and Azure-specific services, see [reference.md](reference.md).

Official documentation:
- [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/)
- [Reliability](https://learn.microsoft.com/en-us/azure/well-architected/reliability/)
- [Security](https://learn.microsoft.com/en-us/azure/well-architected/security/)
- [Cost Optimization](https://learn.microsoft.com/en-us/azure/well-architected/cost-optimization/)
- [Operational Excellence](https://learn.microsoft.com/en-us/azure/well-architected/operational-excellence/)
- [Performance Efficiency](https://learn.microsoft.com/en-us/azure/well-architected/performance-efficiency/)
- [Azure Well-Architected Review (assessment)](https://learn.microsoft.com/en-us/assessments/azure-architecture-review/)
