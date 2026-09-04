# Macro Patterns

## Dispatch (cross-adapter macros)

```jinja
{% macro cast_string_to_date(column_name) -%}
  {{ return(adapter.dispatch('cast_string_to_date')(column_name)) }}
{%- endmacro %}

{% macro default__cast_string_to_date(column_name) %}
  cast({{ column_name }} as date)
{% endmacro %}

{% macro bigquery__cast_string_to_date(column_name) %}
  parse_date('%Y-%m-%d', {{ column_name }})
{% endmacro %}
```

Dispatch lets a macro support multiple warehouses without conditional soup.

## Hooks

- `on-run-start`/`on-run-end` in `dbt_project.yml` for session setup
  (e.g. `SET TIMEZONE`), warehouse-specific and model-scoped via
  `pre-hook`/`post-hook` on models.
- NEVER put credentials or destructive ops in hooks; hooks run automatically
  and silently.

## Portability rules

- Use `current_timestamp()` from dbt (`{{ current_timestamp() }}`), not
  warehouse-specific functions.
- Wrap warehouse-specific SQL behind dispatch with `default__` fallback.
- Test macros on at least two adapters before publishing to a package.

## Docs blocks

```jinja
{% docs percent_change %}
  Computes percentage change between two measures.
  Returns null when the base is zero.
{% enddocs %}
```

Reference in YAML with `{{ doc('percent_change') }}` so generated docs
explain the macro.
