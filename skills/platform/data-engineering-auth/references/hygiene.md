# Credential Hygiene

## Detecting leaked secrets

Before finishing any task that touched credentials, scan the working tree:

```bash
grep -rn "BEGIN .* PRIVATE KEY" --include="*" . 2>/dev/null
grep -rn "aws_secret_access_key" --include="*.json" --include="*.yaml" --include="*.yml" --include="*.env*" . 2>/dev/null
grep -rn "api[_-]key[[:space:]]*[:=]" --include="*.py" --include="*.sh" . 2>/dev/null
```

CI also runs gitleaks on every push; a local scan is faster for catching
issues before commit.

## Rotating leaked credentials

If a scan finds real secrets in a committed file:

1. Revoke immediately (key deletion, credential version invalidation).
2. Remove the secret from git history (`git filter-repo` or BFG).
3. Rotate to a fresh short-lived credential following the skill workflow.
4. Add a `.gitignore` pattern so the path can never be committed again.

## Enforcing hygiene in skill scripts

- Scripts MUST read secrets from environment variables via `os.environ` and
  fail fast with a clear message when a required variable is missing.
- Scripts MUST NOT print full secrets; log only the last 4 characters for
  correlation.
- Any temp credential file MUST be removed in a `finally`/cleanup step.
