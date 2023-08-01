# ERDio

This is CLI utility to generate editable Draw.io ERD from DBML or updating existing diagram.


## Installation

You can install ERDio using pip:

```bash
pip install erdio
```

## Quick start

Assuming you have already installed `dbt` and `dbterd` utility to generate artifacts.

1. Use `dbt` to generate docs.

```bash
$ dbt docs generate

16:15:02  Running with dbt=1.5.3
16:15:03  Registered adapter: postgres=1.5.3
16:15:03  Found 241 models, 492 tests, 4 snapshots, 0 analyses, 850 macros, 0 operations, 18 seed files, 70 sources, 0 exposures, 0 metrics, 0 groups
16:15:03
16:15:12  Building catalog
16:15:12  Catalog written to ./target/catalog.json
```

This will create two artifact files contains:

* `manifest.json` includes all tests and documentation
* `catalog.json` includes the set of all columns in the database



2. Use `dbterd` to generate DBML from dbt artifacts.

```bash
$ dbterd run

2023-07-25 16:16:45,768 - dbterd - INFO - Run with dbterd==1.2.4 (main.py:54)
2023-07-25 16:16:46,359 - dbterd - INFO - ./target/output.dbml (base.py:75)

```

This will create DBML manifest to be used for diagraming.



3. Create new Draw.io diagram.

```bash
erdio run
```
