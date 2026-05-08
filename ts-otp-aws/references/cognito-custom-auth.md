# Cognito CUSTOM_AUTH walkthrough

Load this when implementing or debugging the four Cognito Lambda triggers.

## Trigger order

```
client                 Cognito                   triggers
  │  InitiateAuth         │                          │
  │ ──────────────────▶   │  DefineAuthChallenge ──▶ │  (no session → CUSTOM_CHALLENGE)
  │                       │  CreateAuthChallenge ──▶ │  (generate OTP, send via SES/SNS, stash in private params)
  │ ◀── session + hint ── │                          │
  │                       │                          │
  │  RespondToAuth        │                          │
  │ ──────────────────▶   │  VerifyAuthChallenge ──▶ │  (constant-time compare)
  │                       │  DefineAuthChallenge ──▶ │  (correct → issueTokens; wrong → another, until cap)
  │ ◀── id/access/refr ── │                          │
```

`PreSignUp` runs once when the user is created (auto-confirm + auto-verify so the first `InitiateAuth` doesn't trip on an unconfirmed account).

## Dispatcher pattern

One Lambda, one handler, switch on `event.triggerSource`. See `assets/handlers/handler.ts`. The `default` arm throws to make unknown triggers loud — they shouldn't reach the function unless Terraform wired the wrong ARN.

CloudWatch payload on failure:

```ts
{ triggerSource, userPoolId, userName, errorName, errorMessage, httpStatusCode }
```

The SDK error name (`MessageRejected`, `MailFromDomainNotVerified`, `AccessDenied`, `OptedOut`) is the most useful field — grep for it directly when triaging.

## `define-challenge.ts` — the state machine

3 states based on `request.session`:

1. **Empty session** → first call → emit `CUSTOM_CHALLENGE`, no tokens.
2. **Last challenge correct** → `issueTokens=true`.
3. **Last challenge wrong** + under cap (`MAX_ATTEMPTS=3`) → emit another `CUSTOM_CHALLENGE`.
4. **Wrong** + at cap → `failAuthentication=true`.

The 3-attempt cap is enforced here, not in `verify-challenge`. Don't move it.

## `create-challenge.ts` — generation + delivery

Reads channel from `event.request.clientMetadata?.channel` (set by your frontend `InitiateAuthCommand` call). Defaults to `email`. Generates the OTP with `randomInt(0, 1_000_000).toString().padStart(6, "0")` — cryptographically random, no `Math.random`.

Critical phantom-user branch:

```ts
const phantom = event.request.userNotFound === true;
if (!phantom) {
  // send the email or SMS
}
// always return a synthetic challenge so InitiateAuth replies identically
```

Throwing on phantom users surfaces as `UserLambdaValidationException` and leaks user existence. The bundled handler gets this right; if you hand-roll, mirror the pattern.

The OTP itself goes into `privateChallengeParameters.code` — Cognito stores this server-side and hands it back to `verify-challenge` in the same flow. **Never** put it in `publicChallengeParameters` (those are returned to the client).

`publicChallengeParameters` carries only `{ channel, hint }` where `hint` is `maskTail(...)` — `***1234`, not the raw email/phone.

## `verify-challenge.ts` — comparison

```ts
import { timingSafeEqual } from "node:crypto";
const ab = Buffer.from(expected, "utf8");
const bb = Buffer.from(actual, "utf8");
if (ab.length !== bb.length) return false;
return timingSafeEqual(ab, bb);
```

Reject early if `actual` is not exactly 6 digits (`/^\d{6}$/`). Dev bypass: `OTP_DEV_BYPASS=1` accepts the constant `000000` — never set this in production.

`event.response.answerCorrect = true | false` is the only output. Cognito calls `define-challenge` again right after, and that's where the cap and token issuance decision happens.

## `pre-signup.ts` — auto-confirm

```ts
event.response.autoConfirmUser = true;
event.response.autoVerifyEmail = true;
event.response.autoVerifyPhone = true;
```

Use only when the identity is already proven by the OTP itself (i.e. signup IS the first login). If you have an out-of-band proof (admin invite, prepaid email confirmation), keep this on. If you require the classic confirmation-code flow, remove the trigger.

## Common failure modes

| Symptom | Likely cause |
|---|---|
| `UserLambdaValidationException` on `InitiateAuth` | A trigger threw. Check CloudWatch for the dispatcher's `auth-triggers failed` line, look at `errorName`. |
| `MessageRejected: Email address is not verified` | SES sandbox not exited, or `SES_FROM` not verified for this region. |
| `OptedOut` on SNS publish | The phone number is on the SNS opt-out list. Surface a generic "we couldn't send a code" message. |
| `NotAuthorizedException` after a few attempts | The session expired (3-min default) or the cap was hit. Restart `InitiateAuth`. |
| OTP delivered, verification always fails | `privateChallengeParameters` not making the round-trip — check that `create-challenge` writes `code`, not `otp`, and that `verify-challenge` reads the same key. |
| Account existence leaks ("user does not exist") | Phantom-user branch in `create-challenge` is throwing instead of returning. |

## Frontend wiring

`InitiateAuthCommand` with `AuthFlow: "CUSTOM_AUTH"` and `ClientMetadata: { channel: "email" | "sms" }`. Then `RespondToAuthChallengeCommand` with `ChallengeName: "CUSTOM_CHALLENGE"` and `ChallengeResponses: { USERNAME, ANSWER: code }`. See `assets/frontend/cognito-server-snippet.ts` for a working server-side adapter (resolves phone → username via `ListUsers`, returns `{session, hint}` to the client).

## Sources

- Brisals & Hedger, *Serverless Development on AWS* (O'Reilly) — passwordless authentication appendix.
- Mathieu, *Mastering AWS Security 2e* (Packt) — Cognito chapter on `CUSTOM_AUTH`.
- AWS docs (referenced in `citations.md`).
