# Distribution & Sort Design

## DISTSTYLE matrix

| Style | Use |
| --- | --- |
| `KEY` | fact tables joined on a common key; best for large joins |
| `EVEN` | small tables, or when no natural distkey exists |
| `ALL` | small dimension tables copied to every slice (kills broadcast) |

Rules:

- Joins are local when both sides share the same distkey; mismatched keys
  force `DS_DIST` (data redistribution) — expensive on large joins.
- Distkey choice is nearly permanent: changing it requires table rebuild.

## SORTKEY mechanics

- Compound sort: `SORTKEY (a, b)` — best when queries filter on `a` and
  `a AND b` (prefix matching).
- Interleaved sort: `SORTKEY INTERLEAVED (a, b)` — equal-weight filters on
  multiple columns; costs more during VACUUM.
- Zone maps: sort order lets Redshift skip blocks outside the filter range —
  the pruning mechanism.

## Encoding notes

- `zstd`: good default for strings/numbers; `az64`: best for integers/dates.
- Raw: for high-cardinality random values (no compressible pattern).
- Wrong encodings show as `ENCODE raw` with poor compression in
  `SVV_TABLE_INFO` — review at design time.