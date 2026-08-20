# Patterns Catalog

## Common patterns

| Type | Pattern (PCRE) | Notes / false positives |
| --- | --- | --- |
| Email | `^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$` | low false positives; confirm domains |
| Phone (US) | `^\+?1?[ -]?\(?\d{3}\)?[ -]?\d{3}[ -]?\d{4}$` | matches some order IDs — confirm |
| SSN | `^\d{3}-\d{2}-\d{4}$` | high signal when column named ssn |
| Credit card | `^(4\d{12}(?:\d{3})?\|5[1-5]\d{14}\|3[47]\d{13})$` | Luhn-check before confirming |
| IP | `^(?:\d{1,3}\.){3}\d{1,3}$` | server logs, not PII — classify by context |
| Name | `^[A-Z][a-z]+ [A-Z][a-z]+$` | huge false-positive rate; use column names |
| DOB | `^\d{4}-\d{2}-\d{2}$` | check column semantics |

## Column-name signals

- `ssn`, `email`, `phone`, `card`, `dob`, `passport`, `national_id`,
  `address`, `ip`, `token` — strong names (but never classify by name
  alone).

## Workflow rules

- Scan a representative sample (>=10k rows or 5%).
- Confirm with a human + `SELECT DISTINCT` eyeball on candidates.
- Re-scan after schema changes: new columns silently add PII.