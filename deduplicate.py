import pandas as pd
from utils import logger
from config import CONFIG

def deduplicate_customers(df: pd.DataFrame) -> pd.DataFrame:
    initial_count = len(df)
    df["source_priority"] = df["source"].map(CONFIG["source_priority"]).fillna(99)
    df = df.sort_values("source_priority")

    def merge_group(group: pd.DataFrame) -> pd.Series:
        best = group.iloc[0].copy()
        for col in ["phone", "region", "first_name", "last_name", "registration_date"]:
            if col in group.columns and pd.isna(best.get(col)):
                non_null = group[col].dropna()
                if len(non_null) > 0:
                    best[col] = non_null.iloc[0]
        if "opt_out" in group.columns:
            best["opt_out"] = group["opt_out"].fillna(0).astype(bool).any()
        best["sources"] = ",".join(group["source"].unique())
        best["source_count"] = len(group["source"].unique())
        return best

    valid_mask = df["email_valid"] == True
    valid_df = df[valid_mask]
    invalid_df = df[~valid_mask]
    deduped = (
        valid_df
        .groupby("email", sort=False)
        .apply(merge_group)
        .reset_index(drop=True)
    )

    result = pd.concat([deduped, invalid_df], ignore_index=True)
    removed = initial_count - len(result)
    logger.info(f"  Records before deduplication: {initial_count}")
    logger.info(f"  Duplicate records removed: {removed}")
    logger.info(f"  Records after deduplication: {len(result)}")
    return result