# SNS account-wide SMS preferences. Without a spending limit, a brute-force
# loop on the OTP-start endpoint can run up four-figure bills in minutes
# (a.k.a. SMS pumping). Start conservative and raise as legitimate volume
# justifies.

variable "sms_monthly_spend_limit_usd" {
  description = "Hard cap on SMS spend per month, in whole USD."
  type        = number
  default     = 50
}
variable "sms_default_sender_id" {
  description = "Default 3-11 alphanumeric sender ID used when PublishCommand omits one."
  type        = string
  default     = "OTP"
}

resource "aws_sns_sms_preferences" "default" {
  monthly_spend_limit            = var.sms_monthly_spend_limit_usd
  default_sms_type               = "Transactional"
  default_sender_id              = var.sms_default_sender_id
  delivery_status_iam_role_arn   = null
  delivery_status_success_sampling_rate = 0
}

# Optional: a CloudWatch alarm that fires when monthly spend approaches the cap.
# Uncomment after creating an SNS topic for alerts and wiring it as the action.
#
# resource "aws_cloudwatch_metric_alarm" "sms_spend" {
#   alarm_name          = "sns-sms-spend-near-limit"
#   comparison_operator = "GreaterThanOrEqualToThreshold"
#   evaluation_periods  = 1
#   metric_name         = "SMSMonthToDateSpentUSD"
#   namespace           = "AWS/SNS"
#   period              = 3600
#   statistic           = "Maximum"
#   threshold           = floor(var.sms_monthly_spend_limit_usd * 0.8)
#   alarm_actions       = [aws_sns_topic.alerts.arn]
# }
