// Adapted from ai-assisted-dev (MIT) — see references/citations.md
// Auto-confirm the user so the first InitiateAuth doesn't trip on an
// unconfirmed account. Use only when the OTP itself is the proof of identity
// (i.e. signup IS the first login). Remove this trigger if you require the
// classic Cognito confirmation-code flow.

import type { PreSignUpTriggerEvent } from "aws-lambda";

export const preSignUp = (event: PreSignUpTriggerEvent): PreSignUpTriggerEvent => {
	event.response.autoConfirmUser = true;
	event.response.autoVerifyEmail = true;
	event.response.autoVerifyPhone = true;
	return event;
};
