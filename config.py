"""Pipeline configuration: paths, logging, and source settings."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
LOGS_DIR = BASE_DIR / "logs"


CONFIG = {
    "input_dir": BASE_DIR / "data" / "raw",
    "output_dir": BASE_DIR / "data" / "processed",
    "crm_api_url": "https://api.shopstream.example.com/v2/customers",
    "crm_api_key": "sk-xxxx",          # Use environment variable in production
    "valid_regions": ["US", "EU", "APAC"],
    "email_regex": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "quality_threshold": 0.95,         # 95% of records must pass each check
    "source_priority": {"crm": 1, "website": 2, "erp": 3, "marketing": 4},
}

for d in [CONFIG["input_dir"], CONFIG["output_dir"]]:
    d.mkdir(parents=True, exist_ok=True)
