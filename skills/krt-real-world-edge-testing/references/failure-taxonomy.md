# Failure Taxonomy

Use the categories that intersect the discovered workflow. Prefer a few high-value cross-boundary cases over exhaustive low-value permutations.

## Input And Representation

- missing, null, empty, or whitespace-only values;
- exact limits and one unit beyond them;
- oversized inputs and long unbroken tokens;
- Unicode normalization, emoji, RTL, mixed scripts, encodings, and malformed binary data;
- unsupported formats, duplicate identifiers, and contradictory records.

## State And Lifecycle

- create, update, rename, move, archive, delete, restore;
- duplicate delivery, stale version, partial completion, and interrupted workflow;
- resource disappearance during processing;
- reconciliation after downtime and idempotency across repeated runs.

## Authentication And Authorization

- missing, invalid, expired, revoked, or rotated credentials;
- insufficient permissions and partial access to related resources;
- cross-tenant or cross-object access;
- credentials exposed through URLs, errors, redirects, or logs.

## Concurrency And Ordering

- duplicate or simultaneous requests;
- out-of-order events and read-after-write timing;
- optimistic-lock conflicts;
- restart during processing and multiple workers claiming the same work;
- updates arriving during reconciliation.

## External Dependencies

- timeout, connection reset, rate limiting, and recovery after outage;
- malformed, partial, stale, non-JSON, or incompatible responses;
- provider authentication and quota failure.

## Infrastructure

- service restart, cold start, partial deployment, and dependency unavailability;
- database, queue, DNS, routing, disk, storage, or schema failure;
- misconfigured environment and bounded resource exhaustion.

## Security And Hostile Content

- prompt, script, markup, path, redirect, metadata, and log injection;
- SSRF-like target selection and secret-disclosure requests;
- oversized decompression and cross-source data confusion;
- untrusted instructions carried through documents, retrieval, jobs, or agents.

Security cases remain defensive validation. Route broader vulnerability assessment or offensive requests to the security workflow and preserve its authorization boundaries.

## Output And Attribution

- missing, wrong, or cross-wired source attribution;
- a correct fact attributed to the wrong source;
- contradictory sources, fabricated values without context, truncation, duplication, and unstable ordering;
- sensitive content in errors, responses, logs, or evidence.

## Performance And Boundedness

- maximum expected corpus, batch, page, queue, or result set;
- worst-case valid input and slow dependency behavior;
- enforced timeouts, retry amplification, memory growth, backlog, truncation, and repeated-run stability.

Performance cases should verify an agreed bound. This skill does not invent a service-level objective or replace a dedicated load-testing program.
