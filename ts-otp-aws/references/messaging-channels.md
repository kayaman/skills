# Messaging channels: SES (email) and SNS (SMS)

Load this when tuning deliverability, debugging sandbox/spend errors, or expanding to new countries.

## SES (email)

### Sandbox vs production

A new SES account starts in **sandbox**: only verified addresses can receive, 200 emails/day, 1 email/second. For real OTP traffic you must request **production access** in the AWS console (Account → Request production access). Until then, every recipient must be a verified identity.

| Symptom | Fix |
|---|---|
| `MessageRejected: Email address is not verified. The following identities failed the check in region us-east-1: noreply@x.com` | The `FromEmailAddress` (`SES_FROM`) is not a verified identity in this region. |
| `MailFromDomainNotVerified` | Domain identity created but DKIM/MAIL FROM not configured. Set `MAIL FROM` subdomain (e.g. `bounce.x.com`) and SPF/DKIM records. |
| Going to spam folder | Enable DKIM, set DMARC `p=none` initially, warm up the domain (don't blast 10k from a cold IP). Custom MAIL FROM domain helps SPF alignment. |
| `Throttling` | SES quota — request rate limit increase. Default fresh quota is low. |

### Recommended setup (Terraform-shaped)

- **Domain identity** (not address identity) — lets you send from any local-part.
- **DKIM** — `aws_sesv2_email_identity` with `dkim_signing_attributes`, then create the 3 CNAME records in Route 53.
- **MAIL FROM domain** — `aws_sesv2_email_identity_mail_from_attributes` pointing at `bounce.<your-domain>`.
- **SPF** — TXT `v=spf1 include:amazonses.com -all` on the MAIL FROM subdomain.
- **DMARC** — TXT `v=DMARC1; p=none; rua=mailto:dmarc@yourdomain.com` initially; tighten to `quarantine`/`reject` after monitoring.

### What goes in the email

- **Subject** is short and unique: `Your sign-in code` (not `OTP for foo`). Prevents collapsing in inbox threads.
- **Body** is plaintext-first: code, expiry, "ignore if not you" line, sender brand. HTML is optional and adds bounce risk.
- **Never** include a clickable login link in the same email as the code (that's a magic-link, different threat model).
- **Subject** must NOT contain the code (some clients show subjects in notifications without auth context).

## SNS (SMS)

### Spending guardrails

`MonthlySpendLimit` on `aws_sns_sms_preferences` — start at $50 USD and raise as you confirm legitimate volume. Without this, a brute-force start-OTP loop can run up four-figure bills in minutes (a.k.a. SMS pumping / toll fraud).

```hcl
resource "aws_sns_sms_preferences" "default" {
  monthly_spend_limit = 50
  default_sms_type    = "Transactional"
  default_sender_id   = "OTP"
}
```

### `SMSType=Transactional`

Always set on OTP messages (the bundled `sms.ts` does):

```ts
MessageAttributes: {
  "AWS.SNS.SMS.SMSType":  { DataType: "String", StringValue: "Transactional" },
  "AWS.SNS.SMS.SenderID": { DataType: "String", StringValue: "OTP" },
}
```

`Promotional` messages can be silently dropped by carriers; `Transactional` has higher priority and price.

### Country-specific gotchas

| Region | Constraint |
|---|---|
| **United States** | 10DLC registration required for high-volume sending. Use a dedicated origination number registered with the carrier; long-codes alone get heavily filtered. |
| **India** | DLT registration (TRAI) — sender ID + template registered in advance. Unregistered messages are dropped. |
| **EU / UK** | Sender ID accepted; regulatory-driven preferences vary by country. |
| **Brazil** | Short-codes regulated; sender ID generally accepted but may be replaced by carrier. |
| **China, Vietnam** | Origination identity required; templates must be pre-approved. |

If you're shipping outside one or two known countries, prefer email by default and require an explicit opt-in for SMS.

### Origination identities & sender ID

`SenderID` is a cosmetic 3–11 alphanumeric string shown to the recipient on supported networks. On unsupported networks (US, Canada) it's ignored; the recipient sees the long-code or short-code. Don't rely on `SenderID` for trust.

For US production traffic, register a 10DLC campaign and provision an origination number; reference it via `OriginationIdentity` on `PublishCommand` for deterministic routing.

### Opt-out

SNS auto-handles `STOP` keywords and adds the number to the per-account opt-out list. Subsequent publishes fail with `OptedOut` — surface this as a generic "we couldn't send a code" message; never tell the user they're opted out (account enumeration).

## When **not** to use Pinpoint

Pinpoint sits a layer above SES + SNS and adds campaigns, A/B testing, segmentation, push notifications. **Don't** use it for transactional OTP — it's overkill, costs more, and conflates marketing concerns with auth. SES + SNS direct is the right primitive.

## Internationalization

- Localize subject + body via a small lookup keyed on user locale (Cognito stores `locale` attribute; custom path stores it in your user record).
- The 6-digit code is locale-free; the surrounding prose is what changes.
- Right-to-left languages: ensure your email template's `dir="rtl"` and that the digits render LTR (Unicode bidi handles this automatically for Arabic-Indic numerals).

## Sources

- *AWS Security Cookbook 2e* — Kanikathottu — SES + SNS hardening.
- *AWS for Solutions Architects 3e* — Shrivastava et al. — messaging service selection.
- AWS docs — SES sending authorization, SNS SMS attributes (linked in `citations.md`).
