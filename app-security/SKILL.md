---
name: app-security
description: >-
  Application and infrastructure security review skill. Use this skill whenever
  reviewing, auditing, designing, or hardening any application — whether it's a
  new project, a PR review, an architecture decision, or a "is this secure?"
  question. Covers OWASP Top 10, cloud infrastructure (AWS, Azure, GCP),
  serverless security, API security, authentication/authorization, secrets
  management, dependency supply chain, CI/CD pipeline hardening, and
  observability. Trigger this skill for any mention of security audit, threat
  model, hardening, vulnerability, pen-test prep, compliance checklist, or
  secure-by-default architecture. Also trigger when the user asks to review
  Terraform/IaC, Lambda functions, API Gateway configs, IAM policies, or
  Cognito setups — even if they don't explicitly say "security."
license: CC-BY-4.0
metadata:
  author: kayaman
  version: "1.0.0"
  model: claude-opus-4-6
  generated: "2026-04-06"
  repository: https://github.com/kayaman/skills
  category: security
  tags: security, owasp, aws, cloud, iac, appsec, devsecops
---

# Application & Infrastructure Security

A comprehensive security review framework for modern web applications.
Structured as actionable checklists organized by domain, suitable for both
quick audits and thorough threat modeling sessions.

## How to Use This Skill

When reviewing an application:

1. **Identify the stack** — read the project's README, IaC files, and deployment config
2. **Select relevant domains** from the checklist below
3. **Walk through each item**, flagging findings as PASS / FAIL / N/A / NEEDS-REVIEW
4. **For each FAIL**, provide a concrete remediation with code or config example
5. **Summarize** with a severity-ranked findings table

For deeper guidance on any domain, read the corresponding file in `references/`.

---

## Security Domains & Checklists

### 1. Authentication & Authorization

- [ ] Passwords hashed with bcrypt/scrypt/argon2 (never MD5/SHA1)
- [ ] MFA enabled or available for all user-facing auth
- [ ] JWTs validated server-side: signature, expiration, issuer, audience
- [ ] JWT secrets/keys rotated periodically; asymmetric signing preferred (RS256/ES256)
- [ ] Session tokens have reasonable expiration and are revoked on logout
- [ ] OAuth/OIDC flows use PKCE for public clients
- [ ] Authorization checks happen at the resource level, not just route level (IDOR prevention)
- [ ] Cognito/Auth0/Entra ID: custom auth flows reviewed for logic bypass
- [ ] Rate limiting on login/OTP/password-reset endpoints
- [ ] Account enumeration prevented (consistent responses for valid/invalid accounts)

> **Reference**: `references/authn-authz.md`

### 2. API Security

- [ ] All endpoints require authentication unless explicitly public
- [ ] Input validation on every field (type, length, format, range)
- [ ] Output encoding to prevent XSS in API responses rendered by clients
- [ ] CORS restricted to known origins (no `*` in production)
- [ ] Rate limiting per user/IP with appropriate HTTP 429 responses
- [ ] Request size limits enforced (body, headers, query params)
- [ ] No sensitive data in URLs or query strings (use POST bodies or headers)
- [ ] API versioning strategy prevents breaking changes from exposing old vulns
- [ ] GraphQL: query depth limiting, introspection disabled in production
- [ ] Error responses don't leak stack traces, internal paths, or DB schemas

> **Reference**: `references/api-security.md`

### 3. Cloud Infrastructure (AWS Focus)

- [ ] IAM policies follow least privilege — no `Action: *` or `Resource: *`
- [ ] Lambda execution roles scoped to specific tables/buckets/queues
- [ ] No hardcoded credentials; use IAM roles, SSM Parameter Store, or Secrets Manager
- [ ] S3 buckets: public access blocked unless explicitly required; encryption at rest enabled
- [ ] CloudFront: HTTPS-only, TLS 1.2+, security headers (HSTS, CSP, X-Frame-Options)
- [ ] DynamoDB: encryption at rest enabled, fine-grained access control via IAM
- [ ] VPC: Lambda in VPC only if accessing private resources; security groups least-privilege
- [ ] CloudTrail enabled for all regions; log file validation on
- [ ] GuardDuty enabled; findings reviewed and actioned
- [ ] Resource tags for cost and access control accountability

> **Reference**: `references/cloud-aws.md` (also `references/cloud-azure.md`, `references/cloud-gcp.md`)

### 4. Infrastructure as Code (Terraform/CDK/CloudFormation)

- [ ] No secrets in `.tf` files, `.tfvars` committed, or CDK code — use variables + vault
- [ ] `.tfstate` stored remotely with encryption and locking (S3 + DynamoDB)
- [ ] IaC scanned with tfsec, checkov, or trivy before apply
- [ ] `terraform plan` output reviewed in PR before merge
- [ ] Provider versions pinned; module versions pinned
- [ ] Drift detection: periodic `terraform plan` to catch manual changes
- [ ] Sensitive outputs marked `sensitive = true`
- [ ] No overly permissive security groups (0.0.0.0/0 ingress without justification)

> **Reference**: `references/iac-security.md`

### 5. Secrets Management

- [ ] No secrets in source code, environment variables baked into images, or logs
- [ ] Secrets stored in AWS Secrets Manager, SSM Parameter Store, Azure Key Vault, or similar
- [ ] Secrets rotated on a schedule; rotation is automated where possible
- [ ] `.env` files in `.gitignore`; `.tfvars` with secrets in `.gitignore`
- [ ] CI/CD secrets use platform-native secret stores (GitHub Secrets, etc.)
- [ ] API keys scoped to minimum required permissions
- [ ] Git history scanned for leaked secrets (truffleHog, gitleaks)
- [ ] Pre-commit hooks prevent accidental secret commits

> **Reference**: `references/secrets.md`

### 6. Dependency & Supply Chain Security

- [ ] Dependencies pinned to exact versions (lockfiles committed)
- [ ] Automated vulnerability scanning (Dependabot, Snyk, npm audit, pip-audit)
- [ ] No unnecessary dependencies; unused deps removed
- [ ] Private registries or mirrors for critical deps
- [ ] Docker/container base images from trusted sources; pinned by digest
- [ ] SBOM generated for production artifacts
- [ ] GitHub Actions: actions pinned by SHA, not tag
- [ ] Renovate/Dependabot PRs reviewed promptly

> **Reference**: `references/supply-chain.md`

### 7. CI/CD Pipeline Security

- [ ] CI/CD runs in isolated environments; no shared credentials across projects
- [ ] Build artifacts signed or checksummed
- [ ] Branch protection: required reviews, status checks, no force-push to main
- [ ] Deployment credentials are short-lived (OIDC federation with cloud providers)
- [ ] Pipeline config changes require review (GitHub Actions YAML, etc.)
- [ ] No `pull_request_target` with checkout of PR head (GitHub Actions injection)
- [ ] Container images scanned before push to registry
- [ ] Rollback plan documented and tested

> **Reference**: `references/cicd-security.md`

### 8. Frontend & PWA Security

- [ ] Content Security Policy (CSP) header configured; no `unsafe-inline` without nonce
- [ ] Subresource Integrity (SRI) for third-party scripts
- [ ] Service worker scope minimized; no caching of sensitive data
- [ ] localStorage/sessionStorage: no tokens or secrets stored unencrypted
- [ ] HTTPS enforced everywhere; HSTS with `includeSubDomains` and `preload`
- [ ] Third-party scripts audited and minimized
- [ ] Form inputs sanitized client-side AND server-side
- [ ] Share Target / Web Share API: input validated before processing

> **Reference**: `references/frontend-security.md`

### 9. Data Protection & Privacy

- [ ] PII encrypted at rest and in transit
- [ ] Data classification applied (public, internal, confidential, restricted)
- [ ] Database backups encrypted; access to backups restricted
- [ ] Logs sanitized — no PII, tokens, or secrets in log output
- [ ] Data retention policies defined and enforced (TTL on DynamoDB, lifecycle on S3)
- [ ] GDPR/LGPD: consent mechanisms, data export, right to deletion implemented
- [ ] Cross-border data transfer compliance verified

> **Reference**: `references/data-protection.md`

### 10. Observability & Incident Response

- [ ] Centralized logging with tamper-evident storage
- [ ] Security-relevant events logged: auth failures, permission denials, input validation failures
- [ ] Alerting on anomalous patterns (brute force, unusual API usage, privilege escalation)
- [ ] Runbooks for common incident types (credential leak, DDoS, data breach)
- [ ] Incident response contacts and escalation paths documented
- [ ] Post-incident review process defined
- [ ] WAF rules reviewed periodically (CloudFront, API Gateway)

> **Reference**: `references/observability-ir.md`

---

## OWASP Top 10 (2021) Quick Cross-Reference

| # | Risk | Primary Checklist Domains |
|---|------|--------------------------|
| A01 | Broken Access Control | 1, 2 |
| A02 | Cryptographic Failures | 1, 5, 9 |
| A03 | Injection | 2, 8 |
| A04 | Insecure Design | All (threat modeling) |
| A05 | Security Misconfiguration | 3, 4, 7 |
| A06 | Vulnerable Components | 6 |
| A07 | Auth Failures | 1 |
| A08 | Software/Data Integrity | 6, 7 |
| A09 | Logging/Monitoring Failures | 10 |
| A10 | SSRF | 2, 3 |

---

## Threat Modeling (Lightweight)

When performing a threat model for any application:

1. **Draw the architecture** — identify trust boundaries, data flows, entry points
2. **STRIDE per element** — for each component, ask:
   - **S**poofing: Can an attacker impersonate a user or service?
   - **T**ampering: Can data be modified in transit or at rest?
   - **R**epudiation: Can actions be denied without evidence?
   - **I**nformation Disclosure: Can sensitive data leak?
   - **D**enial of Service: Can the service be overwhelmed?
   - **E**levation of Privilege: Can a low-privilege user gain higher access?
3. **Rank risks** — likelihood × impact → priority
4. **Define mitigations** — map each risk to a checklist item above

---

## Findings Report Template

When presenting results, use this structure:

```
## Security Review — [Application Name]
### Date: YYYY-MM-DD
### Scope: [what was reviewed]

### Critical Findings
| # | Domain | Finding | Severity | Remediation |
|---|--------|---------|----------|-------------|

### Summary
- Total items reviewed: N
- PASS: N | FAIL: N | N/A: N | NEEDS-REVIEW: N
- Critical: N | High: N | Medium: N | Low: N

### Recommendations (prioritized)
1. ...
```
