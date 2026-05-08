// Adapted from ai-assisted-dev (MIT) — see references/citations.md
// SES v2 transactional sender for OTP codes. Lazy-singleton client — the
// constructor is cheap, but reusing it across warm invocations avoids
// recreating the HTTP agent.

import { SESv2Client, SendEmailCommand } from "@aws-sdk/client-sesv2";

let client: SESv2Client | null = null;
const ses = (): SESv2Client => (client ??= new SESv2Client({}));

export const sendOtpEmail = async (to: string, otp: string): Promise<void> => {
	const from = process.env["SES_FROM"];
	if (!from) throw new Error("SES_FROM env var must be set");
	const appName = process.env["APP_NAME"] ?? "your account";

	await ses().send(
		new SendEmailCommand({
			FromEmailAddress: from,
			Destination: { ToAddresses: [to] },
			Content: {
				Simple: {
					Subject: { Data: "Your sign-in code", Charset: "UTF-8" },
					Body: {
						Text: {
							Data: `Your sign-in code is ${otp}. It expires in 5 minutes.\n\nIf you didn't request this, ignore the message.\n\n${appName}`,
							Charset: "UTF-8",
						},
					},
				},
			},
		}),
	);
};
