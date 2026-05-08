// Adapted from ai-assisted-dev (MIT) — see references/citations.md
//
// Server-side Cognito client used by the OTP login endpoints. Lazy-singleton
// pattern; reuses the HTTP agent across warm Lambda invocations.
//
// Required env vars:
//   COGNITO_CLIENT_ID      — App client ID (no secret).
//   COGNITO_USER_POOL_ID   — User pool ID (only needed for phone→username lookup).
//   AWS_REGION             — Defaults to us-east-1 if unset.

import {
	CognitoIdentityProviderClient,
	InitiateAuthCommand,
	ListUsersCommand,
	RespondToAuthChallengeCommand,
} from "@aws-sdk/client-cognito-identity-provider";

let cached: CognitoIdentityProviderClient | null = null;
const cognito = (): CognitoIdentityProviderClient =>
	(cached ??= new CognitoIdentityProviderClient({
		region: process.env.AWS_REGION ?? "us-east-1",
	}));

export type Channel = "email" | "sms";

const requireClientId = (): string => {
	const id = process.env.COGNITO_CLIENT_ID;
	if (!id) throw new Error("COGNITO_CLIENT_ID env var must be set");
	return id;
};

const requireUserPoolId = (): string => {
	const id = process.env.COGNITO_USER_POOL_ID;
	if (!id) throw new Error("COGNITO_USER_POOL_ID env var must be set");
	return id;
};

const isPhoneE164 = (s: string): boolean => /^\+\d{8,15}$/.test(s);
const isEmail = (s: string): boolean => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s);

/**
 * Resolve any identifier (E.164 phone or email) to the Cognito username.
 * The user pool uses email as the username, so phone lookups go through
 * `ListUsers` with a `phone_number = "..."` filter.
 *
 * On no-match, returns the original identifier so InitiateAuth produces a
 * phantom-user session — Cognito's `prevent_user_existence_errors=ENABLED`
 * keeps that opaque to the caller.
 */
const resolveUsername = async (identifier: string): Promise<string> => {
	if (isEmail(identifier)) return identifier;
	if (!isPhoneE164(identifier)) return identifier;
	const out = await cognito().send(
		new ListUsersCommand({
			UserPoolId: requireUserPoolId(),
			Filter: `phone_number = "${identifier}"`,
			Limit: 1,
		}),
	);
	const user = out.Users?.[0];
	const email = user?.Attributes?.find((a) => a.Name === "email")?.Value;
	return email ?? identifier;
};

export type StartResult = {
	readonly session: string;
	readonly username: string;
	readonly channel: Channel;
	readonly hint: string;
};

export const startOtpAuth = async (identifier: string, channel: Channel): Promise<StartResult> => {
	const username = await resolveUsername(identifier);
	const out = await cognito().send(
		new InitiateAuthCommand({
			AuthFlow: "CUSTOM_AUTH",
			ClientId: requireClientId(),
			AuthParameters: { USERNAME: username },
			ClientMetadata: { channel },
		}),
	);
	if (!out.Session) throw new Error("Cognito did not return a session");
	const params = (out.ChallengeParameters ?? {}) as Record<string, string>;
	return {
		session: out.Session,
		username,
		channel: (params.channel as Channel) ?? channel,
		hint: params.hint ?? "",
	};
};

export type VerifyResult =
	| {
			readonly ok: true;
			readonly idToken: string;
			readonly accessToken: string;
			readonly refreshToken: string | undefined;
	  }
	| {
			readonly ok: false;
			readonly session: string | null;
			readonly error: "wrong-code" | "expired" | "unknown";
	  };

export const verifyOtp = async (
	username: string,
	session: string,
	code: string,
): Promise<VerifyResult> => {
	try {
		const out = await cognito().send(
			new RespondToAuthChallengeCommand({
				ChallengeName: "CUSTOM_CHALLENGE",
				ClientId: requireClientId(),
				Session: session,
				ChallengeResponses: { USERNAME: username, ANSWER: code },
			}),
		);
		if (out.AuthenticationResult?.IdToken && out.AuthenticationResult.AccessToken) {
			return {
				ok: true,
				idToken: out.AuthenticationResult.IdToken,
				accessToken: out.AuthenticationResult.AccessToken,
				refreshToken: out.AuthenticationResult.RefreshToken,
			};
		}
		// Cognito returned a fresh challenge — wrong code, ask again.
		return { ok: false, session: out.Session ?? null, error: "wrong-code" };
	} catch (e) {
		const name = (e as { name?: string }).name ?? "";
		if (name === "NotAuthorizedException") return { ok: false, session: null, error: "expired" };
		return { ok: false, session: null, error: "unknown" };
	}
};
