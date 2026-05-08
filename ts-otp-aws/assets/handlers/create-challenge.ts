// Adapted from ai-assisted-dev (MIT) — see references/citations.md
// Generates a 6-digit OTP, sends it via SES (email) or SNS (SMS), and stashes
// the code in privateChallengeParameters for the verify trigger to read back.
//
// Phantom-user safety: with prevent_user_existence_errors=ENABLED, Cognito
// invokes this trigger for unknown usernames with userNotFound=true and an
// empty userAttributes map. The handler MUST succeed silently — throwing
// surfaces as UserLambdaValidationException to InitiateAuth and leaks user
// existence to the caller.

import { randomInt } from "node:crypto";
import type { CreateAuthChallengeTriggerEvent } from "aws-lambda";
import { sendOtpEmail } from "../notifiers/email.js";
import { sendOtpSms } from "../notifiers/sms.js";

type Channel = "email" | "sms";

const pickChannel = (raw: string | undefined): Channel => (raw === "sms" ? "sms" : "email");

const generateOtp = (): string => randomInt(0, 1_000_000).toString().padStart(6, "0");

const maskTail = (s: string, tail = 4): string =>
	s.length <= tail ? s.replace(/./g, "*") : `${"*".repeat(s.length - tail)}${s.slice(-tail)}`;

export const createChallenge = async (
	event: CreateAuthChallengeTriggerEvent,
): Promise<CreateAuthChallengeTriggerEvent> => {
	const channel = pickChannel(event.request.clientMetadata?.["channel"]);
	const otp = generateOtp();

	const email = event.request.userAttributes["email"];
	const phone = event.request.userAttributes["phone_number"];

	const phantom = event.request.userNotFound === true;

	if (!phantom) {
		if (channel === "sms") {
			if (!phone) throw new Error("user has no phone_number on file");
			await sendOtpSms(phone, otp);
		} else {
			if (!email) throw new Error("user has no email on file");
			await sendOtpEmail(email, otp);
		}
	}

	event.response.publicChallengeParameters = {
		channel,
		hint: channel === "sms" ? maskTail(phone ?? "") : maskTail((email ?? "").split("@")[0] ?? ""),
	};
	event.response.privateChallengeParameters = { code: otp };
	event.response.challengeMetadata = `OTP-${channel.toUpperCase()}`;

	return event;
};
