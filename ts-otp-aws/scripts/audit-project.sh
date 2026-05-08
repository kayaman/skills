#!/usr/bin/env bash
# audit-project.sh — detect OTP-related patterns in a TypeScript/AWS repo and print a punch list.
#
# Usage: audit-project.sh <repo-root>
# Exits 0 on clean run, 2 if ripgrep is missing, 1 on bad invocation.

set -uo pipefail

usage() {
  cat <<'EOF'
Usage: audit-project.sh <repo-root>

Audits a TypeScript/AWS repository for OTP / passwordless-auth patterns and
prints a punch list grouped by category. Detects which of the canonical
shapes the repo most resembles:

  - cognito-custom-auth   (ai-assisted-dev style)
  - custom-dynamodb-otp   (magj-dev style)
  - cognito-client-only   (blogmarks style)
  - none

Requires: ripgrep (rg). Read-only — never modifies the target repo.
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ $# -ne 1 ]]; then
  usage
  exit 1
fi

ROOT="$1"
if [[ ! -d "$ROOT" ]]; then
  echo "error: '$ROOT' is not a directory" >&2
  exit 1
fi

if ! command -v rg >/dev/null 2>&1; then
  echo "error: ripgrep (rg) is required. Install via your package manager." >&2
  exit 2
fi

# Helper: count matches across the repo for a regex, ignoring node_modules + dist.
count() {
  rg --no-messages -c --type-add 'code:*.{ts,tsx,js,mjs,cjs,tf,json}' --type code \
     --glob '!node_modules' --glob '!dist' --glob '!build' --glob '!.next' --glob '!.turbo' \
     -- "$1" "$ROOT" 2>/dev/null | awk -F: '{s+=$NF} END{print s+0}'
}

# Helper: did we see *any* match?
seen() {
  [[ "$(count "$1")" -gt 0 ]] && echo "yes" || echo "no"
}

# Helper: pretty row.
row() {
  local label="$1"
  local present="$2"
  local marker
  case "$present" in
    yes) marker="[x]" ;;
    no)  marker="[ ]" ;;
    *)   marker="[?]" ;;
  esac
  printf "  %s %s\n" "$marker" "$label"
}

echo "ts-otp-aws audit  ::  $ROOT"
echo

# --- Cognito CUSTOM_AUTH signals ---
COG_CUSTOM_AUTH=$(seen 'CUSTOM_AUTH')
COG_DEFINE=$(seen 'DefineAuthChallenge')
COG_CREATE=$(seen 'CreateAuthChallenge')
COG_VERIFY=$(seen 'VerifyAuthChallengeResponse')
COG_PRESIGN=$(seen 'PreSignUp_(SignUp|AdminCreateUser|ExternalProvider)')
COG_PREVENT_LEAK=$(seen 'prevent_user_existence_errors')

echo "Cognito CUSTOM_AUTH triggers:"
row "AuthFlow: CUSTOM_AUTH"                         "$COG_CUSTOM_AUTH"
row "DefineAuthChallenge handler"                   "$COG_DEFINE"
row "CreateAuthChallenge handler"                   "$COG_CREATE"
row "VerifyAuthChallengeResponse handler"           "$COG_VERIFY"
row "PreSignUp handler"                             "$COG_PRESIGN"
row "prevent_user_existence_errors (Terraform)"     "$COG_PREVENT_LEAK"
echo

# --- Channel signals (SES + SNS) ---
SES_CLIENT=$(seen '@aws-sdk/client-sesv2|@aws-sdk/client-ses')
SES_SEND=$(seen 'SendEmailCommand')
SES_FROM=$(seen 'SES_FROM')
SNS_CLIENT=$(seen '@aws-sdk/client-sns')
SNS_PUBLISH=$(seen 'PublishCommand')
SNS_TYPE=$(seen 'AWS\.SNS\.SMS\.SMSType')
SNS_SENDER=$(seen 'AWS\.SNS\.SMS\.SenderID')
SNS_SPEND=$(seen 'monthly_spend_limit|MonthlySpendLimit')

echo "Messaging channels:"
row "SES SDK imported"                              "$SES_CLIENT"
row "SES SendEmailCommand used"                     "$SES_SEND"
row "SES_FROM env var referenced"                   "$SES_FROM"
row "SNS SDK imported"                              "$SNS_CLIENT"
row "SNS PublishCommand used"                       "$SNS_PUBLISH"
row "SMSType=Transactional set"                     "$SNS_TYPE"
row "SenderID set"                                  "$SNS_SENDER"
row "SNS monthly spend limit configured"            "$SNS_SPEND"
echo

# --- DynamoDB OTP signals ---
DDB_TTL=$(seen 'attribute_name *= *"ttl"|TTL.*ttl')
DDB_PK_SK=$(seen 'hash_key *= *"PK"')
DDB_OTP_NAMING=$(seen 'otp#|OTP_TTL_SECONDS|MAX_OTP_ATTEMPTS|MAX_OTP_PER_HOUR')

echo "DynamoDB OTP storage:"
row "TTL attribute configured (Terraform)"          "$DDB_TTL"
row "Single-table PK/SK pattern"                    "$DDB_PK_SK"
row "OTP-related constants or PK prefix"            "$DDB_OTP_NAMING"
echo

# --- Security primitives ---
SEC_TIMING=$(seen 'timingSafeEqual')
SEC_RANDOM_INT=$(seen 'randomInt')
SEC_DEV_BYPASS=$(seen 'OTP_DEV_BYPASS|AAD_DEV_OTP_BYPASS')

echo "Security primitives:"
row "constant-time comparison (timingSafeEqual)"    "$SEC_TIMING"
row "crypto.randomInt for OTP generation"           "$SEC_RANDOM_INT"
row "dev-bypass flag (non-prod only)"               "$SEC_DEV_BYPASS"
echo

# --- Testing ---
TEST_MOCK=$(seen 'aws-sdk-client-mock')
TEST_VITEST=$(seen 'from ["'"'"']vitest["'"'"']')

echo "Testing:"
row "aws-sdk-client-mock present"                   "$TEST_MOCK"
row "Vitest test runner"                            "$TEST_VITEST"
echo

# --- Frontend/UI ---
UI_OTP_INPUT=$(seen 'autocomplete="one-time-code"|OtpCodeInput')
UI_INITIATE=$(seen 'InitiateAuthCommand')
UI_RESPOND=$(seen 'RespondToAuthChallengeCommand')

echo "Frontend integration:"
row "OTP input UI component"                        "$UI_OTP_INPUT"
row "InitiateAuthCommand call site"                 "$UI_INITIATE"
row "RespondToAuthChallengeCommand call site"       "$UI_RESPOND"
echo

# --- Verdict ---
verdict() {
  if [[ "$COG_DEFINE" == "yes" && "$COG_CREATE" == "yes" && "$COG_VERIFY" == "yes" ]]; then
    if [[ "$SES_SEND" == "yes" || "$SNS_PUBLISH" == "yes" ]]; then
      echo "cognito-custom-auth — complete"
      return
    fi
    echo "cognito-custom-auth — partial (handlers present, channel delivery missing)"
    return
  fi
  # Custom-DDB shape: OTP constants/PK + (SES or SNS) + DDB TTL + randomInt
  if [[ "$DDB_OTP_NAMING" == "yes" && "$DDB_TTL" == "yes" && "$SEC_RANDOM_INT" == "yes" \
       && ( "$SES_SEND" == "yes" || "$SNS_PUBLISH" == "yes" ) ]]; then
    if [[ "$SEC_TIMING" == "yes" ]]; then
      echo "custom-dynamodb-otp — complete"
    else
      echo "custom-dynamodb-otp — partial (missing constant-time comparison)"
    fi
    return
  fi
  if [[ "$UI_INITIATE" == "yes" || "$UI_OTP_INPUT" == "yes" ]]; then
    echo "cognito-client-only — server OTP missing"
    return
  fi
  echo "none — start with assets/handlers/* and assets/terraform/* in the ts-otp-aws skill"
}

echo "Verdict: $(verdict)"
echo
echo "Next steps:"
case "$(verdict)" in
  cognito-custom-auth*complete*)
    echo "  - Review references/security-checklist.md before production cutover."
    echo "  - Confirm SES out of sandbox and SNS spend limit are in place."
    ;;
  cognito-custom-auth*partial*)
    echo "  - Wire SES/SNS notifiers (assets/notifiers/email.ts, sms.ts)."
    echo "  - Set SES_FROM and SMS_SENDER_ID env vars on the auth-triggers Lambda."
    ;;
  custom-dynamodb-otp*partial*)
    echo "  - Replace direct string equality with crypto.timingSafeEqual for OTP/hash comparison."
    echo "  - See references/security-checklist.md and references/custom-dynamodb-otp.md."
    ;;
  custom-dynamodb-otp*complete*)
    echo "  - Verify rate limit and attempt cap are enforced server-side via ConditionExpression."
    echo "  - Check the OTP record is deleted on successful verify."
    ;;
  cognito-client-only*)
    echo "  - Add the four CUSTOM_AUTH triggers from assets/handlers/."
    echo "  - Wire them into the user pool via assets/terraform/cognito-userpool.tf."
    echo "  - Add notifiers (SES + SNS) and Terraform identity setup."
    ;;
  *)
    echo "  - Decide Cognito vs custom (see references/architecture-decision.md)."
    echo "  - Default: copy assets/handlers/* + assets/notifiers/* and apply assets/terraform/*."
    ;;
esac
