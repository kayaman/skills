---
name: rfc2119
description: Enforces RFC 2119 (BCP 14) requirement level keywords in documentation, specifications, and technical writing. Ensures correct usage of MUST, SHOULD, MAY and related terms as defined by RFC 2119 and clarified by RFC 8174. Use when writing or reviewing specs, RFCs, ADRs, design docs, API contracts, or any normative technical document.
---

# RFC 2119 — Requirement Level Keywords

This skill enforces the correct use of requirement level keywords as defined in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119) and clarified by [RFC 8174](https://datatracker.ietf.org/doc/html/rfc8174) (together forming BCP 14).

## When to Use This Skill

Use this skill when writing or reviewing:

- Technical specifications and standards
- Architecture Decision Records (ADRs)
- API contracts and interface documentation
- Design documents with normative requirements
- RFCs or RFC-style documents
- Configuration or policy documents with enforceable rules
- Any document that needs unambiguous requirement levels

## Keywords and Their Meanings

### Absolute Requirements

| Keyword      | Meaning                                       |
| ------------ | --------------------------------------------- |
| **MUST**     | An absolute requirement of the specification. |
| **REQUIRED** | Synonym for MUST.                             |
| **SHALL**    | Synonym for MUST.                             |

### Absolute Prohibitions

| Keyword       | Meaning                                       |
| ------------- | --------------------------------------------- |
| **MUST NOT**  | An absolute prohibition of the specification. |
| **SHALL NOT** | Synonym for MUST NOT.                         |

### Recommendations

| Keyword         | Meaning                                                                                                                                             |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **SHOULD**      | Valid reasons MAY exist to ignore this item, but the full implications MUST be understood and carefully weighed before choosing a different course. |
| **RECOMMENDED** | Synonym for SHOULD.                                                                                                                                 |

### Discouraged

| Keyword             | Meaning                                                                                                                                           |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| **SHOULD NOT**      | Valid reasons MAY exist when the behavior is acceptable or useful, but the full implications SHOULD be understood and the case carefully weighed. |
| **NOT RECOMMENDED** | Synonym for SHOULD NOT.                                                                                                                           |

### Truly Optional

| Keyword      | Meaning                                                                                                                                                   |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **MAY**      | The item is truly optional. Implementations that do not include the option MUST be prepared to interoperate with implementations that do, and vice versa. |
| **OPTIONAL** | Synonym for MAY.                                                                                                                                          |

## RFC 8174 Clarification — Capitalization Rule

Per RFC 8174, **only UPPERCASE usage** of these keywords carries the special RFC 2119 meaning. When written in lowercase or mixed case, the words have their normal English meaning and are NOT governed by this specification.

- `MUST` → normative requirement (RFC 2119 meaning)
- `must` → ordinary English usage (no special meaning)
- `Must` → ordinary English usage (no special meaning)

## Boilerplate Text

Documents following BCP 14 MUST include this paragraph near the beginning:

> The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [BCP 14](https://datatracker.ietf.org/doc/html/bcp14) [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119) [RFC 8174](https://datatracker.ietf.org/doc/html/rfc8174) when, and only when, they appear in all capitals, as shown here.

## Rules for Applying Keywords

When writing or reviewing documents, follow these rules:

### 1. Use Keywords Sparingly

Keywords MUST only be used where actually required for interoperation or to limit behavior with potential for causing harm. They MUST NOT be used to impose a particular method on implementors when the method is not required for interoperability.

### 2. Choose the Right Level

- Use **MUST** / **MUST NOT** only for absolute requirements and prohibitions. Violations mean the implementation is non-conformant.
- Use **SHOULD** / **SHOULD NOT** when exceptions are legitimate but rare. The author expects compliance in the vast majority of cases.
- Use **MAY** when a feature is truly optional and both inclusion and omission are equally valid choices.

### 3. Always Capitalize When Normative

When a keyword conveys a BCP 14 requirement level, it MUST be written in ALL CAPITALS. When the word is used in its ordinary English sense, it MUST NOT be written in ALL CAPITALS and SHOULD follow normal English capitalization rules.

**Correct:**
> Clients MUST include the `Authorization` header in every request.
> The server must be running before tests can execute.

**Incorrect:**
> Clients must include the `Authorization` header in every request. *(ambiguous — is this normative?)*
> The server MUST be running before tests can execute. *(over-use — this is not a spec requirement)*

### 4. Elaborate Security Implications

Authors SHOULD document the security implications of not following a MUST or SHOULD, or of doing something marked MUST NOT or SHOULD NOT. Most implementors will not have had the benefit of the experience and discussion that produced the specification.

### 5. Pair Prohibitions with Alternatives

When using MUST NOT or SHOULD NOT, the document SHOULD provide guidance on what to do instead.

**Good:**
> Passwords MUST NOT be stored in plaintext. They MUST be hashed using a current, approved algorithm such as bcrypt or Argon2.

**Insufficient:**
> Passwords MUST NOT be stored in plaintext.

## Checklist for Document Review

When reviewing a document for RFC 2119 compliance:

- [ ] The BCP 14 boilerplate paragraph is present near the beginning of the document
- [ ] Keywords are ONLY in ALL CAPS when conveying normative meaning
- [ ] Lowercase uses of "must", "should", "may", etc. do not carry normative intent
- [ ] MUST / MUST NOT are reserved for absolute requirements and prohibitions
- [ ] SHOULD / SHOULD NOT are used where exceptions are possible but discouraged
- [ ] MAY / OPTIONAL are used for truly optional features
- [ ] Keywords are used sparingly and only where necessary
- [ ] Security implications of ignoring MUST/SHOULD items are documented
- [ ] MUST NOT / SHOULD NOT are paired with alternative guidance where applicable

## References

- [RFC 2119 — Key words for use in RFCs to Indicate Requirement Levels](https://datatracker.ietf.org/doc/html/rfc2119) (March 1997)
- [RFC 8174 — Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words](https://datatracker.ietf.org/doc/html/rfc8174) (May 2017)
- [BCP 14](https://datatracker.ietf.org/doc/html/bcp14) (comprises RFC 2119 + RFC 8174)
