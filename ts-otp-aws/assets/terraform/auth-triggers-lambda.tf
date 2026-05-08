# auth-triggers Lambda: a single Node 22 ESM function that dispatches all four
# Cognito CUSTOM_AUTH triggers. The frontend never invokes this directly —
# Cognito is the only caller (via the lambda_config block on the user pool).

variable "name_prefix" { type = string }
variable "lambda_zip" {
  description = "Path to the prebuilt ESM bundle (handler.js + bundled deps)."
  type        = string
}
variable "ses_from" {
  description = "Verified SES identity used as the From address for OTP emails."
  type        = string
}
variable "sms_sender_id" {
  description = "3-11 alphanumeric SMS sender ID. Cosmetic on networks that honor it."
  type        = string
  default     = "OTP"
}
variable "app_name" {
  description = "Brand string used in OTP email/SMS bodies."
  type        = string
}
variable "log_retention_days" {
  type    = number
  default = 14
}
variable "tags" {
  type    = map(string)
  default = {}
}

data "aws_iam_policy_document" "lambda_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "auth_triggers" {
  name               = "${var.name_prefix}-auth-triggers"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
  tags               = var.tags
}

resource "aws_iam_role_policy_attachment" "lambda_basic" {
  role       = aws_iam_role.auth_triggers.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy" "auth_triggers_inline" {
  name = "auth-triggers-channels"
  role = aws_iam_role.auth_triggers.id
  # Render the policy template from the sibling assets/iam directory so
  # placeholders like ${SES_FROM} are substituted before applying.
  policy = templatefile("${path.module}/../iam/auth-trigger-policy.json", {
    SES_FROM = var.ses_from
  })
}

resource "aws_lambda_function" "auth_triggers" {
  function_name = "${var.name_prefix}-auth-triggers"
  role          = aws_iam_role.auth_triggers.arn
  filename      = var.lambda_zip
  handler       = "handler.handler"
  runtime       = "nodejs22.x"
  timeout       = 10
  memory_size   = 512
  architectures = ["arm64"]

  source_code_hash = filebase64sha256(var.lambda_zip)

  environment {
    variables = {
      SES_FROM      = var.ses_from
      SMS_SENDER_ID = var.sms_sender_id
      APP_NAME      = var.app_name
      # OTP_DEV_BYPASS intentionally omitted — set only in dev workspaces, never here.
    }
  }

  tags = var.tags
}

resource "aws_cloudwatch_log_group" "auth_triggers" {
  name              = "/aws/lambda/${aws_lambda_function.auth_triggers.function_name}"
  retention_in_days = var.log_retention_days
  tags              = var.tags
}

output "auth_triggers_lambda_arn" { value = aws_lambda_function.auth_triggers.arn }
output "auth_triggers_role_arn" { value = aws_iam_role.auth_triggers.arn }
