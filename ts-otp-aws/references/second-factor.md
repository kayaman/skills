# Second factors layered on OTP

Brief sketch — this skill is OTP-first; full WebAuthn / TOTP coverage belongs in dedicated skills. Use this when the user asks "how do I add a second factor on top of the OTP login I just built?"

## The framing

OTP via email/SMS is **single-factor**: possession of the inbox or phone number. To raise the bar for sensitive accounts:

1. **OTP for sign-in**, then **TOTP** (RFC 6238 authenticator app) for step-up on sensitive actions.
2. **OTP for sign-in**, then **WebAuthn passkey** for step-up — phishing-resistant, no shared secret.
3. **Passkey for sign-in (primary)**, with **OTP as account-recovery fallback** when the device is lost.

The third pattern is the modern target. The bundled OTP flow becomes the recovery channel, not the primary auth.

## TOTP add-on (sketch)

After successful OTP auth, prompt for TOTP enrollment:

1. Generate a base32 secret, store **encrypted at rest** (KMS-backed) keyed by user.
2. Render a `otpauth://totp/<issuer>:<account>?secret=<base32>&issuer=<issuer>` QR code (use `qrcode` npm package).
3. User scans into Authy / 1Password / Google Authenticator.
4. On step-up, accept any 6-digit code derived from `HMAC-SHA1(secret, floor(now/30))` within a ±1 window.

In magj-dev, this lives at `lambda/src/auth/admin-mfa-handlers.ts` with crypto helpers in `admin-mfa-crypto.ts`. The encryption key is fetched from Secrets Manager via `lambda/src/shared/secrets.ts` (lazy + cached).

`@simplewebauthn/server` and the Node `otplib` package are the typical TS dependencies.

## WebAuthn passkey add-on (sketch)

After successful OTP auth, prompt for passkey enrollment:

1. Server: `generateRegistrationOptions({ rpName, rpID, userID, userName })` from `@simplewebauthn/server`.
2. Browser: `navigator.credentials.create(...)` with the returned options.
3. Server: `verifyRegistrationResponse(...)` and store the resulting `credentialID + publicKey + counter` per user.
4. On sign-in: `generateAuthenticationOptions` → browser `navigator.credentials.get(...)` → server `verifyAuthenticationResponse`.

magj-dev has a working WebAuthn enrollment + verification path for admins; treat it as a reference implementation. Keys live alongside the user record in DynamoDB.

## When to graduate the architecture

If passkeys become primary and OTP becomes recovery-only:

- Move the OTP flow behind a `/recover` endpoint, not the main login.
- Tighten the OTP rate limit harder (1 OTP per 24h per identifier, hard 24h cooldown after a recovery flow completes).
- Require re-authentication with the passkey after recovery before any destructive action.

## Out of scope here

- The full RFC 6238 / RFC 4226 implementation details — `otplib` covers them. Read *Real-World Cryptography* (Wong) chapter on HMAC-based auth for the protocol grounding.
- The full WebAuthn ceremony — `@simplewebauthn/server` docs are the right reference.
- Recovery-code grids ("write down these 10 codes") — different threat model; not addressed.

## Sources

- *Real-World Cryptography* — David Wong — HMAC-based OTP, TOTP/HOTP background.
- magj-dev internal: `lambda/src/auth/admin-mfa-handlers.ts`, `admin-mfa-crypto.ts`, `admin-mfa-store.ts` — working TOTP + passkey pattern.
- `@simplewebauthn/server` and `otplib` library docs.
