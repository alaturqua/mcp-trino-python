# Tools and prompts

The assistant picks these tools on its own; you don't call them by name. This page shows what it can do.

Parameters marked *optional* can be left out when `TRINO_CATALOG` / `TRINO_SCHEMA` are set.
Results come back as JSON unless noted otherwise.

## Explore

| Tool                | What it does                                           | Parameters                                       |
| ------------------- | ------------------------------------------------------ | ------------------------------------------------ |
| `show_catalogs`     | List all catalogs                                      | none                                             |
| `show_schemas`      | List the schemas in a catalog                          | `catalog` *optional*                             |
| `show_tables`       | List the tables in a schema                            | `catalog`, `schema_name` *optional*              |
| `show_catalog_tree` | Tree of all catalogs, schemas and tables (can be slow) | none                                             |
| `describe_table`    | Columns and types of a table                           | `table`; `catalog`, `schema_name` *optional*     |
| `show_create_table` | The `CREATE TABLE` statement                           | `table`; `catalog`, `schema_name` *optional*     |
| `show_create_view`  | The `CREATE VIEW` statement                            | `view`; `catalog`, `schema_name` *optional*      |
| `show_stats`        | Column statistics                                      | `table`; `catalog`, `schema_name` *optional*     |

## Query

| Tool                 | What it does                                       | Parameters        |
| -------------------- | -------------------------------------------------- | ----------------- |
| `execute_query`      | Run a SQL statement and return the rows            | `query`           |
| `show_query_history` | Recent queries on the cluster, newest first        | `limit` *optional* |

## Iceberg metadata

All take `table`, plus optional `catalog` and `schema_name`.

| Tool                        | Shows                                                                    |
| --------------------------- | ------------------------------------------------------------------------ |
| `show_table_properties`     | Table properties                                                         |
| `show_table_history`        | When each snapshot became current                                        |
| `show_snapshots`            | Snapshots with operation and change summary                              |
| `show_metadata_log_entries` | Metadata file log                                                        |
| `show_manifests`            | Manifest files; `all_snapshots=true` for every snapshot                  |
| `show_entries`              | Manifest entries; `all_snapshots=true` for every snapshot                |
| `show_partitions`           | Partitions with record counts and sizes                                  |
| `show_files`                | Data files in the current snapshot                                       |
| `show_refs`                 | Branches and tags                                                        |

## Iceberg maintenance

These change tables. Clients that support it ask you before running them, and they are hidden in
[read-only mode](configuration.md#read-only-mode).

| Tool                 | What it does                                       | Parameters                                                        |
| -------------------- | -------------------------------------------------- | ----------------------------------------------------------------- |
| `optimize`           | Compact small data files                           | `table`; `catalog`, `schema_name` *optional*                      |
| `optimize_manifests` | Rewrite and compact manifest files                 | `table`; `catalog`, `schema_name` *optional*                      |
| `expire_snapshots`   | Remove snapshots older than a threshold            | `table`; `retention_threshold` (default `7d`); `catalog`, `schema_name` *optional* |

## Prompts

Prompts are ready-made conversation starters. In Claude Code they show up as slash commands.

| Prompt             | What it does                                                  |
| ------------------ | ------------------------------------------------------------- |
| `explore_data`     | Start exploring a catalog or schema                           |
| `maintain_iceberg` | Discuss which maintenance an Iceberg table needs              |
