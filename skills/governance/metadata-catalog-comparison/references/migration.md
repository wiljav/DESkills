# Migration Notes

## Leaving a legacy catalog

1. Export everything: entities, schemas, lineage, ownership, tags.
2. Re-create ownership/glossary in the new tool (semi-manual; the data
   exists in tickets/HR systems if not exported).
3. Point ingest recipes at the new endpoint; run both in parallel for 2
   weeks.
4. Retire the old catalog to read-only for one quarter (search still
   finds legacy datasets).
5. Delete read-only instance after the quarter — unless compliance
   requires retention.

## Pitfalls

- Lineage loss: many legacy tools store lineage in proprietary formats —
  export edges explicitly, not just entities.
- Ownership drift: assign the SAME owners in the new tool before
  migration, or the catalog starts orphaned.
- Quality history: GE/dbt results often don't migrate; keep the old
  instance's dashboards until the new one accumulates history.
