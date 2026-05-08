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

const buildHint = (
	channel: Channel,
	userName: string,
	email: string | undefined,
	phone: string | undefined,
): string => {
	if (channel === "sms") return maskTail(phone ?? userName);
	const source = email ?? userName;
	const localPart = source.split("@")[0] ?? source;
	return maskTail(localPart || source);
};

export const createChallenge = async (
	event: CreateAuthChallengeTriggerEvent,
): Promise<CreateAuthChallengeTriggerEvent> => {
	const channel = pickChannel(event.request.clientMetadata?.["channel"]);
	const otp = generateOtp();

	const email = event.request.userAttributes["email"];
	const phone = event.request.userAttributes["phone_number"];

	const phantom = event.request.userNotFound === true;
	const hasEmail = Boolean(email);
	const hasPhone = Boolean(phone);

	const effectiveChannel: Channel =
		channel === "sms"
			? hasPhone
				? "sms"
				: hasEmail
					? "email"
					: "sms"
			: hasEmail
				? "email"
				: hasPhone
					? "sms"
					: "email";

	const deliveryTarget = effectiveChannel === "sms" ? phone : email;

	if (!phantom && deliveryTarget) {
		if (effectiveChannel === "sms") {
			await sendOtpSms(deliveryTarget, otp);
		} else {
			await sendOtpEmail(deliveryTarget, otp);
		}
	}

	event.response.publicChallengeParameters = {
		channel: effectiveChannel,
		hint: buildHint(effectiveChannel, event.userName, email, phone),
	};
	event.response.privateChallengeParameters = { code: otp };
	event.response.challengeMetadata = `OTP-${effectiveChannel.toUpperCase()}`;

	return event;
};
