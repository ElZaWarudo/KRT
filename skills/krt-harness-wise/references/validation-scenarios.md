# Validation Scenarios

Use these prompts and expectations to forward-test Harness Wise behavior.

## Create New Harness

Prompt:

```text
Use krt-harness-wise to prepare a harness for adding invoice export.
```

Expected:

- Finds initialization context.
- Writes or proposes `docs/harnesses/invoice-export.md` depending on confidence.
- Does not scan the whole source tree.
- Validates the harness structure.

## Diagnose Existing Harness

Prompt:

```text
Use krt-harness-wise to improve docs/harnesses/invoice-export.md.
```

Expected:

- Runs diagnosis before patch/regeneration.
- Reports findings first.
- Applies a minimal patch when the harness is salvageable.

## Regenerate Weak Harness

Input harness lacks objective, source ranking, and initialization context.

Expected:

- Verdict is `Regenerate recommended`.
- Does not silently patch around a misleading foundation.

## Ambiguous Scope

Prompt:

```text
Use krt-harness-wise for the billing thing.
```

Expected:

- Asks one focused question before writing.

## Deprecated Surface Check

Expected:

- The active skill contract does not present generic docs trimming, skill audit, or broad repo intelligence as first-class behavior.
