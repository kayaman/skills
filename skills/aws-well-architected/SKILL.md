---
name: well-architected
description: Enforces AWS Well-Architected Framework best practices across all six pillars (Operational Excellence, Security, Reliability, Performance Efficiency, Cost Optimization, Sustainability). Use when designing AWS architecture, writing infrastructure code (CDK, CloudFormation, Terraform), reviewing pull requests for cloud workloads, or making technology selection decisions on AWS.
---

# AWS Well-Architected Framework

Reference: https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html

## When to Apply

Apply this skill whenever:

- Proposing or reviewing AWS architecture decisions
- Writing or reviewing IaC (CDK, CloudFormation, Terraform, SAM)
- Reviewing pull requests that touch cloud infrastructure or AWS service integrations
- Selecting AWS services or making technology trade-off decisions
- Evaluating cost, performance, security, or reliability implications of a change

## General Principles

These cross-cutting principles apply to all pillars:

- Treat infrastructure as code — define all resources in version-controlled templates
- Prefer managed services over self-managed to reduce operational burden
- Design for failure — assume components will fail; build resilience into the architecture
- Automate operations — deployments, scaling, remediation, and testing
- Make frequent, small, reversible changes; avoid large, risky releases
- Collect and act on observability data (metrics, logs, traces) at every layer

---

## Pillar 1: Operational Excellence

**Focus:** Build and run workloads correctly while continuously improving processes.

### Design Principles

- Organize teams around business outcomes with aligned KPIs
- Implement observability for actionable insights across all layers
- Automate operations safely with guardrails (rate control, error thresholds, approvals)
- Make frequent, small, reversible changes
- Anticipate failure — run failure simulations and game days
- Learn from all operational events and share learnings across teams
- Refine operational procedures frequently

### Rules

- MUST define and expose operational KPIs tied to business outcomes, not just technical metrics
- MUST implement structured logging, distributed tracing, and dashboards for every workload
- MUST use automation (CI/CD pipelines, runbooks-as-code) for all deployments and operational tasks
- SHOULD document and regularly rehearse runbooks for failure scenarios
- SHOULD hold post-incident reviews and feed learnings back into procedures

---

## Pillar 2: Security

**Focus:** Protect data, systems, and assets using cloud-native security controls.

### Design Principles

- Implement a strong identity foundation: least privilege, separation of duties, no long-term static credentials
- Maintain traceability: real-time monitoring, alerting, and auditing of all actions
- Apply security at all layers: edge, VPC, load balancers, compute, OS, application, code
- Automate security: define and manage security controls as code in version-controlled templates
- Protect data in transit and at rest: classify data by sensitivity; use encryption and access controls
- Keep people away from data: minimize direct access to production data; use automation
- Prepare for security events: define incident response playbooks and run simulations

### Rules

- MUST enforce least-privilege IAM policies; MUST NOT use wildcard (`*`) permissions in production
- MUST enable encryption at rest and in transit for all data stores and communication channels
- MUST enable CloudTrail, VPC Flow Logs, and GuardDuty in every account
- MUST rotate credentials and secrets automatically (use AWS Secrets Manager or Parameter Store)
- SHOULD use AWS Organizations SCPs to enforce account-level guardrails
- SHOULD separate workload environments (dev, staging, production) into distinct AWS accounts

---

## Pillar 3: Reliability

**Focus:** Ensure a workload performs its intended function correctly and consistently.

### Design Principles

- Automatically recover from failure by monitoring KPIs and triggering automated remediation
- Test recovery procedures using automation to simulate failures before they occur in production
- Scale horizontally to eliminate single points of failure
- Stop guessing capacity — monitor demand and use auto-scaling
- Manage all infrastructure changes through automation

### Rules

- MUST design for multi-AZ deployments for all stateful services; MUST NOT rely on single-AZ for production
- MUST implement health checks and automatic replacement of unhealthy instances
- MUST define and test RTO/RPO targets; document and rehearse DR procedures
- MUST use managed queues (SQS, EventBridge) to decouple components and absorb load spikes
- SHOULD implement chaos engineering or fault injection testing (AWS Fault Injection Service)
- SHOULD use circuit breakers and retry logic with exponential backoff for all service calls

---

## Pillar 4: Performance Efficiency

**Focus:** Use computing resources efficiently to meet system requirements and adapt as demand changes.

### Design Principles

- Democratize advanced technologies — consume ML, NoSQL, transcoding as managed services
- Go global in minutes — leverage multiple AWS Regions and edge services (CloudFront, Global Accelerator)
- Use serverless architectures to eliminate server management and reduce transactional costs
- Experiment more often — compare resource types and configurations using automated benchmarks
- Apply mechanical sympathy — choose services that match access patterns and workload characteristics

### Rules

- MUST select storage and database types based on access patterns (e.g., DynamoDB for key-value, Aurora for relational, S3 for object)
- MUST configure auto-scaling for all compute resources to match demand without over-provisioning
- SHOULD use caching layers (ElastiCache, DAX, CloudFront) to reduce latency and backend load
- SHOULD benchmark and load-test before production launches and after significant architecture changes
- SHOULD place resources in Regions closest to end users; use CDN for static and cacheable content

---

## Pillar 5: Cost Optimization

**Focus:** Avoid unnecessary costs and achieve business value from every dollar spent.

### Design Principles

- Implement Cloud Financial Management: build FinOps capability, set budgets, and review spend regularly
- Adopt a consumption model: pay only for what you use; shut down idle resources
- Measure overall efficiency: track cost per unit of business output
- Stop spending on undifferentiated heavy lifting: prefer managed services over self-managed infrastructure
- Analyze and attribute expenditure: tag all resources; allocate costs to workload owners

### Rules

- MUST tag all AWS resources with at minimum `project`, `environment`, and `owner` tags
- MUST set AWS Budgets alerts for every account and workload
- SHOULD use Savings Plans or Reserved Instances for predictable, sustained compute workloads
- SHOULD use Spot Instances for fault-tolerant, batch, or stateless workloads where applicable
- SHOULD regularly review AWS Cost Explorer and Trusted Advisor recommendations
- MUST delete or stop unused resources (development environments, snapshots, orphaned volumes)

---

## Pillar 6: Sustainability

**Focus:** Minimize the environmental impact of running cloud workloads.

### Design Principles

- Understand your impact: measure resource consumption and emissions per unit of work
- Establish sustainability goals and track regression against them
- Maximize utilization: right-size workloads; eliminate idle resources
- Anticipate and adopt more efficient hardware and software offerings as they become available
- Use managed services to benefit from AWS's infrastructure efficiency at scale
- Reduce downstream impact: minimize client-side resource requirements

### Rules

- SHOULD right-size all compute resources — avoid persistent over-provisioning
- SHOULD use graviton-based (ARM) instances where workload is compatible; they deliver better performance per watt
- SHOULD implement S3 Lifecycle policies to move infrequently accessed data to cheaper, lower-energy storage tiers
- SHOULD use auto-scaling and serverless to avoid idle capacity
- SHOULD measure and report on resource efficiency (cost and compute per transaction/user)

---

## Architecture Review Checklist

Use this checklist when proposing or reviewing AWS architecture. Address any unchecked item before approving.

### Operational Excellence
- [ ] Observability is defined: metrics, structured logs, and distributed traces are collected
- [ ] Deployments are automated via CI/CD pipelines with rollback capability
- [ ] Operational runbooks exist for known failure scenarios
- [ ] KPIs tied to business outcomes are identified and monitored

### Security
- [ ] All IAM roles and policies follow least privilege; no wildcard permissions in production
- [ ] All data at rest and in transit is encrypted
- [ ] CloudTrail, GuardDuty, and VPC Flow Logs are enabled
- [ ] Secrets are managed via Secrets Manager or Parameter Store, not hardcoded
- [ ] Network access is restricted with security groups and NACLs

### Reliability
- [ ] Workload is deployed across multiple availability zones
- [ ] Health checks and auto-healing are configured
- [ ] RTO and RPO are defined; backup and DR procedures are tested
- [ ] Components are decoupled using queues or event buses
- [ ] Service quotas are known and headroom is sufficient

### Performance Efficiency
- [ ] Storage and database types are matched to access patterns
- [ ] Auto-scaling is configured for all compute resources
- [ ] Caching is applied where latency reduction is needed
- [ ] Load testing has been performed against expected peak traffic

### Cost Optimization
- [ ] All resources are tagged with `project`, `environment`, `owner`
- [ ] AWS Budgets alerts are configured
- [ ] Idle or unused resources have been removed
- [ ] Right-sizing analysis has been performed
- [ ] Savings Plans / Reserved Instances evaluated for sustained workloads

### Sustainability
- [ ] Compute resources are right-sized; no persistent idle capacity
- [ ] Graviton instances evaluated for compatible workloads
- [ ] S3 Lifecycle policies applied to data with varying access frequency
- [ ] Serverless or auto-scaling used to eliminate idle compute

---

## Trade-off Guidance

Common tensions between pillars and how to resolve them:

| Tension | Guidance |
|---|---|
| Security vs. Performance | Prefer TLS termination at the load balancer, not per-instance; use regional endpoints to avoid cross-region latency |
| Cost vs. Reliability | Use multi-AZ for stateful tiers (databases, queues); accept single-AZ for stateless compute only in non-critical environments |
| Cost vs. Performance | Use reserved capacity for baseline load and on-demand/Spot for burst; cache aggressively |
| Operational simplicity vs. Reliability | Prefer managed services even at higher unit cost; reduced operational burden outweighs marginal cost difference for most workloads |
| Sustainability vs. Performance | Right-sizing and graviton instances generally improve both; resolve conflicts by optimizing for per-transaction cost |

---

## Additional Resources

For detailed best practices per pillar, see [reference.md](reference.md).

Official whitepapers:
- [Operational Excellence](https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/welcome.html)
- [Security](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
- [Reliability](https://docs.aws.amazon.com/wellarchitected/latest/reliability-pillar/welcome.html)
- [Performance Efficiency](https://docs.aws.amazon.com/wellarchitected/latest/performance-efficiency-pillar/welcome.html)
- [Cost Optimization](https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/welcome.html)
- [Sustainability](https://docs.aws.amazon.com/wellarchitected/latest/sustainability-pillar/sustainability-pillar.html)
