// Adapted from ai-assisted-dev (MIT) — see references/citations.md
// State machine for the CUSTOM_AUTH flow. Caps wrong-answer attempts at 3.

import type { DefineAuthChallengeTriggerEvent } from "aws-lambda";

const MAX_ATTEMPTS = 3;

/**
 * - First call (no session): issue CUSTOM_CHALLENGE
 * - Subsequent calls:
 *     last answer correct → issue tokens
 *     wrong but under MAX_ATTEMPTS → issue another CUSTOM_CHALLENGE
 *     wrong at MAX_ATTEMPTS → fail authentication
 */
export const defineChallenge = (
	event: DefineAuthChallengeTriggerEvent,
): DefineAuthChallengeTriggerEvent => {
	const session = event.request.session ?? [];
	const last = session.at(-1);

	if (session.length === 0) {
		event.response.issueTokens = false;
		event.response.failAuthentication = false;
		event.response.challengeName = "CUSTOM_CHALLENGE";
		return event;
	}

	if (last?.challengeName === "CUSTOM_CHALLENGE" && last.challengeResult === true) {
		event.response.issueTokens = true;
		event.response.failAuthentication = false;
		return event;
	}

	if (session.length >= MAX_ATTEMPTS) {
		event.response.issueTokens = false;
		event.response.failAuthentication = true;
		return event;
	}

	event.response.issueTokens = false;
	event.response.failAuthentication = false;
	event.response.challengeName = "CUSTOM_CHALLENGE";
	return event;
};
