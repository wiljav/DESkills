# Change Management Playbook

## Breaking change flow

1. **Propose** — draft the MAJOR bump with: what breaks, why, migration
   path. Post to the owners' channel.
2. **Notify** — message ALL registered consumers (from the contract's
   `consumers` section) with the notice period (default 2 weeks).
3. **Respond** — give consumers a deadline to reply; unresponsive
   consumers get a reminder after 1 week.
4. **Decide** — owner (or the escalation team) approves the bump with the
   reply record attached.
5. **Implement** — dual-write or additive migration first where feasible.
6. **Publish** — new contract version + changelog entry; consumers
   migrate at their pace.
7. **Verify** — 1 week after: re-run enforcement tests; confirm consumers
   report no regressions.

## Templates

```yaml
# migration note
migration:
  from: "1.1.0"
  to: "2.0.0"
  reason: amount now stored as DECIMAL(12,2) with rounding
  consumer_action: re-parse money fields; no other change
  deadline: "2024-03-01"
```

## Rules

- No silent breaking changes: the commit message and changelog are the
  record.
- Additive first: add `new_field`, deprecate `old_field`, remove later.
- If an SLA break is caused by a contract violation, the producer owes the
  fix — log in the incident runbook (data-quality-incident-runbook).