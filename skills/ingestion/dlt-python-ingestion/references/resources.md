# Resource & Disposition Patterns

## write_disposition

| Disposition | Behavior | Use |
| --- | --- | --- |
| `append` | always insert | immutable events, logs |
| `replace` | drop + reload | small reference data |
| `merge` | upsert by `primary_key` | mutable entities, CDC-ish loads |

## API pagination helper

```python
@dlt.resource(name="pages")
def pages():
    cursor = None
    while True:
        batch = fetch_page(cursor=cursor, limit=1000)
        if not batch:
            break
        yield batch
        cursor = batch[-1]["id"]
```

Rules:

- Yield batches (lists) of rows — batching reduces load overhead.
- Guard against infinite loops: cap pages, verify cursor advances.

## Multiple resources in one source

```python
@dlt.source
def saas_api():
    return [users(), events(), orders()]
```

Each resource becomes its own table with its own state — but share one
pipeline run for atomicity of the load.

## Schema hints

- `T.DecimalType()`, `T.TimestampType()`, `T.JsonType()`, `T.DateType()`.
- Use hints when inference guesses wrong (e.g. ISO strings vs timestamps).
- Hints live in the resource decorator or a `schema` file — one source of
  typing truth.