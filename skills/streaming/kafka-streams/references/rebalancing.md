# Rebalancing & Recovery

## Rebalance triggers

- New instance joins / instance leaves (crash, scale-down, deploy).
- Topic partition count changes.
- The group re-distributes partitions: tasks move with their state stores
  (via changelog restore).

## During rebalance

- Processing pauses; `rebalance.max.wait.ms` bounds waiting.
- Large state = slow restore: monitor restore progress
  (`kafka-consumer-groups --describe` + app logs).

## Safe recovery playbook

1. Stop the app (SIGTERM, wait for graceful shutdown).
2. Fix the root cause (code/data).
3. Decide: replay from earliest (input replayable) vs reset state.
   - Replay: `--to-earliest` on input topics; state rebuilds deterministically.
   - Reset: only when state is corrupted AND replay is impossible.
4. Restart; verify offsets/lag and aggregations against the expected
   baseline.

## Deployment discipline

- Rolling deploys one instance at a time (minimizes rebalances).
- Pin the app version to the topic/serde versions; schema drift across
  deploy = corrupt state.
