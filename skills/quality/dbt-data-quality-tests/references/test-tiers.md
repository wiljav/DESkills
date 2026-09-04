# Test Tiers & Severity Policy

## Tier definitions

| Tier | Severity | Examples | Cadence |
| --- | --- | --- | --- |
| Critical | `error` | PK uniqueness, not-null on PK, FK integrity on facts | every build |
| Standard | `error` | range invariants, business rules | every build |
| Soft | `warn` | distribution, quantile, trend-sensitive | every build + monthly review |

## Rules of thumb

- Facts fail hard; exploratory/intermediate models may warn.
- A warn that fires for 3+ consecutive builds is a fail: escalate it.
- Never downgrade a failing error to warn without a documented reason and a
  follow-up task.
- Thresholds come from history, not guesswork: baseline 4-8 weeks of
  measurements before setting soft-gate bounds.

## Review cadence

- Monthly: re-baseline distribution gates, review warn-fire rates.
- Per-incident: re-evaluate related gates (see incident runbook).
