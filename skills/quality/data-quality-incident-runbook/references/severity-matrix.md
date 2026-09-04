# Severity Matrix

| Severity | Impact | Response | Escalation |
| --- | --- | --- | --- |
| SEV-1 | Tier-1 marts wrong; consumers blocked; regulatory/financial impact | immediate mitigation; block consumers; page on-call | exec + data platform lead |
| SEV-2 | non-critical assets wrong; SLA at risk | mitigate same day; owner leads | data platform lead |
| SEV-3 | gates failing, no consumer impact | fix next business day; monitor | owner only |

## Escalation rules

- SEV-1: escalate if not mitigated in 1 hour.
- SEV-2: escalate if not fixed in 1 business day.
- Any incident with a data-repair step: escalation required for approval of
  the repair script.

## Communication

- SEV-1: incident Slack channel + email.
- SEV-2: owning team channel.
- SEV-3: issue tracker entry.

Every severity gets a written post-mortem entry — even false alarms (they
document monitor tuning).
