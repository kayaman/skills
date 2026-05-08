// Adapted from ai-assisted-dev (MIT) — see references/citations.md
// Cognito user pool dispatcher: routes the four CUSTOM_AUTH triggers and
// PreSignUp through one Lambda function. The default arm intentionally throws
// so that an incorrectly-wired trigger ARN surfaces fast.

import type {
	CreateAuthChallengeTriggerEvent,
	DefineAuthChallengeTriggerEvent,
	PreSignUpTriggerEvent,
	VerifyAuthChallengeResponseTriggerEvent,
} from "aws-lambda";
import { createChallenge } from "./handlers/create-challenge.js";
import { defineChallenge } from "./handlers/define-challenge.js";
import { preSignUp } from "./handlers/pre-signup.js";
import { verifyChallenge } from "./handlers/verify-challenge.js";

type CognitoTriggerEvent =
	| PreSignUpTriggerEvent
	| DefineAuthChallengeTriggerEvent
	| CreateAuthChallengeTriggerEvent
	| VerifyAuthChallengeResponseTriggerEvent;

export const handler = async (event: CognitoTriggerEvent): Promise<CognitoTriggerEvent> => {
	try {
		switch (event.triggerSource) {
			case "PreSignUp_AdminCreateUser":
			case "PreSignUp_SignUp":
			case "PreSignUp_ExternalProvider":
				return preSignUp(event as PreSignUpTriggerEvent);

			case "DefineAuthChallenge_Authentication":
				return defineChallenge(event as DefineAuthChallengeTriggerEvent);

			case "CreateAuthChallenge_Authentication":
				return createChallenge(event as CreateAuthChallengeTriggerEvent);

			case "VerifyAuthChallengeResponse_Authentication":
				return verifyChallenge(event as VerifyAuthChallengeResponseTriggerEvent);

			default: {
				const exhaustive = event as { triggerSource: string };
				throw new Error(`unsupported trigger source: ${exhaustive.triggerSource}`);
			}
		}
	} catch (err) {
		// Surface the failing trigger + underlying AWS SDK error code in one
		// CloudWatch line so the SES/SNS reason (MessageRejected,
		// MailFromDomainNotVerified, AccessDenied, ...) is immediately greppable.
		// Anything thrown here becomes UserLambdaValidationException at the caller.
		const e = err as { name?: string; message?: string; $metadata?: { httpStatusCode?: number } };
		console.error("auth-triggers failed", {
			triggerSource: event.triggerSource,
			userPoolId: event.userPoolId,
			userName: event.userName,
			errorName: e.name ?? "Unknown",
			errorMessage: e.message ?? String(err),
			httpStatusCode: e.$metadata?.httpStatusCode,
		});
		throw err;
	}
};
