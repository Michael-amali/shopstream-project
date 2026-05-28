import pandas as pd
import json
import numpy as np
from pathlib import Path
from utils import logger
from config import CONFIG

STANDARD_SCHEMA = [
    "email", "first_name", "last_name", "phone", "region",
    "registration_date", "opt_out", "source"
]

def ingest_website_csv(filepath: Path) -> pd.DataFrame:
    logger.info(f"Ingesting website CSV: {filepath}")
    df = pd.read_csv(
        filepath,
        encoding="iso-8859-1",
        dtype={"Phone": str},
        parse_dates=["Registration Date"],
        na_values=["", "N/A", "null", "NULL", "none", "NaN"],
    )
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[^\w]", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
        .str.strip("_")
    )
    df = df.rename(columns={
        "customeremail": "email",
        "first_name": "first_name",
        "last_name": "last_name",
        "registration_date": "registration_date",
        "optout": "opt_out",
    })
    test_mask = df["email"].str.contains(r"@test\.shopstream\.com$", na=False, case=False)
    removed = test_mask.sum()
    df = df[~test_mask].copy()
    logger.info(f"  Removed {removed} test accounts")
    df["source"] = "website"
    logger.info(f"  Ingested {len(df)} records from website CSV")
    return df

def ingest_crm_json(filepath: Path) -> pd.DataFrame:
    logger.info(f"Ingesting CRM JSON: {filepath}")
    raw = json.loads(filepath.read_text())
    df = pd.json_normalize(raw["customers"], sep="_")
    df = df.rename(columns={
        "profile_first_name": "first_name",
        "profile_last_name": "last_name",
        "registration_date": "registration_date",
    })
    df["registration_date"] = pd.to_datetime(df["registration_date"], errors="coerce")
    df["source"] = "crm"
    logger.info(f"  Ingested {len(df)} records from CRM JSON")
    return df

def ingest_erp_fixed_width(filepath: Path) -> pd.DataFrame:
    logger.info(f"Ingesting ERP fixed-width: {filepath}")
    colspecs = [
        (0, 10), (10, 60), (60, 120), (120, 140), (140, 145), (145, 155), (155, 160)
    ]
    col_names = ["customer_id", "full_name", "email", "phone", "region_code", "registration_date", "status"]
    df = pd.read_fwf(filepath, colspecs=colspecs, names=col_names, dtype=str, encoding="iso-8859-1")
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()
    name_split = df["full_name"].str.split(n=1, expand=True)
    df["first_name"] = name_split[0] if 0 in name_split.columns else None
    df["last_name"] = name_split[1] if 1 in name_split.columns else None
    df["registration_date"] = pd.to_datetime(df["registration_date"], errors="coerce")
    df["region"] = df["region_code"]
    df["source"] = "erp"
    logger.info(f"  Ingested {len(df)} records from ERP")
    return df

def align_schema(df: pd.DataFrame, source_name: str) -> pd.DataFrame:
    """
    Align a source DataFrame to the standard schema.
    Missing columns are added as NaN. Extra columns are dropped.
    """
    for col in STANDARD_SCHEMA:
        if col not in df.columns:
            df[col] = np.nan
    return df[STANDARD_SCHEMA].copy()

def ingest_all_sources() -> pd.DataFrame:
    frames = []

    website_df = ingest_website_csv(CONFIG["input_dir"] / "website_customers.csv")
    frames.append(align_schema(website_df, "website"))

    crm_df = ingest_crm_json(CONFIG["input_dir"] / "crm_export.json")
    frames.append(align_schema(crm_df, "crm"))

    erp_df = ingest_erp_fixed_width(CONFIG["input_dir"] / "erp_customers.txt")
    frames.append(align_schema(erp_df, "erp"))

    combined = pd.concat(frames, ignore_index=True)
    logger.info(f"Total records combined: {len(combined)}")
    for source in combined["source"].unique():
        count = (combined["source"] == source).sum()
        logger.info(f"  {source}: {count} records")
    
    return combined