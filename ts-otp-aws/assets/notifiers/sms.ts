// Adapted from ai-assisted-dev (MIT) — see references/citations.md
// SNS transactional SMS sender for OTP codes. SenderID is parameterized via
// SMS_SENDER_ID and falls back to "OTP". On networks that don't honor sender
// IDs (US/Canada), the recipient sees the long/short code instead.
//
// Phone numbers must be in E.164 (+<country><subscriber>). Validate at the
// edge — SNS rejects malformed numbers with InvalidParameter.

import { PublishCommand, SNSClient } from "@aws-sdk/client-sns";

let client: SNSClient | null = null;
const sns = (): SNSClient => (client ??= new SNSClient({}));

export const sendOtpSms = async (phoneE164: string, otp: string): Promise<void> => {
	const senderId = process.env["SMS_SENDER_ID"] ?? "OTP";
	const appName = process.env["APP_NAME"] ?? "App";

	await sns().send(
		new PublishCommand({
			PhoneNumber: phoneE164,
			Message: `[${appName}] Sign-in code: ${otp} (5 min). Reply STOP to unsubscribe.`,
			MessageAttributes: {
				"AWS.SNS.SMS.SMSType": { DataType: "String", StringValue: "Transactional" },
				"AWS.SNS.SMS.SenderID": { DataType: "String", StringValue: senderId },
			},
		}),
	);
};
