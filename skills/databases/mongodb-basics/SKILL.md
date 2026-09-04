---
name: mongodb-basics
metadata:
  category: Databases
description: >-
  Models, queries, and integrates MongoDB collections into pipelines:
  document schema design, aggregation queries, change streams, and
  extraction patterns. Use when MongoDB is a source or operational store.
  Don't use for relational modeling (use postgres-basics) or analytics
  workloads (warehouse skills).
allowed-tools:
  - mongosh
  - python
---

# MongoDB Basics

MongoDB stores flexible documents; for data platforms it is a source of
semi-structured data or an operational store. This skill covers modeling,
querying, and getting data out.

## Prerequisites

- A running MongoDB instance (local, Atlas, or self-managed).
- `mongosh` client; `pymongo` for Python work.
- Read-only user for extraction work per the auth skill.

## Safety & Confirmation Tiers

- **Tier R (read-only)**: `find`, `aggregate`, `explain`, collection
  stats.
- **Tier M (mutation)**: writes, index creation, and change-stream
  pipeline setup. Index creation on hot collections impacts writes —
  confirm before applying.

## Workflow

### 1. Inspect the Deployment

```bash
mongosh "mongodb://{user}:{pwd}@{host}:27017/admin" --eval "db.adminCommand({listDatabases:1})"
mongosh ... --eval "db.orders.stats(); db.orders.getIndexes();"
```

### 2. Model Documents

```json
{
  "_id": "ORD-1001",
  "customer_id": "C42",
  "amount": 199.99,
  "created_at": "2024-01-15T10:00:00Z",
  "items": [ { "sku": "A1", "qty": 2, "price": 99.99 } ],
  "status": "paid"
}
```

Rules:

- Embed related sub-documents (items) when read together; reference
  (`customer_id`) when shared/updated elsewhere.
- `_id` is immutable and indexed — choose a natural key or hash.
- Avoid unbounded arrays: they cap document size and complicate sharding.

### 3. Index and Verify

```js
db.orders.createIndex({ customer_id: 1, created_at: -1 });
db.orders.find({ customer_id: "C42", created_at: { $gte: ISODate("2024-01-01") } })
         .explain("executionStats");
```

Rules:

- Index on the filter and sort columns (same rules as SQL, no prefix
  limitation).
- `explain("executionStats")`: `totalDocsExamined` should be far below
  collection size; `nReturned` close to scanned.

### 4. Aggregate for Extraction

```js
db.orders.aggregate([
  { $match: { status: "paid", created_at: { $gte: ISODate("2024-01-01") } } },
  { $unwind: "$items" },
  { $project: { order_id: "$_id", sku: "$items.sku", qty: "$items.qty" } },
  { $group: { _id: "$sku", total_qty: { $sum: "$qty" } } }
]);
```

Rules:

- `$match` FIRST (prunes early, uses indexes); `$unwind` after narrowing.
- Extract at the level the warehouse needs; flatten nested documents in
  the transformation layer, not ad-hoc in consumers.

### 5. Stream Changes (Change Streams)

```js
const pipeline = [{ $match: { "fullDocument.status": "paid" } }];
const stream = db.orders.watch(pipeline, { fullDocument: "updateLookup" });
```

Rules:

- Change streams need replica sets (not standalone).
- Consumer offsets via `resumeToken` — persist it (like Kafka offsets).
- For heavy CDC volume prefer Debezium -> Kafka (kafka-connect).

### 6. Export for Backups/Bulk

```bash
mongodump --uri "mongodb://..." --db analytics --collection orders --out ./dump
mongorestore --uri "mongodb://..." --db analytics ./dump/analytics
```

- Schedule mongodump (or Atlas backups); test restore quarterly.

## Validation

- Index used in explain; docs examined in line with `nReturned`.
- Aggregation returns the expected shape/counts (compare with a sample
  cross-check).
- Change stream delivers events; resumeToken resumes after a restart.
- Restore test passes.

## Definition of Done

- Collection modeling documented (embed vs reference rationale).
- Indexes verified via explain; write impact acceptable.
- Extraction pattern (aggregate or change stream) working.
- Backup + quarterly restore test in place.

## Reference Directory

- [Modeling Patterns](references/modeling.md): embed/reference rules and
  schema evolution.
- [Aggregation & Extraction](references/aggregation.md): pipeline stages
  and flattening patterns.

## Related Skills

- [Kafka Connect](../../ingestion/kafka-connect/SKILL.md): Debezium CDC
  from MongoDB.
- [File Ingestion](../../ingestion/file-ingestion-gcs-s3/SKILL.md):
  alternate extraction paths.
- [dlt Python Ingestion](../../ingestion/dlt-python-ingestion/SKILL.md):
  declarative MongoDB sources.
