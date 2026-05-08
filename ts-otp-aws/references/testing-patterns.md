# Testing patterns

Load this when writing or fixing tests for OTP handlers. Pattern source: `ai-assisted-dev/lambda/auth-triggers/src/__tests__/`.

## Stack

- **Vitest** as the runner. Node environment.
- **`aws-sdk-client-mock` v4** as the SDK mock. One `mockClient(X)` per AWS service used.
- **No LocalStack** for unit-level coverage. LocalStack is reserved for integration tests if you choose to add them later — overkill for the OTP path.

## File layout

```
lambda/auth-triggers/
├── src/
│   ├── handlers/
│   │   ├── create-challenge.ts
│   │   ├── define-challenge.ts
│   │   ├── verify-challenge.ts
│   │   └── pre-signup.ts
│   ├── notifiers/
│   │   ├── email.ts
│   │   └── sms.ts
│   ├── handler.ts
│   └── __tests__/
│       ├── create-challenge.test.ts
│       ├── define-challenge.test.ts
│       └── verify-challenge.test.ts
└── package.json
```

## `aws-sdk-client-mock` recipe

```ts
import { SESv2Client, SendEmailCommand } from "@aws-sdk/client-sesv2";
import { PublishCommand, SNSClient } from "@aws-sdk/client-sns";
import { mockClient } from "aws-sdk-client-mock";
import { afterEach, beforeEach, describe, expect, it } from "vitest";
import { createChallenge } from "../handlers/create-challenge.js";

const sesMock = mockClient(SESv2Client);
const snsMock = mockClient(SNSClient);

beforeEach(() => {
  sesMock.reset();
  snsMock.reset();
  sesMock.on(SendEmailCommand).resolves({});
  snsMock.on(PublishCommand).resolves({ MessageId: "x" });
  process.env["SES_FROM"] = "noreply@example.com";
});
afterEach(() => {
  delete process.env["SES_FROM"];
});
```

`mockClient` intercepts every command sent through the SDK constructor — both eager and lazy-singleton patterns work without changes.

## Event factories

The Cognito trigger event types are large. A factory keeps tests readable:

```ts
import type { CreateAuthChallengeTriggerEvent } from "aws-lambda";

const baseEvent = (
  channel: "email" | "sms" | undefined,
  opts: { userNotFound?: boolean } = {},
): CreateAuthChallengeTriggerEvent =>
  ({
    version: "1",
    region: "us-east-1",
    userPoolId: "pool",
    userName: "u",
    callerContext: { awsSdkVersion: "x", clientId: "c" },
    triggerSource: "CreateAuthChallenge_Authentication",
    request: {
      userAttributes: opts.userNotFound
        ? {}
        : { email: "test@example.com", phone_number: "+15551234567" },
      challengeName: "CUSTOM_CHALLENGE",
      session: [],
      userNotFound: opts.userNotFound ?? false,
      ...(channel ? { clientMetadata: { channel } } : {}),
    },
    response: {
      publicChallengeParameters: {},
      privateChallengeParameters: {},
      challengeMetadata: "",
    },
  }) as unknown as CreateAuthChallengeTriggerEvent;
```

The `as unknown as` cast bypasses Cognito's wide event type — the factory only sets the fields the handler reads.

## What to assert

### `create-challenge.test.ts`

- Channel branching: `channel=email` triggers `SendEmailCommand` exactly once, no `PublishCommand`.
- Channel branching: `channel=sms` triggers `PublishCommand` exactly once, no `SendEmailCommand`.
- Default to `email` when `clientMetadata.channel` is missing.
- **Phantom-user safety**: `userNotFound=true` produces zero sends but still returns a synthetic challenge (`privateChallengeParameters.code` matches `/^\d{6}$/`).
- The `code` is 6 digits and stored under `privateChallengeParameters` (not `publicChallengeParameters`).

### `define-challenge.test.ts`

State-machine table tests covering:

| Session | Last result | Expected response |
|---|---|---|
| `[]` | — | `challengeName=CUSTOM_CHALLENGE`, no tokens |
| `[CUSTOM_CHALLENGE: true]` | correct | `issueTokens=true` |
| `[CUSTOM_CHALLENGE: false]` | wrong, length 1 | another `CUSTOM_CHALLENGE` |
| `[wrong, wrong, wrong]` | wrong, length 3 | `failAuthentication=true` |

### `verify-challenge.test.ts`

- Correct code → `answerCorrect=true`.
- Wrong code (same length) → `answerCorrect=false`.
- Non-numeric / wrong-length input → `answerCorrect=false` without invoking the comparator.
- `OTP_DEV_BYPASS=1` + `000000` → `answerCorrect=true`. Without the env var, `000000` should fail (unless coincidentally the issued OTP).

## Custom-path tests (DynamoDB)

When testing the no-Cognito flow, mock `DynamoDBClient` (or `DynamoDBDocumentClient`):

```ts
import { DynamoDBClient } from "@aws-sdk/client-dynamodb";
import { UpdateItemCommand, PutItemCommand, DeleteItemCommand } from "@aws-sdk/client-dynamodb";
import { mockClient } from "aws-sdk-client-mock";

const ddbMock = mockClient(DynamoDBClient);

beforeEach(() => {
  ddbMock.reset();
  ddbMock.on(UpdateItemCommand).resolves({ Attributes: { count: { N: "1" } } });
  ddbMock.on(PutItemCommand).resolves({});
  ddbMock.on(DeleteItemCommand).resolves({});
});
```

Drive each branch (rate-limit hit, expired OTP, attempt cap exceeded) by changing the `Attributes` returned from `UpdateItemCommand` to simulate the conditional outcome. The `ConditionExpression` failure path is tested by rejecting with a `ConditionalCheckFailedException`-shaped error.

## Coverage targets

- Each handler ≥ 90% line coverage.
- Both channel branches AND the phantom-user branch must have explicit tests — these are the high-blast-radius paths.
- The dispatcher (`handler.ts`) has at most a smoke test asserting unknown trigger sources throw.

## Integration / contract tests (optional)

If the project has the budget for it:

- One test per environment that calls `InitiateAuthCommand` → asserts a session is returned → calls `RespondToAuthChallengeCommand` with `OTP_DEV_BYPASS=1` and `000000` → asserts tokens. Run against a dedicated dev user pool.
- DynamoDB integration via a test table created/destroyed per CI run, behind a feature flag.

## Sources

- ai-assisted-dev internal: `lambda/auth-triggers/src/__tests__/create-challenge.test.ts` is the canonical example bundled here.
- *Production-Ready Serverless* — Cui & Tankersley — Lambda testing strategies, mock-vs-localstack tradeoffs.
