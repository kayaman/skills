# SOLID Principles

Five principles of class design from Robert C. Martin. Collectively they
describe what a maintainable OO system looks like at the unit level.
Follow them enough and rigidity, fragility, and coupling drop sharply;
follow them dogmatically and designs become abstract cathedrals nobody
can change. The goal is *judgment*, not ceremony.

Canonical references: Martin, *Agile Software Development, Principles,
Patterns, and Practices* (2002); Martin, *Clean Architecture* (2017),
Chs. 7–11.

---

## S — Single Responsibility Principle

> A class should have only one reason to change.

Not "a class should do one thing" — that's the common misreading. SRP is
about **axes of change**. If the billing team and the marketing team
both edit `InvoicePrinter` for different reasons, the class has two
responsibilities and should split.

**Diagnostic:** imagine two stakeholders. If they could plausibly
request changes that both land in the same class, the class violates
SRP.

**Symptoms:**

- Classes named `Manager`, `Handler`, `Utility`, `Helper`.
- Files over 500 lines.
- Methods grouped by "calls the same external system" rather than by a
  single coherent behavior.
- Changes in one feature break tests in unrelated features.

**Fix:** extract cohesive clusters. Use Fowler's *Extract Class*
refactor. The litmus test: each extracted class has a single reason to
change and its name is a noun from the domain, not a role word.

---

## O — Open/Closed Principle

> Software entities should be open for extension but closed for
> modification.

The stable thing is the **abstraction**; new behavior arrives through
new types, not by editing existing ones.

Classic example: a `PriceCalculator` that dispatches on customer type
via a chain of `if customer.is_vip(): … elif customer.is_wholesale():
…`. Adding a new customer type forces editing the calculator. An
OCP-compliant design passes a `PricingPolicy` in — new policy, new
class, no edits.

```python
# Before — modifying existing code for each new policy
class PriceCalculator:
    def calc(self, order: Order, customer_type: str) -> Money:
        if customer_type == "vip":     return order.subtotal * 0.8
        elif customer_type == "wholesale": return order.subtotal * 0.7
        # … edit here every time a new customer type arrives
        else:                          return order.subtotal

# After — extension through new classes (Strategy)
class PricingPolicy(Protocol):
    def apply(self, subtotal: Money) -> Money: ...

class VipPolicy:
    def apply(self, subtotal: Money) -> Money:
        return subtotal * 0.8
```

**Nuance:** OCP doesn't mean "no file ever changes". It means the
**stable interface** — the contract other code depends on — stays
closed. Extensions come through new implementations behind the same
contract.

**Warning.** Premature OCP is its own problem. Do not invent extension
points until the second concrete variant appears. Wait for the second
requirement, then refactor to abstract. (*Rule of Three*, Fowler.)

---

## L — Liskov Substitution Principle

> Subtypes must be substitutable for their base types without altering
> the correctness of the program.

A caller holding a reference to the base type should be unable to tell
which subtype it actually has. If `Rectangle.setWidth(w)` changes only
width, `Square.setWidth(w)` can't silently change height too — that's
a contract violation.

**Common violations:**

- Subclass that throws `NotImplementedError` for some base method ("we
  don't support delete for read-only lists"). The subclass is not a
  real subtype; extract a smaller interface.
- Subclass that strengthens preconditions ("base accepts any string,
  but this subtype requires a valid URL"). Callers that were fine with
  the base will now fail.
- Subclass that weakens postconditions ("base guarantees sorted output,
  this one doesn't"). Callers relying on the guarantee break.
- Subclass that narrows exception types inconsistently.

**Diagnostic:** searches for `isinstance(x, SubType)` or
`typeof x === 'SubType'` inside business logic are red flags. If
callers must inspect the subtype to behave correctly, the hierarchy is
broken.

**Fix:** split the hierarchy. Read-only and read-write collections are
different interfaces, not parent and child. Use ISP to define the
smaller one.

---

## I — Interface Segregation Principle

> Clients should not be forced to depend on interfaces they do not use.

Fat interfaces force implementations to support methods their callers
don't want. Split them.

**Example.** A `Document` interface with 30 methods. A cache consumer
only needs `get_key()` and `modified_at()`. A printer consumer only
needs `render()`. Each consumer should depend on a narrow interface
revealing only what it uses.

```python
# Before
class Document(Protocol):
    def get_key(self) -> str: ...
    def modified_at(self) -> datetime: ...
    def render(self) -> bytes: ...
    def save(self) -> None: ...
    # … 26 more

# After — split by consumer need
class Cacheable(Protocol):
    def get_key(self) -> str: ...
    def modified_at(self) -> datetime: ...

class Renderable(Protocol):
    def render(self) -> bytes: ...
```

**Python note.** `typing.Protocol` (PEP 544) fits ISP perfectly because
it's *structural* — a class satisfies the Protocol by having the
methods, no explicit inheritance required. Implementations don't need
to know about all the Protocols they happen to satisfy.

**TypeScript note.** TypeScript interfaces are also structural.
Discriminated unions often replace class hierarchies for ISP-style
role modeling.

---

## D — Dependency Inversion Principle

> High-level modules should not depend on low-level modules. Both should
> depend on abstractions. Abstractions should not depend on details;
> details should depend on abstractions.

This is the principle that makes Clean Architecture possible. In
practice:

1. High-level policy (business rules) defines the interface it needs.
2. Low-level mechanisms (DB, HTTP, email) implement that interface.
3. Both depend on the abstraction, which lives with the high-level
   policy.

```python
# In application (high-level):
class PaymentGateway(Protocol):
    def charge(self, amount: Money, token: str) -> ChargeResult: ...

class CheckoutUseCase:
    def __init__(self, gateway: PaymentGateway):
        self._gateway = gateway
```

```python
# In infrastructure (low-level):
class StripeGateway:
    def charge(self, amount: Money, token: str) -> ChargeResult:
        # stripe.Charge.create(...)
        ...
```

The high-level `CheckoutUseCase` does not know about Stripe. Stripe
conforms to the interface the use case requires. To add PayPal, write
a new adapter. No change to high-level code.

**Not the same as DI.** Dependency Inversion is a *design principle*
(dependency direction). Dependency Injection is a *mechanism* for
wiring dependencies (constructor parameters, setter methods, a
container). You can practice DIP with plain constructor injection; you
do not need a DI framework.

**Diagnostic:** in the inner layer, grep for imports of specific
libraries (`import requests`, `from stripe import`). Every such import
is a DIP violation waiting to be fixed.

---

## GRASP — a complementary lens

GRASP (General Responsibility Assignment Software Patterns, Larman) is
a set of nine principles for deciding **where a piece of behavior
should live**. SOLID tells you how classes should be shaped; GRASP
tells you how to assign responsibilities. Worth a mention because
several map directly to decisions you'll make while applying SOLID.

- **Information Expert** — assign the responsibility to the object that
  has the information needed to fulfill it. (Don't "ask then act" on
  another object; tell it to act.)
- **Creator** — class `B` should create `A` if `B` contains, aggregates,
  records, or closely uses `A`.
- **Controller** — assign use-case coordination to a dedicated class
  (what Clean Architecture calls the interactor).
- **Low Coupling** and **High Cohesion** — the fundamental metrics. All
  of SOLID serves these.
- **Polymorphism** — replace conditional behavior with polymorphic
  dispatch.
- **Pure Fabrication** — invent a class that doesn't map to a domain
  concept when doing so reduces coupling or raises cohesion.
- **Indirection** — insert an intermediate class to decouple two.
- **Protected Variations** — put a stable interface around things that
  vary.

Ref: Larman, *Applying UML and Patterns*, Ch. 17.

---

## How to apply SOLID during review

Not every class needs every principle. A small review protocol that
catches most structural issues:

1. **Size check.** How big is this class? Over 300 lines is a strong
   SRP smell.
2. **Change-reason check.** Who requests changes to this class, and
   why? More than one axis → split.
3. **Dependency direction.** Does this class import from the outer
   layer? DIP violation.
4. **Interface shape.** What does each caller actually use? If they
   use a small subset, extract a narrower interface (ISP).
5. **Subtype substitutability.** For every subclass, can it pass all
   the tests written for the base? If not, LSP violation.
6. **Extension points.** For the next plausible feature, is there an
   open seam or will you be editing existing logic? If the latter, OCP
   may be missing.

---

## When SOLID bites back

- **Over-abstraction.** Every concept behind an interface "just in
  case" is busywork that obscures the design. Abstract when a second
  concrete appears, not before.
- **Premature DIP.** Inverting dependencies has a cost (more files,
  more indirection). Worth it at bounded-context or service boundaries;
  overkill inside a single module that never changes across use cases.
- **Dogmatic SRP.** Splitting a class into six micro-classes can
  fragment cohesion. High cohesion is a goal *competing* with SRP, not
  subordinate to it. Cluster methods that genuinely belong together
  even if they technically span two reasons to change.
- **Interface explosion from ISP.** Ten Protocols with one method each
  is often worse than two Protocols with five focused methods. Aim for
  the granularity your callers actually need.

The principles are tools. The aim is code that is cheap to change for
the reasons change is most likely to come. When a principle and that
aim conflict, the aim wins.
