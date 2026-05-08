# SES domain identity, DKIM, and custom MAIL FROM. After applying this you must
# also publish the DKIM CNAMEs and MAIL FROM MX/TXT records in your DNS zone
# (a Route 53 zone is shown as the example).

variable "ses_domain" {
  description = "Apex domain used as the SES sending identity (e.g. example.com)."
  type        = string
}
variable "mail_from_subdomain" {
  description = "Subdomain used for MAIL FROM (must NOT be the apex; e.g. bounce)."
  type        = string
  default     = "bounce"
}
variable "route53_zone_id" {
  description = "Hosted zone ID for the apex domain. Set to null to manage records elsewhere."
  type        = string
  default     = null
}

resource "aws_sesv2_email_identity" "domain" {
  email_identity = var.ses_domain
}

resource "aws_sesv2_email_identity_mail_from_attributes" "domain" {
  email_identity         = aws_sesv2_email_identity.domain.email_identity
  mail_from_domain       = "${var.mail_from_subdomain}.${var.ses_domain}"
  behavior_on_mx_failure = "USE_DEFAULT_VALUE"
}

# DKIM CNAMEs — published only when a Route 53 zone is provided.
resource "aws_route53_record" "dkim" {
  count = var.route53_zone_id == null ? 0 : 3

  zone_id = var.route53_zone_id
  name    = "${aws_sesv2_email_identity.domain.dkim_signing_attributes[0].tokens[count.index]}._domainkey.${var.ses_domain}"
  type    = "CNAME"
  ttl     = 600
  records = ["${aws_sesv2_email_identity.domain.dkim_signing_attributes[0].tokens[count.index]}.dkim.amazonses.com"]
}

# MAIL FROM SPF (TXT) and MX records.
resource "aws_route53_record" "mail_from_mx" {
  count = var.route53_zone_id == null ? 0 : 1

  zone_id = var.route53_zone_id
  name    = aws_sesv2_email_identity_mail_from_attributes.domain.mail_from_domain
  type    = "MX"
  ttl     = 600
  records = ["10 feedback-smtp.${data.aws_region.current.name}.amazonses.com"]
}

resource "aws_route53_record" "mail_from_spf" {
  count = var.route53_zone_id == null ? 0 : 1

  zone_id = var.route53_zone_id
  name    = aws_sesv2_email_identity_mail_from_attributes.domain.mail_from_domain
  type    = "TXT"
  ttl     = 600
  records = ["v=spf1 include:amazonses.com -all"]
}

# DMARC policy on the apex — start at p=none with reporting, tighten later.
variable "dmarc_rua" {
  description = "Mailbox that receives DMARC aggregate reports (e.g. dmarc@example.com)."
  type        = string
  default     = null
}

resource "aws_route53_record" "dmarc" {
  count = var.route53_zone_id == null || var.dmarc_rua == null ? 0 : 1

  zone_id = var.route53_zone_id
  name    = "_dmarc.${var.ses_domain}"
  type    = "TXT"
  ttl     = 600
  records = ["v=DMARC1; p=none; rua=mailto:${var.dmarc_rua}"]
}

data "aws_region" "current" {}

output "ses_identity" { value = aws_sesv2_email_identity.domain.email_identity }
output "mail_from_domain" { value = aws_sesv2_email_identity_mail_from_attributes.domain.mail_from_domain }
