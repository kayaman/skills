# Genie Conversation API

Embed Genie answers in custom apps, Slack bots, internal portals, or agent flows. The API is REST, asynchronous (poll for completion), and authenticated via OAuth.

## Contents

1. Authentication
2. Endpoint reference
3. Polling pattern
4. Response shape
5. Rate limits
6. End-to-end example (Python)
7. Embedding patterns
8. Operational notes

---

## 1. Authentication

OAuth — pick one based on caller identity:

- **OAuth U2M (User-to-Machine)** — the calling app acts on behalf of the end user. The user's Unity Catalog ACLs (row filters, column masks, table privileges) are enforced. Use for any human-facing surface.
- **OAuth M2M (Machine-to-Machine)** — a service principal calls the API. The service principal's privileges apply, *not* the end user's. Only safe when the upstream surface is itself authenticated and authorised, or when the data set is non-sensitive.

The service principal must have:

- `CAN RUN` (or higher) on the Genie space.
- `SELECT` on every Unity Catalog object the space references.

**Anti-pattern.** M2M as a backdoor around row filters. If the agent is fronted by a multi-tenant app, you owe the data owner a per-user authorisation story — pass user identity through and use U2M, or replicate the row filter at the app layer.

## 2. Endpoint reference

Base path: `/api/2.0/genie/spaces/{space_id}`.

| Verb | Path | Purpose |
|---|---|---|
| POST | `/start-conversation` | Open a new conversation with a first question. Returns `conversation_id` and `message_id`. |
| POST | `/conversations/{conversation_id}/messages` | Ask a follow-up in an existing conversation. |
| GET | `/conversations/{conversation_id}/messages/{message_id}` | Poll for status; on `COMPLETED` returns attachments (text + SQL). |
| GET | `/conversations/{conversation_id}/messages/{message_id}/query-result/{attachment_id}` | Fetch the materialised query result rows. |

Request body for POSTs:

```json
{ "content": "Show me net new ARR for EMEA in 2026" }
```

## 3. Polling pattern

`GET …/messages/{message_id}` returns a `status` field. States to handle:

- `IN_PROGRESS` — keep polling.
- `COMPLETED` — `attachments` populated.
- `FAILED` — inspect `error` for the reason; surface to user.
- `CANCELED` — typically user-initiated; treat as terminal.

Recommendation:

- Poll every 1–2 seconds initially.
- Apply **exponential backoff up to 60 seconds**.
- Hard stop after 10 minutes — there's no value in waiting longer for an interactive surface.
- Only POSTs count toward the rate limit; GETs are free.

## 4. Response shape

A `COMPLETED` message returns `attachments` — typically a `text` attachment (Genie's prose summary) and a `query` attachment (the generated SQL with `query.parameters`). Trusted-asset usage is signalled by `query.parameters` referring to a parameterized example or SQL Function.

Reasoning trace lives in `query_attachments` — useful for debugging *why* Genie chose a particular path.

## 5. Rate limits

- Free-tier reference: ~5 questions per minute per workspace.
- Paid: up to 20 questions per minute per workspace.
- Per-space: 10,000 conversations total — plan archival or cloning before saturation.

Only POST `start-conversation` and `messages` count. Polling GETs are exempt.

## 6. End-to-end example (Python)

```python
import os
import time
import requests

WS = os.environ["DATABRICKS_HOST"]            # e.g. https://acme.cloud.databricks.com
TOKEN = os.environ["DATABRICKS_TOKEN"]        # OAuth U2M or M2M access token
SPACE = os.environ["GENIE_SPACE_ID"]
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def ask(question: str) -> dict:
    # 1. Start conversation
    r = requests.post(
        f"{WS}/api/2.0/genie/spaces/{SPACE}/start-conversation",
        json={"content": question},
        headers=HEADERS,
        timeout=30,
    )
    r.raise_for_status()
    conv_id = r.json()["conversation_id"]
    msg_id = r.json()["message_id"]

    # 2. Poll until COMPLETED, with exponential backoff capped at 60s
    delay, deadline = 1.0, time.time() + 600
    while time.time() < deadline:
        m = requests.get(
            f"{WS}/api/2.0/genie/spaces/{SPACE}/conversations/{conv_id}/messages/{msg_id}",
            headers=HEADERS,
            timeout=30,
        ).json()
        if m["status"] == "COMPLETED":
            break
        if m["status"] in ("FAILED", "CANCELED"):
            raise RuntimeError(f"Genie {m['status']}: {m.get('error')}")
        time.sleep(delay)
        delay = min(delay * 1.5, 60.0)
    else:
        raise TimeoutError("Genie did not complete within 10 minutes")

    # 3. If a query attachment exists, fetch its rows
    rows = []
    for att in m.get("attachments", []):
        if att.get("type") == "query":
            qr = requests.get(
                f"{WS}/api/2.0/genie/spaces/{SPACE}/conversations/{conv_id}"
                f"/messages/{msg_id}/query-result/{att['attachment_id']}",
                headers=HEADERS,
                timeout=60,
            ).json()
            rows.extend(qr.get("data", []))

    return {"text": m, "rows": rows}

if __name__ == "__main__":
    print(ask("Net new ARR for EMEA in 2026 by quarter"))
```

## 7. Embedding patterns

Three common shapes:

**A. Chat surface in an internal app.**
U2M auth, one conversation per user session, follow-ups via `messages`. Show the generated SQL behind a "View SQL" affordance — power users want it; consumers don't.

**B. Slack/Teams bot.**
M2M with a per-channel service principal whose privileges match the channel's audience (separate principals per audience). Map a thread to one conversation_id; new threads = new conversation. Surface "Trusted" status as an emoji indicator.

**C. Agent tool.**
A Mosaic AI / LangGraph agent calls Genie as one of its tools. Wrap `ask()` as a typed tool with a structured return (text + rows + sql). Cap polling timeout aggressively (60–120s) — agents that wait minutes feel broken.

For all three: log `correlation_id` from the response next to your app's request id. Cross-system debugging without it is painful.

## 8. Operational notes

- **Fresh conversations per session.** Don't reuse a `conversation_id` across unrelated user tasks; conversation context contaminates intent.
- **Retry with jitter on 429.** The rate limit is per-workspace; under bursty load, queue and back off rather than hammering.
- **Prefer Serverless** for API-driven loads — predictable cold-start behaviour.
- **Cache by question hash *only* for non-personalised data.** Per-user filtering through Unity Catalog means a cached answer for user A is wrong for user B.

(Sources: Databricks docs — *Use the Genie Conversation API*; release notes 2025–2026.)
