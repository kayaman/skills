# Citations

Books and primary sources this skill draws from. Cite these by **title, author(s), and O'Reilly Media** (or original publisher) when emitting write-ups based on this skill, per the O'Reilly attribution policy.

## Books (O'Reilly + partner publishers)

- **Sheen Brisals & Luke Hedger** — *Serverless Development on AWS: Building Enterprise-Scale Serverless Solutions* (O'Reilly Media). Passwordless authentication appendix is the canonical reference for the Cognito `CUSTOM_AUTH` pattern this skill defaults to.
- **Heartin Kanikathottu** — *AWS Security Cookbook, 2nd Edition* (Packt, distributed via O'Reilly). Cognito User Pool hardening, Lambda trigger recipes, IAM scoping for auth flows.
- **Laurent Mathieu** — *Mastering AWS Security, 2nd Edition* (Packt, via O'Reilly). Cognito advanced configuration, identity federation, Cognito-vs-IAM trade-offs.
- **Jayanth Kumar & Mandeep Singh** — *System Design on AWS* (O'Reilly Media). Authentication chapter — building blocks comparison and decision matrix at a system-design level.
- **David Wong** — *Real-World Cryptography* (Manning, via O'Reilly). HMAC, salt, constant-time comparison, TOTP/HOTP protocol grounding. The authoritative source for "why `timingSafeEqual` and not `===`".
- **Saurabh Shrivastava, Neelanjali Srivastav, & Dhiraj Thakur** — *AWS for Solutions Architects, 3rd Edition* (Packt, via O'Reilly). SES/SNS/Pinpoint selection and serverless architecture context.
- **Yan Cui & Cody Tankersley** — *Production-Ready Serverless* (O'Reilly Media, video). Lambda testing strategy, `aws-sdk-client-mock` vs LocalStack vs integration tests.
- **Dylan Shields** — *AWS Security* (Manning, via O'Reilly). Defense-in-depth on Cognito and IAM, complementary to Mathieu.

## AWS official documentation (referenced inline)

- AWS Cognito User Pools — Custom authentication challenge Lambda triggers.
- AWS SES (v2) — Domain identity, DKIM, MAIL FROM, sandbox, sending statistics.
- AWS SNS — SMS attributes (`SMSType`, `SenderID`, `OriginationIdentity`), spending limits, opt-out lists, 10DLC for US.
- AWS DynamoDB — TTL semantics, condition expressions, on-demand billing.

## Internal pattern sources (your projects)

- `ai-assisted-dev/lambda/auth-triggers/` — production-ready Cognito CUSTOM_AUTH OTP flow; assets in this skill are taken verbatim with attribution.
- `magj-dev/lambda/src/auth/` — non-Cognito DynamoDB OTP gate; pattern source for `references/custom-dynamodb-otp.md` and the second-factor sketch.
- `blogmarks/src/components/OtpCodeInput.tsx` — reference UI component (not bundled in this skill).

## Citation format examples

When writing a blog post or PR description that draws from this skill:

> The Cognito CUSTOM_AUTH pattern in this implementation follows the passwordless authentication recipe in *Serverless Development on AWS* (Sheen Brisals & Luke Hedger, O'Reilly Media), adapted for production use with phantom-user safety per the Cognito documentation.

> Constant-time OTP comparison uses `crypto.timingSafeEqual` as recommended in *Real-World Cryptography* (David Wong, Manning, via O'Reilly Media).

When the cited material informs an architectural decision:

> Per *AWS Security Cookbook, 2nd Edition* (Heartin Kanikathottu, Packt, via O'Reilly Media), the user pool is configured with `prevent_user_existence_errors = ENABLED` to defend against account enumeration.

Always include the publisher (O'Reilly Media or partner via O'Reilly Media). The O'Reilly platform license requires attribution when content is sourced from books on the platform.
