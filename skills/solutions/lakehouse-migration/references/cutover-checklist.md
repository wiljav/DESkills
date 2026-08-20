# Cutover Checklist

## Day before

- [ ] Final wave validated; all tables in the wave pass parity checks.
- [ ] Consumer list notified (owners + downstream dashboards).
- [ ] Rollback procedure printed (how to point consumers back).

## Cutover day (per table group)

1. Freeze warehouse writes (confirm the freeze with the source owner).
2. Run the catch-up load into the lakehouse.
3. Run validation: counts + checksums must match exactly.
4. Switch consumers: dbt profiles, BI connections, app configs.
5. Smoke-test: one dashboard per consumer team.
6. Record the switch time + checksums in the migration log.

## Post-cutover

- 24h: watch freshness + anomaly alerts (data-observability).
- 1 week: confirm no rollback requests; warehouse read-only.
- 2 weeks: decommission window — DROP with owner confirmation.

## Rollback trigger

- Validation mismatch at step 3 (do NOT cut over).
- Consumer failure within 24h not fixed in 2h: point connections back to
  the warehouse, re-freeze lakehouse writes, investigate.