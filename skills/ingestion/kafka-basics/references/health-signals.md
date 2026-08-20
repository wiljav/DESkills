# Cluster Health Signals

## Consumer lag

```
LAG = latest offset - committed offset
```

- Persistent growth = consumer throughput < producer throughput.
- Remedies: more partitions + more consumers, faster consumer logic,
  dedupe/aggregate upstream.
- Lag beyond retention = silent data loss for that consumer.

## Under-replicated partitions

`ISR < ReplicationFactor` means replicas fell out of sync.

Diagnosis:

```bash
kafka-topics --bootstrap-server {broker} --describe --under-replicated-partitions
```

Fix: broker disk/CPU pressure, network issues, or broker failure. Resolve
the broker issue; ISR recovers automatically.

## Leader imbalance

`kafka-topics --describe` shows leaders concentrated on few brokers ->
hotspot.

Fix: `kafka-reassign-partitions` with a balanced plan; confirm the plan
before executing (mutation, confirmed).

## Broker metrics worth tracking

- Request latency p99, produce request rate.
- Under-replicated partitions count.
- Disk utilization per broker.
- Network throughput vs broker NIC limits.