---
name: streaming-architecture-patterns
metadata:
  category: Streaming
description: >-
  Chooses event-driven, CDC, and lambda/kappa streaming patterns and
  designs the real-time platform: message brokers, processing engines,
  delivery semantics, and failure handling. Use when designing or reviewing
  a streaming architecture. Don't use for operating specific tools (use
  kafka-basics, flink-basics, dataflow-basics) or for batch platform design
  (use data-platform-architecture).
allowed-tools:
  - python
---

# Streaming Architecture Patterns

This skill is the architecture-level guide for real-time data: when
streaming is the right answer, which pattern fits, and how delivery
semantics are chosen.

## Prerequisites

- Requirements: latency targets, volume, and consumer needs (from the
  stakeholders).
- Knowledge of the batch platform (data-platform-architecture) it will
  complement.
- No tooling required — this is a design skill (diagrams and decisions).

## Safety & Confirmation Tiers

- **Tier R (read-only)**: reviewing the existing architecture, comparing
  options, drafting designs.
- **Tier M (mutation)**: recommending or applying architectural changes
  (new brokers, new processing engines, changed semantics). Confirm with the
  platform owner before implementation begins.

## Workflow

### 1. Decide: Stream, Batch, or Both

| Driver | Recommendation |
| --- | --- |
| Latency < 1 min | streaming |
| Volume bursts, replay needed | streaming with bounded retention + batch lakehouse |
| Existing batch marts, no latency demand | batch (do not introduce streaming) |

Rule: streaming adds operational cost; require a concrete latency/UX driver
to justify it.

### 2. Choose the Pattern

| Pattern | Shape | Use |
| --- | --- | --- |
| Event-driven | producers -> broker -> consumers | decoupled services, async reactions |
| CDC | DB -> Debezium -> broker -> lakehouse | syncing operational stores |
| Kappa | single streaming path serves real-time + batch (replay) | uniform processing, simpler ops |
| Lambda | streaming path for real-time + batch path for historical | when replay is too expensive or engines differ |

### 3. Design Delivery Semantics

State them explicitly per pipeline:

| Semantics | Meaning | Cost |
| --- | --- | --- |
| At-most-once | may drop | cheapest, only for non-critical alerts |
| At-least-once | may duplicate | standard; sinks MUST dedup |
| Exactly-once | no drops, no dups | transactional sinks + checkpointing |

Rules:

- Default: at-least-once ingestion + idempotent sinks.
- Exactly-once only where financial/audit accuracy demands it.
- Document the chosen semantics per pipeline in the architecture doc.

### 4. Handle Failure Scenarios

Design for, and document:

- **Broker outage**: retention sizing for replay; consumers must tolerate
  reconnect.
- **Processing failure**: checkpointing + resume (Flink/Dataflow), state
  replay for Kafka Streams.
- **Sink failure**: dead-letter topics; never silently drop.
- **Schema drift**: schema registry + contract review gate (see
  data-contracts).

### 5. Define Observability

Per pipeline: producer lag, consumer lag, processing time, error rate, and
watermark age (for event-time engines). Wire into the data-observability
framework.

## Validation

- Requirements mapped to a pattern with rationale documented.
- Delivery semantics chosen per pipeline and stated.
- Failure scenarios each have a documented recovery path.
- Observability metrics defined for every pipeline.
- Architecture reviewed with the platform owner before implementation.

## Definition of Done

- Stream-vs-batch decision justified by requirements.
- Pattern selected (event-driven/CDC/kappa/lambda) with trade-offs.
- Delivery semantics table completed.
- Failure recovery paths documented.
- Observability plan defined.

## Reference Directory

- [Pattern Comparison](references/pattern-comparison.md): deep trade-off
  matrix.
- [Design Checklist](references/design-checklist.md): the review checklist
  used to audit streaming designs.

## Related Skills

- [Kafka Basics](../../ingestion/kafka-basics/SKILL.md): the broker layer.
- [Flink Basics](../../processing/flink-basics/SKILL.md) and
  [Dataflow Basics](../../processing/dataflow-basics/SKILL.md): processing
  engines.
- [Streaming Analytics Pipeline](../../solutions/streaming-analytics-pipeline/SKILL.md):
  end-to-end build following this design.