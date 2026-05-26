"""Pipeline entry point: ingest → clean → validate → export."""

from utils import logger
from config import CONFIG
from ingest import ingest_all_sources
from clean import clean_dataframe
from deduplicate import deduplicate_customers
from validate import run_quality_checks
from visualize import generate_eda_report
from datetime import datetime


def run_pipeline():
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("SHOPSTREAM CUSTOMER DATA QUALITY PIPELINE")
    logger.info(f"Run started: {start_time.isoformat()}")
    logger.info("=" * 60)
    logger.info("=" * 60)
    
    logger.info("STEP 1: Data Ingestion")
    combined = ingest_all_sources()
    input_count = len(combined)

    logger.info("STEP 2: Cleaning & Standardization")
    cleaned = clean_dataframe(combined)

    logger.info("STEP 3: Deduplication")
    deduped = deduplicate_customers(cleaned)

    logger.info("STEP 4: Quality Validation")
    quality_report = run_quality_checks(deduped)

    logger.info("STEP 5: Generating EDA visualization...")
    generate_eda_report(deduped, CONFIG["output_dir"])

    logger.info("STEP 6: Exporting Results")
    parquet_path = CONFIG["output_dir"] / "golden_customers.parquet"
    deduped.to_parquet(parquet_path, index=False, engine="pyarrow", compression="gzip")
    logger.info(f"  Parquet export: {parquet_path} ({parquet_path.stat().st_size / 1024:.1f} KB)")

    csv_path = CONFIG["output_dir"] / "golden_customers.csv"
    deduped.to_csv(csv_path, index=False, encoding="utf-8-sig")
    logger.info(f"  CSV export: {csv_path}")

    report_path = CONFIG["output_dir"] / "quality_report.csv"
    quality_report.to_csv(report_path, index=False)
    logger.info(f"  Quality report: {report_path}")

    duration = (datetime.now() - start_time).total_seconds()
    logger.info("=" * 60)
    logger.info("PIPELINE COMPLETE")
    logger.info(f"  Input records:          {input_count:,}")
    logger.info(f"  Output (golden) records:{len(deduped):,}")
    logger.info(f"  Duplicates removed:     {input_count - len(deduped):,}")
    logger.info(f"  Quality checks passed:  {(quality_report['status'] == 'PASS').sum()}/{len(quality_report)}")
    logger.info(f"  Duration:               {duration:.1f}s")
    logger.info("=" * 60)


if __name__ == "__main__":
    run_pipeline()
