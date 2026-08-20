# Contract Sections Explained

## schema

- Field-level: name, type, required, semantic description.
- The semantic note is what turns "amount: DECIMAL" into "gross order
  value in USD" — without it, consumers guess.
- Partitioning/freshness fields belong here too (what keys time travel /
  incremental reads).

## quality

- Measurable, ideally automated: thresholds, not vibes ("null_rate < 1%",
  not "low nulls").
- Each promise maps to a concrete test (GE expectation or dbt test) —
  enforceable promises only.

## availability

- SLAs: uptime, recovery time, backup cadence.
- Realistic promises: an SLA nobody can meet is worse than none.

## semantics

- dedup keys, update semantics (append-only vs upsert), retention.
- The source of truth for "how do I read this table correctly".

## ownership

- Named team + channel: disputes go to the owner; consumers escalate here.
- Without owners, contracts rot — the first question on any incident is
  "who owns this?"