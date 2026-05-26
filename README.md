# my_pipeline

ETL pipeline skeleton: ingest → clean → validate → export.

## Project layout

```
my_pipeline/
├── pipeline.py              # Entry point
├── config.py                # All configuration
├── ingest.py                # Source-specific ingestion
├── clean.py                 # Cleaning functions
├── validate.py              # Data quality checks
├── export.py                # Output writing
├── utils.py                 # Shared helpers
├── tests/
│   ├── test_clean.py
│   └── test_validate.py
├── data/
│   ├── raw/                 # Never modify
│   └── processed/           # Pipeline outputs
├── logs/
├── requirements.txt
└── README.md
```

## Conventions

- **Never edit** files under `data/raw/` — treat it as immutable source data.
- Write pipeline outputs to `data/processed/`.
- Logs are written under `logs/` (log files are gitignored).

## Setup

From the `python-labs` repo root:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r my_pipeline/requirements.txt
```

## Run (after implementation)

```powershell
python my_pipeline/pipeline.py
```

## Test

```powershell
pytest my_pipeline/tests
```
