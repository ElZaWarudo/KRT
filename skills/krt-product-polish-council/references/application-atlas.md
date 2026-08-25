# Versioned Application Atlas

## Contents

1. Purpose and authority
2. Freshness preflight
3. Intent interview
4. Cartographer procedure
5. File schema
6. Coverage gate
7. Size-based strategy
8. Maintenance

## 1. Purpose and Authority

Create a shared factual map of what the application intends to do and what it actually exposes. Store it at `docs/product/application-atlas.md` by default.

Always separate:

- **Declared**: intent confirmed by an authoritative source.
- **Observed**: behavior reproduced in the application or demonstrated by direct evidence.
- **Code**: a capability or route present in code or configuration but not reproduced.
- **Inferred**: a useful hypothesis awaiting confirmation.
- **Unverified**: a known area that could not be examined.

The atlas is not an audit report. Do not include labels such as “bad,” severities, or recommendations. Record differences between intent and observation as neutral facts; the council will decide later whether they constitute findings.

## 2. Freshness Preflight

The first action when using the skill is to check the atlas against the current commit.

The frontmatter stores:

- `verified_source_commit`: the commit present during the last complete exploration;
- `application_fingerprint`: SHA-256 of the covered Git object listing in that commit;
- `tracked_paths`: paths whose changes can make the atlas stale;
- `excluded_paths`: artifacts that do not describe the application, including the atlas itself;
- `last_verified_at`: ISO date of the last substantive verification.

Run:

```bash
rtk python3 <skill-path>/scripts/check_atlas_freshness.py \
  --atlas docs/product/application-atlas.md
```

Interpret the result:

- `fresh`: covered content matches `HEAD` and no relevant uncommitted changes exist;
- `stale`: at least one covered file changed or the working tree contains relevant changes;
- `missing`: the atlas does not exist;
- `invalid`: metadata is missing or the schema cannot be read.

Do not require `verified_source_commit` to equal `HEAD`: a commit that adds the atlas itself changes the SHA and creates impossible self-reference. Require the covered-tree fingerprint to match instead. Use the commit for provenance and the fingerprint as proof.

To obtain the fingerprint to copy into the atlas after exploring a clean commit:

```bash
rtk python3 <skill-path>/scripts/check_atlas_freshness.py \
  --atlas docs/product/application-atlas.md \
  --compute
```

## 3. Intent Interview

Review existing documents first. Ask only what remains unanswered: omit every fact already declared and reformulate compound questions to avoid asking for it again. Ask one short round and wait before fixing declared intent.

Base questions:

1. Who is the primary user, and what problem are they trying to solve?
2. What task must they be able to complete confidently in a normal session?
3. What is the primary action, and what signal confirms successful completion?
4. Which roles, platforms, or usage contexts remain undocumented but are actually supported?
5. Which errors or outcomes would be unacceptable: loss of work, exposure, charges, publication, lockout, or something else?
6. Which boundaries, omissions, or points of friction are deliberate and must not be interpreted as defects?
7. Which flows are most frequent, valuable, or critical to the business and the user?

Record every answer with its source and date. If two authoritative sources conflict, do not resolve the conflict by intuition: record it and request a decision.

If the user asks to continue without answering, record provisional answers as `Inferred`. Do not use those inferences to issue P0/P1 findings for product misalignment.

## 4. Cartographer Procedure

Explore breadth first, then depth:

1. Inventory platforms, entry points, routes, windows, tabs, and primary surfaces.
2. Identify actors, roles, permissions, session states, and differences by plan or tenant.
3. Walk global and local navigation; record entries, exits, return behavior, and deep links.
4. Define important flows with preconditions, primary action, outcome, modified data, and recovery.
5. Catalog the happy, empty, loading, progress, success, validation, error, offline, permission, expired-session, extreme-content, and high-volume states for each surface when applicable.
6. Map persistence: drafts, autosave, selection, filters, scroll position, history, and cross-session state.
7. Record integrations, asynchronous jobs, files, notifications, payments, and other external boundaries.
8. Flag destructive, irreversible, financial, public, or sensitive actions without executing them outside a safe environment.
9. Record input and platform conventions: keyboard, touch, screen reader, back/forward, deep links, windows, files, and responsive behavior.
10. Maintain a coverage ledger with evidence and gaps.

Prefer behavior reproduced at runtime. Use routes, components, tests, and configuration to find hidden areas; use documentation to explain intent. Do not copy secrets or personal data into the atlas.

## 5. File Schema

Use this structure and preserve IDs across versions:

```markdown
---
atlas_schema_version: 1
status: "draft"
verified_source_commit: "<full-sha>"
application_fingerprint: "sha256:<digest>"
tracked_paths: ["app", "src", "config", "docs/product-requirements"]
excluded_paths: ["docs/product/application-atlas.md", "docs/audits/"]
last_verified_at: "YYYY-MM-DD"
---

# Application Atlas

## 1. Intent
- Product promise [Declared]:
- Primary user [Declared]:
- Primary job [Declared]:
- Primary action [Declared]:
- Success signal [Declared]:
- Deliberate constraints [Declared]:
- Unacceptable outcomes [Declared]:
- Sources:

## 2. Platforms and environments
| ID | Platform/environment | Supported | Inputs | Constraints | Evidence |

## 3. Actors and permissions
| ID | Actor/role | Goal | Can | Cannot | Evidence |

## 4. Surface and navigation map
| ID | Surface | Entry | Exits/return | Roles | Route/window | Evidence |

## 5. Flow registry
| ID | Flow | Actor | Frequency | Consequence | Entry | Completion | Surfaces | Evidence |

### FLOW-01 — <name>
- Preconditions:
- Before:
- During:
- After:
- Failure and recovery:
- Real conditions:
- Data written or exposed:
- Context that must survive:
- Evidence:

## 6. State catalog
| ID | Surface/flow | State | Expected behavior | Observed/code/unverified | Evidence |

## 7. Data and context lifecycle
| Data/context | Created | Persisted | Restored | Cleared | Risk | Evidence |

## 8. External and asynchronous boundaries
| Boundary | Trigger | Pending signal | Success | Failure/retry | Evidence |

## 9. Destructive and high-consequence actions
| Action | Consequence | Reversible | Protection | Safe test path | Evidence |

## 10. Content and scale envelopes
| Surface | Empty | Typical | Long/extreme | High volume | File/input limits | Evidence |

## 11. Platform, input and accessibility expectations
| Platform/flow | Keyboard | Touch | Focus | Back/deep link | Reduced motion | Assistive tech | Evidence |

## 12. Coverage ledger
| Item | Status | Evidence | Last checked | Gap/next probe |

## 13. Open intent questions and conflicts
- <question or conflict; source; owner>

## 14. Change log
- YYYY-MM-DD: <factual atlas change and reason>
```

Use `status: "validated"` only after passing the coverage gate. Use `status: "stale"` as soon as a relevant change has not yet been mapped.

## 6. Coverage Gate

Convene the council only when:

- the promise, user, job, primary action, and success signal are declared or marked as hypotheses;
- every known platform and role has a disposition;
- every reachable in-scope surface appears on the map;
- every primary or high-consequence flow has an entry, completion, data, states, and recovery path;
- permissions, session behavior, integrations, and destructive actions have coverage or an explicit gap;
- samples exist for empty, loading, error, extreme-content, volume, viewport, and input conditions when applicable;
- the ledger distinguishes `covered`, `partial`, `unverified`, and `out-of-scope`;
- the fingerprint matches the current commit and no relevant uncommitted changes exist.

If evidence is missing, the Lead may continue only with reduced scope and must declare the limitation. Never present a partial sample as a comprehensive audit.

## 7. Size-Based Strategy

- **Small application**: cover every reachable surface, role, and state.
- **Medium application**: cover every surface; examine all primary and high-consequence flows in depth.
- **Large application**: inventory the full breadth; go deep based on risk and representativeness, including at least one flow per role, platform, interaction pattern, and critical integration.

“Every nook and cranny” means every known area has a coverage disposition, not that impossible or inaccessible combinations were claimed as executed.

## 8. Maintenance

Update the atlas in the same change that modifies:

- routes, navigation, or surfaces;
- roles, permissions, or session states;
- a flow's entry, outcome, or recovery;
- persistence, drafts, or preserved context;
- integrations or asynchronous jobs;
- supported platforms or input conventions;
- data, file, or volume limits;
- product intent or deliberate constraints.

Preserve unaffected IDs and rows. Add a short change-log entry. Recalculate the fingerprint from a clean commit and run the preflight before another audit.
