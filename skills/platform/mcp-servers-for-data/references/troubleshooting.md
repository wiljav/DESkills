# Troubleshooting MCP

## Server fails to start

| Symptom | Cause | Fix |
| --- | --- | --- |
| `command not found: uvx` | uv tool missing | install uv per the stack-setup skill |
| `ModuleNotFoundError` | broken package version | pin a known-good version: `uvx {pkg}=={version}` |
| exits silently | missing env var | export the documented env var names, then re-register |
| `port already in use` | second instance | stop the stale process or switch the port |

## Auth errors from tools

- `PERMISSION_DENIED` / `AccessDenied`: the identity backing the MCP server
  lacks the role. Follow the auth skill to impersonate a service account or
  assume a role with the required scope, then restart the server (it caches
  credentials at startup).
- `EXPIRED_TOKEN`: short-lived token expired mid-session. Re-export and
  restart the server; keep sessions under the token lifetime.

## Tool not listed

1. Confirm the server process is running (`ps`, server logs).
2. Confirm the harness config has the right `command`/`args` (typos in args
   are the most common cause).
3. Restart the harness session after re-registering; many clients only
   enumerate tools at session start.
4. Check the server's own tool list (e.g. `{server} tools`) to verify the
   tools exist before blaming the client.

## Behavior notes

- Write tools may be hidden behind an explicit flag (`--allow-write`). Leave
  it off unless the session requires mutations.
- Keep MCP servers on the same network as the data platform (VPC) for
  production debugging; local sessions generally cannot reach private
  endpoints.