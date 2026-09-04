# Schema Change Policy

## Per-stream policies

| Policy | Behavior | Use |
| --- | --- | --- |
| `propagate_columns` | add new columns | default for evolving sources |
| `propagate` | add + rename/change types (destructive-capable) | only with contract review |
| `block` | fail the sync on change | contract-pinned tables |
| `discard` | drop the change silently | never for consumer tables |

## Decision flow

1. Detect: check the connection's detected schema vs last saved schema.
2. Classify: added column (safe) vs renamed/type-changed (breaking).
3. Breaking changes: notify the contract owner (see data-contracts); block
   or coordinate before propagating.
4. After propagation, verify downstream models still compile (dbt) before
   enabling the next sync.

## Contract integration

- Pin critical tables with `block` + contract checks in the quality layer.
- Every propagated breaking change triggers the data-contracts workflow:
   owner review -> version bump -> consumer migration window.
