# Cognito user pool configured for passwordless OTP via the four CUSTOM_AUTH
# triggers. Adjust variable names to match your project's Terraform conventions.

variable "name_prefix" { type = string }
variable "auth_triggers_lambda_arn" {
  description = "ARN of the Lambda function that dispatches all four CUSTOM_AUTH triggers."
  type        = string
}
variable "tags" {
  type    = map(string)
  default = {}
}

resource "aws_cognito_user_pool" "this" {
  name = "${var.name_prefix}-users"

  # Username is the email — required so passwordless flows can address users
  # consistently across email/SMS channels via ListUsers.
  username_attributes      = ["email"]
  auto_verified_attributes = ["email", "phone_number"]

  password_policy {
    minimum_length    = 8
    require_lowercase = false
    require_uppercase = false
    require_numbers   = false
    require_symbols   = false
  }

  schema {
    name                = "email"
    attribute_data_type = "String"
    required            = true
    mutable             = true
  }

  schema {
    name                = "phone_number"
    attribute_data_type = "String"
    required            = false
    mutable             = true
  }

  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  lambda_config {
    pre_sign_up                    = var.auth_triggers_lambda_arn
    define_auth_challenge          = var.auth_triggers_lambda_arn
    create_auth_challenge          = var.auth_triggers_lambda_arn
    verify_auth_challenge_response = var.auth_triggers_lambda_arn
  }

  tags = var.tags
}

resource "aws_cognito_user_pool_client" "this" {
  name         = "${var.name_prefix}-app"
  user_pool_id = aws_cognito_user_pool.this.id

  # CUSTOM_AUTH must be in the explicit auth flows list, USER_PASSWORD must NOT.
  explicit_auth_flows = [
    "ALLOW_CUSTOM_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
  ]

  # Defends against account enumeration. Combined with the phantom-user safe
  # path in create-challenge, the API does not leak whether an identifier
  # corresponds to a real user.
  prevent_user_existence_errors = "ENABLED"

  generate_secret = false

  refresh_token_validity = 30
  access_token_validity  = 1
  id_token_validity      = 1
  token_validity_units {
    refresh_token = "days"
    access_token  = "hours"
    id_token      = "hours"
  }
}

resource "aws_lambda_permission" "cognito_invoke" {
  statement_id  = "AllowCognitoUserPoolInvoke"
  action        = "lambda:InvokeFunction"
  function_name = var.auth_triggers_lambda_arn
  principal     = "cognito-idp.amazonaws.com"
  source_arn    = aws_cognito_user_pool.this.arn
}

output "user_pool_id" { value = aws_cognito_user_pool.this.id }
output "user_pool_arn" { value = aws_cognito_user_pool.this.arn }
output "client_id" { value = aws_cognito_user_pool_client.this.id }
