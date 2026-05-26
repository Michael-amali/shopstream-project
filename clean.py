import pandas as pd
import numpy as np
import re
from utils import logger
from config import CONFIG

REGION_MAP = {
    "us": "US", "usa": "US", "united states": "US", "north america": "US",
    "na": "US", "amer": "US", "america": "US",
    "eu": "EU", "europe": "EU", "emea": "EU", "eur": "EU", "european union": "EU",
    "apac": "APAC", "asia": "APAC", "asia pacific": "APAC",
    "ap": "APAC", "asia-pacific": "APAC",
}

def standardize_emails(series: pd.Series) -> pd.Series:
    return (
        series
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "", regex=True)
        .replace({"nan": np.nan, "none": np.nan, "": np.nan})
    )

def validate_emails(series: pd.Series) -> pd.Series:
    return series.str.match(CONFIG["email_regex"], na=False)

def standardize_phone_numbers(series: pd.Series) -> pd.Series:
    def clean_phone(phone):
        if pd.isna(phone) or str(phone).strip() in ("", "nan", "None"):
            return np.nan
        phone = str(phone).strip()
        has_plus = phone.startswith("+")
        digits = re.sub(r"[^\d]", "", phone)
        if len(digits) < 7:
            return np.nan
        return f"+{digits}" if has_plus else digits
    return series.apply(clean_phone)

def standardize_names(series: pd.Series) -> pd.Series:
    return (
        series
        .astype(str)
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
        .replace({"Nan": np.nan, "None": np.nan, "": np.nan})
    )

def standardize_regions(series: pd.Series) -> pd.Series:
    return (
        series
        .astype(str)
        .str.strip()
        .str.lower()
        .map(REGION_MAP)
    )

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["email_raw"] = df["email"].copy()
    df["email"] = standardize_emails(df["email"])
    df["email_valid"] = validate_emails(df["email"])
    df["first_name"] = standardize_names(df["first_name"])
    df["last_name"] = standardize_names(df["last_name"])
    df["phone"] = standardize_phone_numbers(df["phone"])
    df["region"] = standardize_regions(df["region"])
    df["registration_date"] = pd.to_datetime(df["registration_date"], errors="coerce")
    if "opt_out" in df.columns:
        df["opt_out"] = df["opt_out"].astype("bool")
    invalid_emails = (~df["email_valid"]).sum()
    null_regions = df["region"].isna().sum()
    logger.info(f"  Invalid emails: {invalid_emails}")
    logger.info(f"  Null regions after standardization: {null_regions}")
    logger.info(f"  Records after cleaning: {len(df)}")
    return df