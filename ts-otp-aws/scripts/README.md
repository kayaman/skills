# scripts/

## `audit-project.sh`

Read-only audit of a TypeScript/AWS repo. Detects OTP-related patterns and prints a punch list grouped by category, then a verdict.

### Usage

```bash
scripts/audit-project.sh /path/to/repo
```

### Verdicts

- `cognito-custom-auth — complete` — Cognito CUSTOM_AUTH triggers + SES/SNS delivery present (matches `ai-assisted-dev` shape).
- `cognito-custom-auth — partial` — handlers present but no channel delivery yet.
- `custom-dynamodb-otp — complete` — single-table OTP records, constant-time compare, TTL (matches `magj-dev` shape).
- `cognito-client-only — server OTP missing` — only client-side Cognito wiring (matches `blogmarks` shape).
- `none` — no OTP infrastructure detected.

### Sample output

```
ts-otp-aws audit  ::  /home/kayaman/Projects/ai-assisted-dev

Cognito CUSTOM_AUTH triggers:
  [x] AuthFlow: CUSTOM_AUTH
  [x] DefineAuthChallenge handler
  [x] CreateAuthChallenge handler
  [x] VerifyAuthChallengeResponse handler
  [x] PreSignUp handler
  [ ] prevent_user_existence_errors (Terraform)

Messaging channels:
  [x] SES SDK imported
  [x] SES SendEmailCommand used
  [x] SES_FROM env var referenced
  [x] SNS SDK imported
  [x] SNS PublishCommand used
  ...

Verdict: cognito-custom-auth — complete
```

### Exit codes

| Code | Meaning |
|---|---|
| 0 | Audit ran (regardless of verdict) |
| 1 | Bad invocation (missing arg or path is not a directory) |
| 2 | `ripgrep` (`rg`) is not installed |

### Requirements

- `bash` 4+
- `ripgrep` (`rg`) — Arch: `pacman -S ripgrep`, Debian/Ubuntu: `apt install ripgrep`, macOS: `brew install ripgrep`.

The script never writes to the target repo; it only `rg`-greps under the root, skipping `node_modules`, `dist`, `build`, `.next`, `.turbo`.
