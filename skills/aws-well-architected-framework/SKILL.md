---
name: aws-well-architected-framework
description: Provides comprehensive AWS Well-Architected Framework knowledge covering all six pillars, design principles, review process, and the Well-Architected Tool. Use when learning or teaching the framework, preparing for Well-Architected Reviews, understanding pillar trade-offs, selecting appropriate AWS lenses, or evaluating workload architecture against the latest 2024-2025 best practices. Not to be confused with the aws-well-architected enforcement skill.
---

# AWS Well-Architected Framework

Reference: [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html) (updated Nov 2024)

## When to Apply

- Preparing for or conducting a Well-Architected Review
- Designing new AWS workloads or evaluating existing ones
- Making trade-off decisions between pillars (e.g., cost vs reliability)
- Selecting a Well-Architected Lens for a specialized workload
- Teaching or learning the framework's principles and review methodology
- Aligning architecture decisions with organizational goals

This skill provides **knowledge and guidance**. For enforcement rules during code reviews and IaC development, see the `aws-well-architected` skill.

---

## General Design Principles

These cross-cutting principles apply to all six pillars:

1. **Stop guessing capacity needs** — use auto-scaling and monitoring to match supply to demand
2. **Test systems at production scale** — create production-scale test environments on demand; decommission after testing
3. **Automate with experimentation in mind** — create and replicate workloads at low cost; track changes via automation
4. **Allow for evolutionary architectures** — design for change; reduce the cost of experimentation
5. **Drive architectures using data** — collect data on how your architecture choices affect workload behavior
6. **Improve through game days** — simulate events in production to understand behavior and test responses

---

## The Six Pillars

### Pillar 1: Operational Excellence

**Focus:** Build and run workloads effectively while continuously improving processes.

**8 Design Principles (expanded June 2024):**

1. Organize teams around business outcomes
2. Implement observability for actionable insights
3. Safely automate where possible (with guardrails)
4. Make frequent, small, reversible changes
5. Refine operations procedures frequently
6. Anticipate failure — run simulations and game days
7. Learn from all operational events
8. Use managed services to reduce operational burden

**Key Areas:** Organization → Prepare → Operate → Evolve

**Key Services:** CloudWatch, Systems Manager, Config, EventBridge, Fault Injection Service, CloudFormation

---

### Pillar 2: Security

**Focus:** Protect data, systems, and assets using cloud-native controls.

**7 Design Principles:**

1. Implement a strong identity foundation (least privilege, no long-term credentials)
2. Maintain traceability (real-time monitoring, auditing)
3. Apply security at all layers (defense in depth)
4. Automate security best practices (security as code)
5. Protect data in transit and at rest
6. Keep people away from data (minimize direct access)
7. Prepare for security events (incident response playbooks)

**Key Areas:** Identity & Access → Detection → Infrastructure Protection → Data Protection → Incident Response

**Key Services:** IAM, GuardDuty, Security Hub, CloudTrail, KMS, WAF, Shield, Secrets Manager, Macie

---

### Pillar 3: Reliability

**Focus:** Ensure workloads perform their intended function correctly and consistently.

**5 Design Principles:**

1. Automatically recover from failure
2. Test recovery procedures
3. Scale horizontally to increase aggregate availability
4. Stop guessing capacity
5. Manage change through automation

**Key Areas:** Foundations → Workload Architecture → Change Management → Failure Management

**Key Services:** Route 53, ELB, Auto Scaling, SQS, Resilience Hub, Elastic Disaster Recovery, Fault Injection Service

**Critical Rules:**
- MUST design for multi-AZ deployments for all production stateful services
- MUST define and test RTO/RPO targets
- MUST implement health checks and automatic replacement of unhealthy instances
- SHOULD implement circuit breakers and retry with exponential backoff

---

### Pillar 4: Performance Efficiency

**Focus:** Use computing resources efficiently as demand and technologies evolve.

**5 Design Principles:**

1. Democratize advanced technologies (consume as managed services)
2. Go global in minutes (multi-Region, edge)
3. Use serverless architectures
4. Experiment more often
5. Apply mechanical sympathy (match technology to access patterns)

**Key Areas:** Selection (Compute, Storage, Database, Networking) → Review → Monitoring → Trade-offs

**Key Services:** EC2 Graviton, Lambda, ECS/EKS, ElastiCache, DAX, CloudFront, DynamoDB, Aurora, Global Accelerator

---

### Pillar 5: Cost Optimization

**Focus:** Achieve business value at the lowest price point.

**5 Design Principles:**

1. Implement Cloud Financial Management (FinOps)
2. Adopt a consumption model (pay only for what you use)
3. Measure overall efficiency (cost per business unit)
4. Stop spending on undifferentiated heavy lifting
5. Analyze and attribute expenditure (tagging, cost allocation)

**Key Areas:** Cloud Financial Management → Expenditure Awareness → Cost-Effective Resources → Demand/Supply Management → Optimization Over Time

**Key Services:** Cost Explorer, Budgets, Cost Optimization Hub, Compute Optimizer, Savings Plans, Spot Instances, Trusted Advisor

---

### Pillar 6: Sustainability (added 2021)

**Focus:** Minimize environmental impact of cloud workloads.

**6 Design Principles:**

1. Understand your impact
2. Establish sustainability goals
3. Maximize utilization
4. Anticipate and adopt more efficient offerings
5. Use managed services
6. Reduce downstream impact

**Key Areas:** Region Selection → User Behavior → Software/Architecture Patterns → Data Patterns → Hardware Patterns → Development/Deployment Patterns

**Key Strategies:** Right-size compute, use Graviton (ARM) instances, S3 Lifecycle policies, serverless for variable workloads, eliminate idle resources

---

## Well-Architected Reviews

A Well-Architected Review is a **constructive conversation about architectural decisions**, not an audit mechanism.

### Three Phases

| Phase | Activities | Output |
|-------|-----------|--------|
| **Prepare** | Identify workload, sponsors, and stakeholders; select pillars and lenses | Review scope and participants |
| **Review** | Walk through per-pillar questions in the WA Tool; identify High/Medium Risk Issues (HRIs/MRIs) | Documented risks and findings |
| **Improve** | Create improvement plan; prioritize by business impact; implement and track via milestones | Measurable risk reduction |

### The Well-Architected Tool

- Free in the AWS Console — guides teams through pillar questions
- Tracks improvement plans and milestones over time
- Supports custom lenses for domain-specific evaluation
- Integrates with AWS Trusted Advisor for automated checks

---

## Lenses

Lenses extend the framework for specific workload types or industries:

| Lens Category | Examples |
|--------------|---------|
| **Technology** | Serverless, SaaS, IoT, Container Build, Data Analytics |
| **AI/ML** | Machine Learning, Generative AI, Responsible AI |
| **Industry** | Financial Services, Healthcare, Games |
| **Custom** | Organization-specific lenses via JSON templates |

- SHOULD select the most relevant lens(es) for the workload type
- MAY create custom lenses to encode organization-specific architectural standards

---

## Pillar Trade-off Guidance

| Tension | Guidance |
|---------|---------|
| **Security vs Performance** | TLS termination at the load balancer, not per-instance; use regional endpoints for latency |
| **Cost vs Reliability** | Multi-AZ for stateful tiers; accept single-AZ for stateless compute in non-critical environments only |
| **Cost vs Performance** | Reserved capacity for baseline; on-demand/Spot for burst; cache aggressively |
| **Operational Simplicity vs Reliability** | Prefer managed services even at higher unit cost — reduced operational burden outweighs marginal cost |
| **Sustainability vs Performance** | Right-sizing and Graviton generally improve both; optimize per-transaction cost |
| **Security vs Operational Simplicity** | Automate security controls; manual security processes cause drift and become a bottleneck |

---

## Checklist

When conducting or preparing for a Well-Architected Review:

- [ ] Workload scope is clearly defined (not the entire organization)
- [ ] Relevant pillars and lenses have been selected
- [ ] Stakeholders from operations, security, development, and finance are involved
- [ ] Each pillar's design principles have been reviewed against the architecture
- [ ] High Risk Issues are identified, prioritized, and assigned to owners
- [ ] An improvement plan with milestones exists in the WA Tool
- [ ] Trade-offs between pillars are documented and accepted consciously
- [ ] The review is treated as a periodic practice, not a one-time event

## Key References

| Book / Resource | Author(s) | Publisher | Year |
|------|-----------|-----------|------|
| *AWS Well-Architected Framework* (official) | AWS | AWS Docs | 2024 |
| *Designing Data-Intensive Applications* | Martin Kleppmann | O'Reilly | 2017 |
| *Software Engineering at Google* | Winters, Manshreck, Wright | O'Reilly | 2020 |
| *Fundamentals of Software Architecture* | Richards, Ford | O'Reilly | 2020 |
| *AWS for Solutions Architects* (2nd ed.) | Shrivastava et al. | Packt | 2023 |
| *Cloud Native Patterns* | Cornelia Davis | Manning | 2019 |
