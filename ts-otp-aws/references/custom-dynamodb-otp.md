# Custom DynamoDB OTP (no Cognito)

Load this when the project doesn't use Cognito or the user explicitly chose the custom path. Pattern adapted from `magj-dev/lambda/src/auth/handler.ts`.

## Single-table layout

One DynamoDB table, on-demand billing, TTL on `ttl`. See `assets/terraform/dynamodb-otp-table.tf` and `assets/schemas/otp-record.schema.json`.

| Item kind | PK | SK | Attributes |
|---|---|---|---|
| OTP record | `otp#<sha256(identifier)>` | `pending` | `otpHash` (sha256 of code), `attempts` (N), `ttl` (N, epoch s, +300), `createdAt` |
| Rate-limit counter | `otp#<sha256(identifier)>` | `rate#<hour-bucket>` | `count` (N), `ttl` (N, +3600) |

`identifier` is the normalized email or E.164 phone. Hashing keeps PII out of the partition key. One identifier maps to one OTP item — issuing a new OTP overwrites the old (`PutItem`, no condition). The rate-limit counter prevents > N issuances per hour.

## Constants (recommended defaults)

```ts
const OTP_TTL_SECONDS = 300;       // 5 minutes
const MAX_OTP_ATTEMPTS = 3;        // per OTP record
const MAX_OTP_PER_HOUR = 3;        // per identifier
const CODE_LENGTH = 6;             // 6 digits
```

## Generation + storage

```ts
import { randomInt, createHash, timingSafeEqual } from "node:crypto";

const generateOtp = (): string =>
  randomInt(0, 1_000_000).toString().padStart(6, "0");

const hashOtp = (code: string, salt: string): string =>
  createHash("sha256").update(`${salt}:${code}`).digest("hex");

const normIdentifier = (raw: string): string => {
  if (raw.includes("@")) return raw.trim().toLowerCase();
  return raw.replace(/[^\d+]/g, ""); // expect E.164 already
};

const idHash = (id: string): string =>
  createHash("sha256").update(normIdentifier(id)).digest("hex");
```

Salt the OTP hash with a per-deployment secret pulled from Secrets Manager (see `magj-dev/lambda/src/shared/secrets.ts` for the cached-fetch pattern). Storing the **hash** rather than the code limits damage if the table is ever exfiltrated.

## Issue endpoint (POST /otp/start)

Pseudocode:

```ts
const id = normIdentifier(req.body.identifier);
const pk = `otp#${idHash(id)}`;

// 1. rate-limit
const hourBucket = Math.floor(Date.now() / 3_600_000);
const rate = await ddb.send(new UpdateItemCommand({
  TableName: TBL,
  Key: { PK: { S: pk }, SK: { S: `rate#${hourBucket}` } },
  UpdateExpression: "ADD #c :one SET #ttl = if_not_exists(#ttl, :exp)",
  ExpressionAttributeNames: { "#c": "count", "#ttl": "ttl" },
  ExpressionAttributeValues: {
    ":one": { N: "1" },
    ":exp": { N: String(Math.floor(Date.now()/1000) + 3600) },
  },
  ReturnValues: "ALL_NEW",
}));
if (Number(rate.Attributes!.count.N) > MAX_OTP_PER_HOUR) {
  return resp200({ ok: true }); // do NOT leak rate-limit state
}

// 2. issue + send (silent on unknown identifier — same return shape)
const code = generateOtp();
await ddb.send(new PutItemCommand({
  TableName: TBL,
  Item: {
    PK: { S: pk },
    SK: { S: "pending" },
    otpHash: { S: hashOtp(code, OTP_SALT) },
    attempts: { N: "0" },
    ttl: { N: String(Math.floor(Date.now()/1000) + OTP_TTL_SECONDS) },
    createdAt: { S: new Date().toISOString() },
  },
}));
if (id.includes("@")) await sendOtpEmail(id, code);
else await sendOtpSms(id, code);

return resp200({ ok: true });
```

The endpoint always returns `{ ok: true }` for any well-formed identifier — no signal about whether a user actually exists, whether the code was sent, or whether the rate limit hit. The frontend instructs the user to check their inbox / messages.

## Verify endpoint (POST /otp/verify)

```ts
const id = normIdentifier(req.body.identifier);
const code = req.body.code;
if (!/^\d{6}$/.test(code)) return resp401();

const pk = `otp#${idHash(id)}`;
// Atomic increment of attempts so two parallel guesses can't both pass
const u = await ddb.send(new UpdateItemCommand({
  TableName: TBL,
  Key: { PK: { S: pk }, SK: { S: "pending" } },
  UpdateExpression: "ADD attempts :one",
  ExpressionAttributeValues: { ":one": { N: "1" } },
  ConditionExpression: "attribute_exists(PK) AND #ttl > :now AND attempts < :max",
  ExpressionAttributeNames: { "#ttl": "ttl" },
  ExpressionAttributeValues: {
    ":one": { N: "1" },
    ":now": { N: String(Math.floor(Date.now()/1000)) },
    ":max": { N: String(MAX_OTP_ATTEMPTS) },
  },
  ReturnValues: "ALL_NEW",
})).catch(() => null);

if (!u) return resp401(); // expired, missing, or over cap

const stored = u.Attributes!.otpHash.S!;
const guess = hashOtp(code, OTP_SALT);
if (!constantEq(stored, guess)) return resp401();

// success — single-use: delete the record
await ddb.send(new DeleteItemCommand({
  TableName: TBL,
  Key: { PK: { S: pk }, SK: { S: "pending" } },
}));

return resp200({ token: signJwt(id) });
```

Key ideas:

- `ConditionExpression` enforces TTL freshness and the attempt cap server-side, so two parallel guesses can't both bypass.
- `attempts` is incremented **before** the comparison, so even a constant-time win still costs one attempt.
- On success, delete the record — single-use.
- Hashes compared, not codes; constant-time even though both sides are hex.

## JWT issuance

Out of scope for this skill in detail — pick `jose` or `aws-jwt-verify`-friendly signing. Sign with a key in Secrets Manager or KMS-backed signer (`KMS Sign API`, `RSASSA_PKCS1_V1_5_SHA_256` for portability with JWKS consumers).

## IAM

Lambda execution role gets:

```json
["dynamodb:GetItem","dynamodb:PutItem","dynamodb:UpdateItem","dynamodb:DeleteItem"]
```

scoped to the table ARN, plus `ses:SendEmail` and `sns:Publish`. See `assets/iam/custom-otp-policy.json` and replace the
`REPLACE_WITH_*` placeholders with your table ARN and verified sender.

## Sources

- *Serverless Development on AWS* — Brisals & Hedger — single-table patterns.
- *Real-World Cryptography* — Wong — HMAC, salt, constant-time compare.
- magj-dev internal: `lambda/src/auth/handler.ts`, `lambda/src/auth/admin-mfa-store.ts`, `terraform/dynamodb.tf` — pattern source.
