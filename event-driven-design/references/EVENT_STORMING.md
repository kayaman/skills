# Event Storming — Reference

Load this when the task starts from a blank domain — no events designed yet — or when an existing system has drifted so far from its domain language that it's easier to rediscover than to refactor.

Event storming is a collaborative modelling technique invented by Alberto Brandolini (*Introducing EventStorming*). O'Reilly references below: Vlad Khononov, *Learning Domain-Driven Design* (O'Reilly); Susanne Kaiser, *Architecture for Flow* (Addison-Wesley via O'Reilly); Michael Keeling, *Design It!* (Pragmatic Bookshelf via O'Reilly); Jean-Georges Perrin & Nick Tune, *Architecture Modernization* (Manning/O'Reilly); Chris Richardson, *Microservices Patterns* (O'Reilly); Vaughn Vernon, *Implementing Domain-Driven Design* (O'Reilly).

---

## 1. Three formats, three questions

Event storming is not one workshop — it is three formats answering three different questions.

| Format | Question | Output |
|---|---|---|
| **Big Picture** | What happens in the business end-to-end? | A timeline of pivotal events; candidate bounded contexts. |
| **Process Level** | How does a specific process flow? | A detailed model of commands, events, policies, actors, read models, and external systems for one bounded context. |
| **Design Level** | How will we implement this aggregate? | A model of aggregates with their commands, events, and invariants — ready to translate to code. |

**Run them in that order.** Skipping Big Picture lands you in detail before you understand the shape of the domain.

---

## 2. The colour code

The specific colours are less important than consistency within a session. This is the canonical set (Brandolini's):

| Colour | Meaning | Past/present | Notation |
|---|---|---|---|
| **Orange** | Domain event | Past tense | `OrderPlaced` |
| **Blue** | Command | Imperative | `PlaceOrder` |
| **Yellow** | Aggregate | Noun | `Order` |
| **Pink / Red** | Hotspot / problem / unknown | — | "Why does this fail 3% of the time?" |
| **Lilac / Purple** | Policy / reactive rule | "Whenever… then…" | "Whenever `OrderPlaced` then trigger `ReserveInventory`" |
| **Pink (different shade)** | External system | Noun | `StripeAPI`, `LegacyCRM` |
| **Yellow (small)** | Actor / persona | Role | "Customer", "Fulfillment clerk" |
| **Green** | Read model | Noun | "Order confirmation view" |

Keep a legend sticky in the room / on the virtual board. New participants lose the thread otherwise.

---

## 3. Running the Big Picture workshop

### 3.1 Setup

- **Time.** Half a day to a full day for a non-trivial domain.
- **Room.** Long wall (physical) or very wide virtual board (Miro/Mural). Timeline runs left to right.
- **Facilitator.** Someone who has run one before, or has done their reading. First-time facilitators should expect chaos in the first hour.
- **Participants.** Mix of domain experts, product, and engineers. Diverse perspectives are the point. Maximum ~12 people; beyond that, split into parallel boards.
- **Supplies.** Thousands of sticky notes in the agreed colours. Sharpies only — no ballpoint pens; pens make notes unreadable at distance.

### 3.2 The chaotic storm (first 30–60 minutes)

Everyone writes orange stickies for domain events they can think of. No discussion. No ordering. Just events, past tense, as many as possible.

> "When a customer signs up, what happens? — UserRegistered, EmailVerificationSent, WelcomeEmailSent, AccountActivated, …"

Stick them to the wall anywhere. Duplicates are fine; they reveal which events are salient.

### 3.3 Place on the timeline

Move the stickies into left-to-right order along the timeline. Duplicates collapse as you go. Events whose position nobody can agree on become *hotspots* (red stickies): they indicate disagreement about what actually happens.

### 3.4 Identify pivotal events

Mark the most important events with bold vertical dividers. These are usually:

- State transitions that matter to the business (`OrderPlaced`, `PaymentCaptured`, `OrderShipped`).
- Events that cross team boundaries.
- Events that stakeholders already talk about by name.

The pivotal events are candidate seams between bounded contexts.

### 3.5 Walk the wall, backward

Starting from the rightmost pivotal event, walk backward asking "what had to happen before this?". This surfaces missing events and exposes implicit assumptions.

### 3.6 Outcome

A timeline of orange events, with red hotspots flagged and pivotal events highlighted. Candidate bounded-context boundaries drawn as vertical lines. Not yet commands, policies, or aggregates — those come next.

---

## 4. Process-level modelling

Pick one region of the Big Picture (one bounded context, usually). For each orange event, add:

- **Blue command** that causes it. `PlaceOrder` → `OrderPlaced`.
- **Yellow aggregate** that handles the command. `Order` aggregate handles `PlaceOrder`.
- **Small yellow actor** that issues the command. "Customer" issues `PlaceOrder`.
- **Lilac policy** for each "whenever X then Y" rule. "Whenever `OrderPlaced` then send a `ReserveInventory` command".
- **Pink external system** where the process touches outside the domain. `StripeAPI` receives `CapturePayment`.
- **Green read model** that populates UI or reports. "Customer order history view".

The result is a detailed process flow. The stickies are now a specification draft.

### Process-level heuristics

- **Every command has an actor.** "Who issues this?" — if no one does, it's a policy, not a command.
- **Every event is caused by something.** Either a command (usually) or a policy (less often). Orphan events hide missing workflow.
- **Aggregate boundaries are where invariants live.** If two commands need to be consistent with each other, they run against the same aggregate.

---

## 5. Design-level modelling

Zoom one more step. Take a single aggregate and draft:

- Its commands (blue).
- Its events (orange).
- Its invariants (written on the aggregate sticky, or a separate note).
- Its relationships to other aggregates (cross-aggregate: only via events, never via direct reference).

At this level you are almost writing code in stickies. Move to actual code when the design feels stable. Round-trip between the sticky model and the code in the first weeks of implementation; discrepancies indicate the model was wrong or the code is diverging — resolve, don't ignore.

(Richardson, *Microservices Patterns*; Vernon, *Implementing Domain-Driven Design*; Khononov, *Learning DDD*.)

---

## 6. From stickies to bounded contexts

A **bounded context** is a scope in which a single ubiquitous language applies. The same word means one thing inside the context, possibly something different outside.

Signals that two regions of the event storm are different bounded contexts:

- The same noun means different things. ("Order" in Sales is pre-checkout; "Order" in Fulfillment is post-payment. Different lifecycles, same word. → Two contexts.)
- Different people govern the rules. (Marketing owns tier rules; Billing owns pricing. → Two contexts.)
- Pivotal events separate them. (Before `OrderPlaced`: cart/browsing context. After: fulfillment context.)

Draw a vertical divider on the wall. Name each region. Each region becomes a candidate service (or a module, if you are not yet breaking apart the monolith — see *Learning DDD* on modular monoliths).

**Context mapping.** Between contexts, draw the relationship: shared kernel, customer/supplier, conformist, anti-corruption layer, published language, open-host service. Events typically travel along a *published language* boundary — the schema is the public contract.

---

## 7. From stickies to events (and to this skill)

After event storming, each orange sticky becomes a candidate event. Before implementing:

1. **Does it have an aggregate?** If no, model the aggregate.
2. **What is its envelope?** Open `EVENT_SCHEMA.md`; apply.
3. **What is the producing topic?** Usually `<context>.<event-name>.v1`.
4. **What are the consumers?** List them. Each consumer is a candidate subscriber with its own schema-compatibility requirements.
5. **Is it a business fact or a technical change?** Business facts are first-class; technical changes (CDC) are infrastructure plumbing and should rarely be on public topics.

An aggregate extracted from design-level event storming flows directly into the aggregate / command handler / event publication pattern in `PATTERNS.md`. The colour code is a translation table — you are not throwing away the stickies when you start coding; you are compiling them.

---

## 8. Common mistakes

- **Starting with blue (commands).** Feels structured; skips the point. Start with orange so domain experts drive the conversation.
- **Ending at Big Picture.** The timeline is informative but not actionable. Commit to process-level for at least the contexts you plan to touch soon.
- **Writing events in the present tense.** "Order placing" instead of "Order placed". Enforce past tense from sticky one; it's the single rule that keeps the model honest.
- **Putting UI state on the wall.** "Customer sees confirmation page" is a read-model concern, not a domain event. Move it to green; the orange event is `OrderConfirmationRendered`… no wait, that is not a domain event either — the fact is `OrderConfirmed`, which was already there.
- **Accepting every hotspot as "TBD".** Hotspots are the value of the workshop. Resolve at least the hotspots on the critical path before leaving.

---

## 9. Remote and asynchronous event storming

Physical is the gold standard. Remote works with some adaptations:

- Very large virtual board (Miro/Mural); pre-create a grid so stickies don't overlap chaotically.
- Smaller groups (5–8). Any larger and people mute.
- Longer sessions are worse; split into two 2-hour sessions with a day between to let the model settle.
- Asynchronous "storm first, converge later": individuals add stickies in their time zone; the group converges in a shared session.

Do not try to event storm by Zoom screen-share without a virtual board. Stickies are not optional.

---

## 10. Exit criteria for an event storming session

A session is done when, on the agreed scope:

- The timeline of orange events is continuous (no "and then somehow…" gaps).
- Every event has a causing command or policy.
- Every command has an aggregate that handles it.
- Red hotspots are either resolved or tagged with an owner and a follow-up.
- Candidate bounded-context boundaries are drawn and named.
- Participants from different disciplines describe the same region of the board in the same words. (If not, the language is not yet ubiquitous.)

Capture the board (photograph the physical wall, export the virtual board). The artifact is a specification-level input for `EVENT_SCHEMA.md` and `PATTERNS.md`.
