# Storage Classes & Tiers

## GCS

| Class | Availability | Retrieval | Use |
| --- | --- | --- | --- |
| Standard | high | instant | active pipeline data |
| Nearline | high | instant (min 30d) | monthly access |
| Coldline | high | instant (min 90d) | quarterly access |
| Archive | low | ~minutes-hours | compliance archives |

## AWS S3

| Class | Retrieval | Min duration | Use |
| --- | --- | --- | --- |
| Standard | instant | - | active data |
| Intelligent-Tiering | instant | - | unknown access patterns |
| Standard-IA | instant | 30d | infrequent reads |
| Glacier Instant | ~ms | 90d | rare reads |
| Glacier Flexible | min-hours | 90d | archives |
| Glacier Deep Archive | 12h+ | 180d | compliance |

## Selection rules

- Choose by ACCESS PATTERN, not by data age alone.
- Lifecycle moves data down the tiers as access cools (see the skill
  workflow); moving up tiers costs retrieval fees.
- Compute engines reading nearline/coldline pay per-request retrieval on
  some clouds — keep the active working set on standard.