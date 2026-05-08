# Security checklist

Load this when reviewing OTP code before production cutover or auditing an existing implementation.

## Code generation & comparison

- [ ] OTP generated with `crypto.randomInt(0, 1_000_000).toString().padStart(6, "0")`. **Not** `Math.random()`.
- [ ] Comparison uses `crypto.timingSafeEqual` after a length check; never `===` or `==`.
- [ ] Compared values are encoded as `Buffer.from(s, "utf8")` (not Latin-1 / binary), and lengths match before `timingSafeEqual` (it throws on mismatched lengths).
- [ ] Reject early if `actual` doesn't match `/^\d{6}$/`. No spaces, dashes, locale digits.

## Storage

- [ ] Cognito path: OTP lives only in `privateChallengeParameters.code` for the lifetime of the auth session. Cognito-managed; no extra writes.
- [ ] Custom path: OTP **hash** (sha256 with per-deployment salt) stored in DynamoDB, not the code itself.
- [ ] DynamoDB TTL attribute name is `ttl`, value is epoch seconds. **Not** ISO strings — TTL only deletes numeric epoch attributes.
- [ ] OTP expiry ≤ 5 minutes (300 s). Longer expiries widen the brute-force window.
- [ ] Rate-limit counter has its own TTL (1 hour) so old buckets self-clean.

## Rate limiting & brute force

- [ ] Per-session attempt cap = **3** (in `define-challenge.ts` for Cognito; in the verify endpoint's `ConditionExpression` for custom).
- [ ] Per-identifier issuance cap = **3 per hour** minimum; raise the bar on suspected abuse.
- [ ] Server-side enforcement only. **Never** trust a client-side counter or a session cookie for the cap.
- [ ] Cap increment happens **before** the hash comparison (custom path) — `UpdateItemCommand` with `ADD attempts :one` and `ConditionExpression`. A correct guess still costs an attempt, but the atomic increment closes parallel-guess races.

## Account enumeration

- [ ] Cognito user pool has `prevent_user_existence_errors = "ENABLED"`.
- [ ] `create-challenge.ts` returns silently when `event.request.userNotFound === true`. **Throwing leaks existence.**
- [ ] Custom path `/otp/start` always returns `{ ok: true }` (or empty 204), regardless of whether the identifier exists, the rate limit was hit, or SES/SNS failed.
- [ ] Error messages on `/otp/verify` collapse to `wrong code | session expired` — never "user not found" or "no OTP issued for this email".

## Logging & PII

- [ ] OTP code is **never** in logs. Don't `console.log(event)` (it includes `privateChallengeParameters`). The bundled handler logs only `triggerSource`, `userPoolId`, `userName`, error name/message/status.
- [ ] Email/phone in logs is masked (`***1234`) for normal operations; full PII only when a flag enables debug logging in non-prod.
- [ ] Lambda env vars containing secrets are encrypted (KMS-managed key, not the default account key) — though OTP-related Lambdas typically have no secrets in env.
- [ ] CloudTrail enabled on the Cognito user pool and the OTP Lambda function.

## Channel security

- [ ] SES domain verified, DKIM aligned, SPF on MAIL FROM, DMARC at minimum `p=none` with reporting.
- [ ] SES out of sandbox before any production traffic.
- [ ] SNS `MonthlySpendLimit` set; no surprise five-figure bills from SMS pumping.
- [ ] SNS `SMSType=Transactional` on every OTP publish.
- [ ] `SenderID` is **not** treated as authentication — it's cosmetic and stripped on US/Canada traffic.

## Transport & frontend

- [ ] All OTP endpoints behind TLS only (no HTTP fallback).
- [ ] No OTP in URL query strings (browser history, referer, server logs). Body only.
- [ ] CSP allowlist for the Cognito IdP endpoint (`cognito-idp.<region>.amazonaws.com`) when calling from the browser.
- [ ] No autofill leakage: input has `autocomplete="one-time-code"` and `inputmode="numeric"` so the OS surfaces the SMS code without exposing it elsewhere.

## Replay & session

- [ ] Single-use semantics: Cognito invalidates the challenge on success; custom path **deletes** the OTP record on a verified guess.
- [ ] After 3 wrong attempts, the session is dead. No "try again" loop on the same OTP — the user must restart `InitiateAuth`.
- [ ] Refresh tokens (Cognito) have a sane lifetime (e.g. 30 days), not the default 10 years.

## Threat-model sanity check

Run this conversation before shipping:

1. "What happens if an attacker runs `/otp/start` for a target's email 10,000 times in 60 seconds?"
   → Rate-limit counter caps it; only the first N go through; SES sees one or two sends max; bill is bounded by SNS spend limit (SMS) or SES per-account limits (email).
2. "What happens if the attacker has the email and tries `000000` through `999999` against `/otp/verify`?"
   → Best case: 3 attempts then session dead, must restart. Each restart sends a real OTP, which costs money — circuit breaker on `/otp/start` per IP/user.
3. "What if SES/SNS errors fire during `create-challenge`?"
   → The dispatcher logs the error name, throws, and Cognito surfaces `UserLambdaValidationException`. The user sees a generic "we couldn't send a code, try again" message — no internals.
4. "What if a developer enables `OTP_DEV_BYPASS=1` in production?"
   → CI policy: assert this env var is unset on prod Terraform. Optionally hard-code an environment guard (`if (process.env.NODE_ENV === "production") return false`).

## Sources

- *Real-World Cryptography* — Wong — HMAC, salting, constant-time guidance.
- *AWS Security Cookbook 2e* — Kanikathottu — Cognito hardening + threat checklist.
- *Mastering AWS Security 2e* — Mathieu — IAM scoping for Cognito + Lambda triggers.
