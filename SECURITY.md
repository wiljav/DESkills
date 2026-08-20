# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, **do not** open a public issue.

Email the maintainers directly at `security@example.com` with:

- Affected skill(s) and file(s)
- Description of the vulnerability
- Proof of concept, if available

You should receive a response within 48 hours. If not, follow up.

## Security expectations for skills

- **Never** commit secrets, credentials, private keys, or `.env` files. The CI
  pipeline runs a secret scan on every change.
- **Never** instruct agents to exfiltrate data, escalate privileges beyond
  least-privilege, or disable audit logging.
- Scripts in `scripts/` must be **read-only by default**. Any script that
  creates resources or mutates data must declare a destructive-action tier and
  require explicit user confirmation (see the authoring guide).
- Skills that reference cloud credentials must instruct agents to prefer
  short-lived, scoped credentials (e.g. workload identity, IAM short-lived
  tokens) over long-lived keys.
