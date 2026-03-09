# Azure Well-Architected Framework — Detailed Reference

Extended best practices per pillar. Read this file when you need deeper guidance beyond what is in SKILL.md.

---

## Pillar 1: Reliability

### Foundations

- Set and monitor Azure service quotas; request quota increases proactively before reaching limits
- Use Azure Management Groups and subscriptions to enforce guardrails and organize workloads
- Design network topology for fault isolation: separate virtual networks per environment; use Azure Virtual WAN or hub-spoke for connectivity
- Factor in organizational constraints (centralized infrastructure, security mandates) that affect autonomy

### Workload Architecture

- Use stateless compute (Azure App Service, Container Apps, AKS); store state in managed data stores (Azure SQL, Cosmos DB, Redis Cache)
- Implement the bulkhead pattern: isolate failures in one subsystem from propagating to others
- Use Azure Service Bus or Event Grid with dead-letter queues to capture and reprocess failed messages
- Apply the saga pattern for distributed transactions across microservices
- Use idempotent operations so retries do not cause duplicate side effects
- Distinguish critical-path components from those that can operate in degraded state

### Change Management

- Deploy infrastructure changes through CI/CD pipelines; no manual changes in production
- Use Bicep or ARM templates (or Terraform) for multi-region deployments
- Implement deployment slots for App Service; use blue-green or canary patterns for containers
- Test backward compatibility of API changes before deploying; use contract tests

### Failure Management

- Use Azure Front Door or Traffic Manager for global load balancing and failover
- Deploy across Availability Zones for zonal redundancy; use multiple regions for critical workloads
- Test failover procedures: run DR drills at least quarterly
- Use Azure Site Recovery for orchestrated disaster recovery; Azure Backup for centralized backup
- Implement automated self-healing; use immutable, ephemeral stateless components

---

## Pillar 2: Security

### Identity and Access Management

- Use Microsoft Entra ID (Azure AD) for human access; avoid long-term static credentials
- Use Managed Identity for workloads (App Service, AKS, VMs) to access Azure resources
- Enforce MFA for all human access to Azure Portal and CLI
- Use RBAC with least privilege; apply Azure Policy to enforce permissions
- Review and remove unused identities and role assignments regularly

### Detection and Monitoring

- Enable Microsoft Defender for Cloud for continuous security assessment and recommendations
- Use Azure Monitor for security-relevant metrics and Log Analytics for centralized logs
- Integrate with Microsoft Sentinel for SIEM and SOAR capabilities
- Enable diagnostic settings and export logs to a centralized, immutable storage account

### Infrastructure Protection

- Use Azure Virtual Network with private subnets; place only Application Gateway or Front Door in public-facing layers
- Apply NSGs (Network Security Groups) at subnet and NIC level; use Azure Firewall for central egress control
- Use Azure DDoS Protection Standard for public endpoints
- Use Azure Private Link to access Azure PaaS services without traversing the public internet

### Data Protection

- Classify all data: public, internal, confidential, restricted
- Enable encryption at rest (Azure Storage, SQL, Cosmos DB); use Azure Key Vault for keys
- Enforce TLS 1.2+ for all API and service-to-service communication
- Use Azure Key Vault for certificates and secrets; never embed keys in code or config

### Incident Response

- Define an incident response plan with severity levels, escalation paths, and communication templates
- Align with organizational SOC; use Defender for Cloud and Sentinel for detection and response
- Pre-provision forensic access and isolated environments for investigation
- Conduct threat modeling; run periodic penetration tests and vulnerability scans

---

## Pillar 3: Cost Optimization

### Cloud Financial Management

- Assign a FinOps owner or team responsible for cost visibility and optimization
- Use Azure Cost Management and Billing for analysis, budgets, and alerts
- Establish monthly cost reviews; set budget alerts at 80% and 100% of budget
- Use Azure Cost Management views and exports for per-workload, per-team reporting

### Expenditure Awareness

- Apply Azure Policy to enforce tagging; block resource creation without required tags
- Use cost allocation and tags to produce per-workload, per-environment reports
- Review top cost drivers regularly; use Cost Analysis to identify unexpected spikes

### Cost-Effective Resources

- Use Azure Spot VMs for fault-tolerant, batch, or stateless workloads (batch jobs, CI runners)
- Purchase Reserved Instances or Savings Plans for 1- or 3-year commitments on predictable compute
- Use Azure Hybrid Benefit where you have existing licenses (Windows, SQL Server)
- Right-size VMs with Azure Advisor and Azure Monitor recommendations
- Delete unattached disks, orphaned public IPs, and unused resources; apply lifecycle management to storage

### Demand and Supply Management

- Use auto-scaling (Virtual Machine Scale Sets, App Service, AKS) to right-size compute
- Treat non-production environments differently; use smaller SKUs, fewer replicas, reduced logging
- Schedule non-production environments to stop outside business hours with Azure Automation or Logic Apps
- Prefer consumption-based (serverless) where usage is variable: Functions, Container Apps, Logic Apps

---

## Pillar 4: Operational Excellence

### Organization

- Align team structures to business outcomes; avoid siloed ops vs. dev ownership
- Define an operating model: who owns on-call, runbooks, and SLO accountability
- Use tags and Management Groups to track workload ownership across subscriptions
- Establish shared responsibility between platform teams and product teams

### Preparation

- Define workload health as code: embed Azure Monitor alerts and dashboards in IaC
- Implement deployment safety: deployment slots, blue-green, automatic rollback on failure
- Use Azure Automation for patch management and runbook automation
- Practice game days and chaos experiments before production incidents occur

### Operation

- Use structured log formats (JSON) for Application Insights and Log Analytics
- Instrument applications with Application Insights (APM, distributed tracing, dependencies)
- Set SLOs for availability and latency; alert before SLO is breached (error budget)
- Use Azure Monitor Alerts and Action Groups for automated remediation triggers

### Evolution

- Review and update runbooks after every incident
- Track tech debt explicitly; allocate capacity in each sprint to reduce operational toil
- Use Azure Advisor recommendations on a regular cadence

### IaC and Pipelines

- Use Bicep or ARM templates for Azure-native IaC; Terraform for multi-cloud or preference
- Store IaC in version control; use Azure DevOps or GitHub Actions for CI/CD
- Promote immutable artifacts through environments; use the same artifact in dev, staging, prod

---

## Pillar 5: Performance Efficiency

### Selection

| Resource Type | Guidance |
| ------------- | -------- |
| Compute | Match VM series to workload: B-series for burstable, D-series for general, E-series for memory, F-series for compute; use Container Apps or AKS for containerized workloads |
| Storage | Azure Blob for object; Managed Disks (Premium SSD, Standard SSD) for VMs; Azure Files for shared file systems |
| Database | Azure SQL for relational; Cosmos DB for global, multi-model; Azure Cache for Redis for low-latency caching; Synapse for analytics |
| Network | Place resources in the same region to minimize latency; use Azure CDN for static and cacheable content; Azure Front Door for global routing and acceleration |

### Review

- Use Azure Advisor and Azure Monitor recommendations to identify underutilized and mis-sized resources
- Benchmark new VM sizes or storage options in staging before production migration
- Profile application performance with Application Insights to identify bottlenecks

### Monitoring

- Define performance SLOs (p50, p95, p99 latency; throughput; error rate) for every public API
- Use Application Insights for APM, container insights for AKS, VM insights for VMs
- Alert on sustained high CPU/memory utilization as a signal of under-sizing

### Trade-offs

- Latency vs. cost: caching reduces latency and backend load but adds complexity and stale data risk; apply TTLs deliberately
- Throughput vs. simplicity: batching reduces API overhead but increases response latency
- Provisioned vs. consumption: provisioned capacity (e.g., Cosmos DB RU/s) is cheaper at sustained load; consumption suits variable workloads

---

## Sustainability Considerations

Sustainability is embedded across Azure WAF pillars rather than a separate pillar. Apply these where relevant:

- Right-size compute; avoid persistent over-provisioning
- Use ARM-based VMs (e.g., Ampere) where compatible for better efficiency
- Apply storage lifecycle policies to move infrequently accessed data to cooler tiers
- Use auto-scaling and serverless to avoid idle capacity
- Prefer Azure-managed services to benefit from Microsoft's infrastructure efficiency
