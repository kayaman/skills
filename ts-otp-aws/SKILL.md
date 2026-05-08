---
name: ts-otp-aws
description: Implement OTP and passwordless authentication on AWS for TypeScript projects using Cognito CUSTOM_AUTH triggers (default) or a custom DynamoDB-backed flow, with SES (email) and SNS (SMS) delivery. Use when the user mentions OTP, one-time password, passwordless login, magic link, Cognito custom auth, DefineAuthChallenge, CreateAuthChallenge, VerifyAuthChallengeResponse, SES verification email, SNS SMS code, or MFA over email/SMS. Covers architecture decision (Cognito vs custom), Lambda trigger handlers, SES/SNS notifiers, DynamoDB schema with TTL, rate limiting, constant-time comparison, threat model (enumeration, replay, brute force), and aws-sdk-client-mock testing.
license: MIT
metadata:
  area: auth
  cloud: aws
  language: typescript
allowed-tools: Read Grep Glob Bash Edit Write
---

# ts-otp-aws

Implement OTP / passwordless authentication on AWS for TypeScript projects.

## When to use

- Adding email or SMS verification codes to a TypeScript app on AWS Lambda.
- Wiring or debugging Cognito `CUSTOM_AUTH` triggers (`DefineAuthChallenge`, `CreateAuthChallenge`, `VerifyAuthChallengeResponse`, `PreSignUp`).
- Standing up a non-Cognito OTP flow on DynamoDB with TTL.

## Default approach

Cognito User Pool with `CUSTOM_AUTH` flow + four Lambda triggers, SESv2 for email, SNS for SMS. The user pool stays the source of truth; the four triggers handle OTP generation, delivery, and verification. Drop-in handlers and Terraform live in `assets/`. The custom-DynamoDB alternate is documented in [`references/custom-dynamodb-otp.md`](references/custom-dynamodb-otp.md) — pick it only when you can't use Cognito.

## Cognito vs custom — quick decision

| If you need… | Pick |
|---|---|
| Managed user directory, JWTs, MFA toggle | Cognito `CUSTOM_AUTH` |
| Standalone API, no user pool, full control over JWT | custom DynamoDB |
| Federation (Google/Apple) alongside OTP | Cognito (out of scope here) |
| Lowest latency, no cold-start triggers | custom DynamoDB |

Full matrix + threat model: [`references/architecture-decision.md`](references/architecture-decision.md).

## Architecture at a glance

```
┌────────┐  InitiateAuth(CUSTOM_AUTH)   ┌──────────────┐  Define→Create   ┌──────────────────┐
│ client │ ───────────────────────────▶ │   Cognito    │ ───────────────▶ │ auth-triggers λ  │
│ (Next/ │ ◀── session + masked hint ── │  User Pool   │                  │ ─ create-chall   │
│ Astro) │                              │              │                  │ ─ define-chall   │
│        │  Respond(answer=otp)         │              │                  │ ─ verify-chall   │
│        │ ───────────────────────────▶ │              │                  │ ─ pre-signup     │
│        │ ◀── id/access/refresh ────── │              │                  └────┬──────┬──────┘
└────────┘                              └──────────────┘                       │      │
                                                                          SESv2│      │SNS
                                                                       ┌───────▼──┐ ┌─▼──────┐
                                                                       │  email   │ │  SMS   │
                                                                       └──────────┘ └────────┘
```

Custom path swaps Cognito + triggers for one Lambda + a DynamoDB OTP table (PK/SK + `ttl`).

## Step 1 — Audit the project

```bash
scripts/audit-project.sh /path/to/repo
```

Reports which patterns the repo already has (Cognito CUSTOM_AUTH, custom DDB, client-only) and what's missing. Exits non-zero on missing `rg`. See `scripts/README.md` for sample output.

## Step 2 — Pick the path

- Existing Cognito user pool, or you want managed JWT issuance → **Cognito CUSTOM_AUTH** (continue to Step 3).
- No user pool, single-purpose API, or you already issue your own JWTs → **custom DynamoDB** (jump to [`references/custom-dynamodb-otp.md`](references/custom-dynamodb-otp.md)).

## Step 3 — Drop in handlers (Cognito path)

Copy the five trigger handlers and two notifiers verbatim:

```
assets/handlers/      → lambda/auth-triggers/src/handlers/
assets/notifiers/     → lambda/auth-triggers/src/notifiers/
```

Required env vars on the Lambda:

| Var | Purpose |
|---|---|
| `SES_FROM` | Verified SES sender (e.g. `noreply@yourdomain.com`) |
| `SMS_SENDER_ID` | 3–11 alphanumeric SMS sender (default `OTP`) |
| `OTP_DEV_BYPASS` | Set to `1` only in non-prod to accept `000000` |
| `APP_NAME` | Brand string used in email/SMS body |

The dispatcher (`handler.ts`) routes by `event.triggerSource`. Walkthrough of each trigger and the phantom-user (`prevent_user_existence_errors`) path: [`references/cognito-custom-auth.md`](references/cognito-custom-auth.md).

## Step 4 — Wire infrastructure (Terraform)

Minimum viable set under `assets/terraform/`:

- `cognito-userpool.tf` — pool + 4 trigger ARN bindings, `prevent_user_existence_errors=ENABLED`, no MFA (OTP **is** the auth).
- `auth-triggers-lambda.tf` — Node 22 ESM Lambda, log retention, IAM role.
- `ses-identity.tf` — domain identity + DKIM + custom MAIL FROM.
- `sns-sms.tf` — `MonthlySpendLimit`, `DefaultSMSType=Transactional`, opt-out preferences.
- `dynamodb-otp-table.tf` — only for the custom path (PK/SK + `ttl` + PITR + deletion protection).

IAM least-privilege policies: `assets/iam/auth-trigger-policy.json` and `assets/iam/custom-otp-policy.json`.

## Step 5 — Frontend integration

Server-side adapter calling `InitiateAuthCommand` + `RespondToAuthChallengeCommand` lives at `assets/frontend/cognito-server-snippet.ts`. Key points:

- `AuthFlow: "CUSTOM_AUTH"`, pass `ClientMetadata: { channel: "email" | "sms" }`.
- For phone identifiers, `ListUsers` with `phone_number = "..."` filter; pass through unknown identifiers unchanged so Cognito's phantom-user path stays opaque.
- Error mapping: `NotAuthorizedException` → session expired; fresh challenge response → wrong code.

## Step 6 — Security must-haves

- Constant-time OTP comparison (`crypto.timingSafeEqual`); reject early if not 6 ASCII digits.
- 3-attempt cap inside `define-challenge.ts`; surface as `failAuthentication=true`.
- 5-minute OTP TTL; never log the code.
- Phantom-user safety: never throw on `userNotFound=true` — silently return a synthetic challenge or you'll leak existence.
- SES out of sandbox, MAIL FROM domain set, DKIM aligned. SNS spend limit + transactional + sender-ID per region.
- Mask channel hint (`***1234`, not `+5511915551234`).

Full checklist: [`references/security-checklist.md`](references/security-checklist.md).

## Step 7 — Test

`aws-sdk-client-mock` v4, one mock per service. Inline minimum:

```ts
import { SESv2Client, SendEmailCommand } from "@aws-sdk/client-sesv2";
import { mockClient } from "aws-sdk-client-mock";
const ses = mockClient(SESv2Client);
ses.on(SendEmailCommand).resolves({});
// run handler, then:
expect(ses.commandCalls(SendEmailCommand)).toHaveLength(1);
```

State-machine and phantom-user assertions: [`references/testing-patterns.md`](references/testing-patterns.md).

## Custom DynamoDB alternate + second factor

When Cognito is not an option, follow [`references/custom-dynamodb-otp.md`](references/custom-dynamodb-otp.md). For layering TOTP authenticator apps or WebAuthn passkeys on top of OTP, see [`references/second-factor.md`](references/second-factor.md) — kept brief on purpose.

Channel deliverability (SES sandbox/DKIM, SNS 10DLC/DLT/origination): [`references/messaging-channels.md`](references/messaging-channels.md). Source attributions: [`references/citations.md`](references/citations.md).

## Validation

- `skills-ref validate /home/kayaman/Projects/ts-otp-aws-skill` (frontmatter + naming).
- `scripts/audit-project.sh ~/Projects/ai-assisted-dev` should say "Cognito CUSTOM_AUTH — complete".
- `wc -l SKILL.md` < 200; each `references/*.md` < 500.

## Out of scope

- Pinpoint marketing campaigns (this is transactional auth).
- Cognito IdP federation (Google/Apple).
- Full WebAuthn/passkey or HOTP/TOTP authenticator-app implementations.
- UI component libraries (an `OtpCodeInput` is referenced but not bundled).
- Generic IAM/Lambda/Terraform fundamentals.
