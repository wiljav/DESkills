# Agent Integrations

Skills are agent-harness-agnostic: each skill is a directory with a `SKILL.md`
entry point, optional `references/`, `scripts/`, and `assets/`. Harnesses load
them differently.

## Loading a skill directly

Point the harness at a skill directory:

- **opencode**: reference the skill path in your config (or clone the repo and
  add `skills/<domain>/<name>` to your skill roots).
- **Claude Code / Codex / Antigravity CLI**: install via the marketplace
  manifests shipped in this repo (see below).

## Marketplace manifests

- `.claude-plugin/marketplace.json` — Claude Code plugin marketplace
  (`claude plugin marketplace add <this-repo>`).
- `.agents/plugins/marketplace.json` — Codex plugin marketplace.

Manifests are validated by `make marketplace`. Plugins may be vendored as git
submodules under `plugins/` (see `.gitmodules`); upstream repos remain the
source of truth.

## MCP servers

Data platforms are commonly exposed to agents via Model Context Protocol (MCP)
servers. The `mcp-servers-for-data` skill documents connecting warehouse,
catalog, and orchestration MCP servers. Any MCP server referenced by a skill
must be listed in that skill's `allowed-tools`.

## Verification

After wiring a harness, verify with:

```bash
make ci
```

If you add a harness-specific integration, document it in this file and add
any required manifest to `make marketplace`.
