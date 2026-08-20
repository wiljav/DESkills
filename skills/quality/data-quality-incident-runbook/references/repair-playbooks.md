# Repair Playbooks

## Playbook 1: Re-run the producing pipeline (preferred)

When the code fix is in and the pipeline is idempotent:

1. Confirm the code fix is deployed to the target environment.
2. Re-run the affected window/partition (orchestrator backfill or
   re-trigger).
3. Verify: violated invariant passes; counts match history.

Pros: verifies fix, clean data, no ad-hoc SQL. Cons: needs idempotency.

## Playbook 2: Targeted SQL repair

Only when re-run is impossible (source gone, window too old, cost):

1. Write the repair as a reviewed SQL script: select affected rows -> show
   the diff -> apply.
2. Count before/after; sample-verify 100 rows.
3. Run with `BEGIN; ... COMMIT;` in a transaction where the warehouse
   supports it.

Rules: NEVER `UPDATE` without a WHERE on the affected keys; NEVER repair
with data you cannot source from history.

## Playbook 3: Snapshot restore

Only with a verified good snapshot and consumer agreement:

1. Restore the asset from the snapshot to a `_restore` staging name first.
2. Validate invariants + counts on the staged restore.
3. Swap (rename) and notify consumers.

Rules: snapshot restore replaces ALL data — confirm nothing newer than the
snapshot matters; re-apply any legitimately newer rows afterwards if
needed.

## Verification checklist (all playbooks)

- [ ] Invariant that fired the incident passes.
- [ ] Row count within expected bounds (compare to pre-incident history).
- [ ] Sample of 100+ rows manually reviewed.
- [ ] Consumers' downstream runs green.
- [ ] Monitoring shows the window closed.