# DynamoDB single-table for the custom (no-Cognito) OTP path. Adapted from
# magj-dev/terraform/dynamodb.tf and ai-assisted-dev/infra/terraform/modules/data/main.tf.
#
# Only used on the custom path. If you're on the Cognito CUSTOM_AUTH path,
# Cognito holds the challenge state and this file is unused — delete it.

variable "name_prefix" { type = string }
variable "tags" {
  type    = map(string)
  default = {}
}

resource "aws_dynamodb_table" "otp" {
  name         = "${var.name_prefix}-otp"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "PK"
  range_key    = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }

  point_in_time_recovery {
    enabled = true
  }

  deletion_protection_enabled = true

  server_side_encryption {
    enabled = true
  }

  tags = var.tags
}

output "otp_table_name" { value = aws_dynamodb_table.otp.name }
output "otp_table_arn" { value = aws_dynamodb_table.otp.arn }
