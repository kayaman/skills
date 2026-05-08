# Architecture decision: Cognito CUSTOM_AUTH vs custom DynamoDB OTP

Load this when the agent must justify the architecture or compare options before writing code.

## Decision matrix

| Concern | Cognito `CUSTOM_AUTH` | Custom DynamoDB OTP |
|---|---|---|
| User directory | Managed user pool | You own the table |
| JWT issuance | Built-in (id + access + refresh) | You sign + rotate keys |
| MFA later (TOTP, SMS-MFA) | Toggle on the user pool | You implement |
| Federation (Google/Apple) | First-class | Bring your own (huge scope) |
| Cold-start cost | 4 trigger Lambdas | 1 Lambda |
| Lock-in | Cognito-shaped users, group claims | None |
| Audit | CloudTrail + Cognito events | You instrument |
| Free tier | 50k MAU | DynamoDB on-demand only |
| Throttle / rate limit | Cognito's limits + your trigger logic | Your DDB record |

**Default:** Cognito `CUSTOM_AUTH`. Pick custom DDB only when one of the following holds:

1. The product already issues its own JWTs and a Cognito user is dead weight.
2. You need an OTP that's not tied to a login (e.g. step-up confirmation for a destructive action).
3. Cognito region/feature gaps block you (e.g. specific compliance, regional residency).

## Threat model (both paths must defend against)

| Threat | Mitigation |
|---|---|
| Account enumeration | Cognito: `prevent_user_existence_errors=ENABLED` + phantom-user safe path in `create-challenge`. Custom: always return identical "we sent a code if the account exists" response. |
| Brute force on the code | 6-digit numeric → 1/10⁶ per try. Cap at **3 attempts** per session (`define-challenge`) + per-identifier rate limit (e.g. 3 OTPs / hour). |
| Replay | Single-use record: delete the OTP on successful verify (custom path) or rely on Cognito session invalidation. |
| Code leakage in logs | Never log `privateChallengeParameters.code` or the raw OTP. The bundled handlers don't. |
| Side-channel timing | `crypto.timingSafeEqual` after length check. |
| SMS pumping (toll fraud via SNS) | SNS `MonthlySpendLimit`, opt-out list, country-allowlist via origination identities, CAPTCHA on the start endpoint at the edge. |
| SES sender spoofing / spam folder | Verified domain identity, DKIM, custom MAIL FROM, SPF aligned, BIMI optional. |
| SIM swap | Prefer email for high-trust actions; if SMS, layer with passkey or TOTP — see `second-factor.md`. |
| Phantom-user existence leak | `create-challenge` MUST succeed silently when `event.request.userNotFound === true`. Throwing surfaces as `UserLambdaValidationException` to `InitiateAuth` and leaks. |

## Channel selection

| Action | Default | Why |
|---|---|---|
| Sign-in / sign-up confirmation | email | Cheaper, deliverability is higher, no SIM-swap surface. |
| Step-up MFA on payment / settings change | SMS or push | Different channel from primary auth. |
| Account recovery | email AND SMS as alternates | One channel can be compromised. |

## When **not** to use this skill

- You actually want **passkeys** (WebAuthn) as the primary factor — OTP is the second factor or fallback. See `second-factor.md` for layering.
- You want **TOTP** authenticator apps (Authy, 1Password) as the only factor — that's RFC 6238, different protocol; this skill doesn't cover it end-to-end.
- You want to send **marketing** email or campaigns — use Pinpoint, not SES + this skill.

## Sources

See `citations.md` for full attributions. Most relevant reading:

- *Serverless Development on AWS* — Brisals & Hedger — passwordless auth appendix (canonical for the CUSTOM_AUTH pattern).
- *AWS Security Cookbook, 2e* — Kanikathottu — Cognito chapter and trigger recipes.
- *Real-World Cryptography* — David Wong — HMAC + constant-time comparison rationale.
