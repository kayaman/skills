// Adapted from ai-assisted-dev (MIT) — see references/citations.md
// Constant-time comparison of the user-submitted OTP against the code stored
// in privateChallengeParameters by create-challenge.
//
// Note: AAD_DEV_OTP_BYPASS in the upstream source has been renamed to
// OTP_DEV_BYPASS for portability across projects. Set OTP_DEV_BYPASS=1 in
// non-prod environments to accept the constant code 000000. CI policy MUST
// assert this var is unset on production Lambda functions.

import { timingSafeEqual } from "node:crypto";
import type { VerifyAuthChallengeResponseTriggerEvent } from "aws-lambda";

const DEV_BYPASS_CODE = "000000";

const constantEq = (a: string, b: string): boolean => {
	const ab = Buffer.from(a, "utf8");
	const bb = Buffer.from(b, "utf8");
	if (ab.length !== bb.length) return false;
	return timingSafeEqual(ab, bb);
};

export const verifyChallenge = (
	event: VerifyAuthChallengeResponseTriggerEvent,
): VerifyAuthChallengeResponseTriggerEvent => {
	const expected = event.request.privateChallengeParameters?.["code"];
	const actual = event.request.challengeAnswer;

	if (typeof expected !== "string" || typeof actual !== "string") {
		event.response.answerCorrect = false;
		return event;
	}
	if (!/^\d{6}$/.test(actual)) {
		event.response.answerCorrect = false;
		return event;
	}

	const devBypass =
		process.env["OTP_DEV_BYPASS"] === "1" && constantEq(actual, DEV_BYPASS_CODE);

	event.response.answerCorrect = devBypass || constantEq(expected, actual);
	return event;
};
