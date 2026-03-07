# AWS Well-Architected Framework — Detailed Reference

Extended best practices per pillar. Read this file when you need deeper guidance beyond what is in SKILL.md.

---

## Pillar 1: Operational Excellence

### Organization

- Align team structures to business outcomes; avoid siloed ops vs. dev ownership
- Define an operating model: who owns on-call, runbooks, and SLO accountability
- Use tags and AWS Organizations to track workload ownership across accounts
- Establish shared responsibility boundaries between platform teams and product teams

### Preparation

- Define workload health as code: embed CloudWatch alarms and dashboards in IaC templates
- Implement deployment safety: canary/blue-green deployments, automatic rollback on alarm
- Use AWS Systems Manager for patch management, parameter storage, and remote operations
- Practice game days and chaos experiments before production incidents occur

### Operation

- Use structured log formats (JSON) so logs are queryable in CloudWatch Logs Insights, OpenSearch, or third-party SIEM
- Instrument every Lambda function, ECS task, and EC2 service with AWS X-Ray for distributed tracing
- Set SLOs (Service Level Objectives) for availability and latency; alert before SLO is breached (error budget)
- Use EventBridge to trigger automated remediation in response to operational events

### Evolution

- Review and update runbooks after every incident
- Track tech debt explicitly; allocate capacity in each sprint to reduce operational toil
- Use AWS Trusted Advisor and AWS Compute Optimizer recommendations on a regular cadence

---

## Pillar 2: Security

### Identity and Access Management

- Use IAM Identity Center (SSO) for human access; avoid long-term IAM user credentials
- Assign IAM roles to compute resources (EC2 instance profiles, Lambda execution roles, ECS task roles)
- Enforce MFA for all human access to the AWS Console and CLI
- Use permission boundaries to limit the maximum permissions that can be granted by any role
- Review and remove unused IAM roles and policies regularly using IAM Access Analyzer

### Detection and Monitoring

- Enable AWS Security Hub to aggregate findings from GuardDuty, Inspector, Macie, Config, and Firewall Manager
- Create CloudWatch metric filters and alarms for security-relevant API calls (root account usage, policy changes, security group modifications)
- Use AWS Config rules to enforce and detect configuration compliance continuously
- Export CloudTrail logs to a centralized, immutable S3 bucket in a dedicated log-archive account

### Infrastructure Protection

- Use VPC with private subnets for all workload compute; place only load balancers in public subnets
- Apply security groups at the resource level; use NACLs as a secondary control at the subnet level
- Use AWS WAF on API Gateway, CloudFront, and ALB to protect against common web exploits
- Enable AWS Shield Advanced for DDoS protection on public endpoints
- Use VPC endpoints (PrivateLink) to access AWS services without traversing the public internet

### Data Protection

- Classify all data: public, internal, confidential, restricted
- Enable SSE (server-side encryption) on all S3 buckets; use KMS CMKs for sensitive data
- Use Amazon Macie to discover and protect sensitive data in S3
- Enforce TLS 1.2+ for all API and service-to-service communication
- Use AWS Certificate Manager (ACM) for all TLS certificates; never embed private keys in code or config

### Incident Response

- Define an incident response plan with severity levels, escalation paths, and communication templates
- Use AWS Systems Manager Incident Manager for structured incident tracking
- Pre-provision forensic IAM roles and isolated VPCs for incident investigation
- Automate initial triage: use Lambda-triggered by GuardDuty findings to isolate compromised instances

---

## Pillar 3: Reliability

### Foundations

- Set and monitor AWS service quotas; request quota increases proactively before reaching limits
- Use AWS Organizations and Control Tower to enforce guardrails across accounts
- Design network topology for fault isolation: separate VPCs per environment, Transit Gateway for connectivity

### Workload Architecture

- Use stateless compute components; store all state in managed data stores (DynamoDB, RDS, ElastiCache)
- Implement the bulkhead pattern: isolate failures in one subsystem from propagating to others
- Use SQS dead-letter queues (DLQ) to capture and reprocess failed messages
- Apply the saga pattern for distributed transactions across microservices
- Use idempotent operations so retries do not cause duplicate side effects

### Change Management

- Deploy infrastructure changes through CI/CD pipelines; no manual changes in production
- Use AWS CloudFormation StackSets or CDK Pipelines for multi-account, multi-region deployments
- Implement canary deployments with automatic rollback using CodeDeploy or Lambda aliases
- Test backward compatibility of API changes before deploying; use contract tests

### Failure Management

- Implement multi-region active-active or active-passive for critical workloads based on RPO/RTO targets
- Use Route 53 health checks with failover routing to redirect traffic during regional failures
- Test failover procedures: run DR drills at least quarterly
- Use AWS Backup for centralized, policy-driven backup across RDS, DynamoDB, EFS, and EC2

---

## Pillar 4: Performance Efficiency

### Selection

| Resource Type | Guidance                                                                                                                                                                  |
| ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Compute       | Match instance family to workload: compute-optimized (C-family) for CPU-bound, memory-optimized (R-family) for in-memory data, storage-optimized (I-family) for high IOPS |
| Storage       | S3 for object storage, EBS gp3 for general block storage, io2 for high-IOPS databases, EFS for shared file systems                                                        |
| Database      | Aurora for relational; DynamoDB for key-value/document at scale; ElastiCache (Redis) for low-latency caching; Redshift for analytics                                      |
| Network       | Place resources in the same AZ to minimize cross-AZ latency; use placement groups for HPC workloads                                                                       |

### Review

- Use AWS Compute Optimizer recommendations to identify under-utilized and mis-sized resources
- Benchmark new instance types or storage options in staging before production migration
- Profile application performance with AWS X-Ray to identify bottlenecks in call chains

### Monitoring

- Define performance SLOs (p50, p95, p99 latency; throughput; error rate) for every public API
- Use CloudWatch Container Insights for ECS/EKS workloads; Lambda Insights for functions
- Alert on sustained high CPU/memory utilization as a signal of under-sizing, not just capacity risk

### Trade-offs

- Latency vs. cost: caching reduces latency and backend load but adds complexity and potential for stale data; apply TTLs deliberately
- Throughput vs. simplicity: batching reduces API call overhead but increases response latency; choose based on consumer requirements
- Provisioned vs. on-demand capacity: provisioned DynamoDB is cheaper at sustained high throughput; on-demand suits unpredictable or low-volume workloads

---

## Pillar 5: Cost Optimization

### Cloud Financial Management

- Assign a FinOps owner or team responsible for cost visibility and optimization
- Use AWS Cost and Usage Report (CUR) exported to S3 + Athena or QuickSight for cost analysis
- Establish monthly cost reviews; set budget thresholds with SNS alerts at 80% and 100% of budget
- Use AWS Organizations consolidated billing to aggregate volume discounts

### Expenditure Awareness

- Apply resource tagging policy as an SCP or Config rule; block resource creation without required tags
- Use Cost Allocation Tags to produce per-workload, per-team cost reports
- Review top cost drivers monthly in Cost Explorer; identify unexpected cost spikes

### Cost-Effective Resources

- Use Graviton (ARM) instances for compatible workloads: ~20% lower cost, better performance per watt
- Purchase Compute Savings Plans for 1- or 3-year commitments on predictable EC2, Lambda, and Fargate usage
- Use Spot Instances for stateless, fault-tolerant workloads (batch jobs, CI runners, ML training)
- Use S3 Intelligent-Tiering for data with unpredictable access patterns
- Delete unattached EBS volumes, obsolete snapshots, and unused Elastic IPs

### Demand and Supply Management

- Use Application Auto Scaling to right-size compute in response to actual demand
- Use Lambda and Fargate Spot for event-driven, burst workloads where cold starts are acceptable
- Schedule non-production environments to stop outside business hours using EventBridge Scheduler or Instance Scheduler

---

## Pillar 6: Sustainability

### Utilization and Efficiency

- Target CPU utilization of 60-80% for sustained workloads; right-size instances that run below 20% utilization
- Use Graviton instances where compatible — better performance per watt for most workload types
- Consolidate workloads onto fewer, larger instances where isolation is not required
- Prefer containers (ECS/EKS) over dedicated EC2 to improve host utilization through bin-packing

### Software and Data Patterns

- Implement efficient algorithms and data structures to reduce CPU cycles and memory usage
- Use asynchronous processing and event-driven patterns to smooth demand and eliminate polling waste
- Compress data before storage and in transit to reduce storage footprint and network throughput
- Apply S3 Lifecycle policies: transition to S3-IA after 30 days, S3 Glacier after 90 days for archival data

### Hardware Adoption

- Adopt new AWS hardware generations (instance types) as they become available; they deliver better efficiency
- Use AWS managed hardware refresh automatically via managed services (RDS, ElastiCache, Lambda)
- Prefer managed services (Fargate, Aurora Serverless) to offload hardware lifecycle responsibility to AWS

### Downstream Impact

- Optimize APIs and web assets to reduce data transferred to clients (pagination, compression, CDN)
- Use CloudFront to cache responses at edge, reducing origin compute load and client-side latency
- Design mobile and web clients to batch requests and minimize polling; prefer webhooks and WebSockets for real-time needs
