# -*- coding: utf-8 -*-
"""
Data Integration: load 7 CSV tables and merge with left joins on id / member_id.
Main table: loan_details. Supports both spec layout (data/raw_data) and step1 output (archive/raw_data).
"""

import os
import pandas as pd

# Paths: prefer data/raw_data (spec); fallback to archive/raw_data (step1 output)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
RAW_DATA_SPEC = os.path.join(PROJECT_ROOT, "data", "raw_data")
RAW_DATA_ARCHIVE = os.path.join(PROJECT_ROOT, "archive", "raw_data")
LOAN_CSV = os.path.join(PROJECT_ROOT, "archive", "loan.csv")

# Cap rows for large files (match step1_split)
MAX_ROWS = 50000


def _raw_data_dir():
    """Use data/raw_data if it has CSVs; else archive/raw_data."""
    for d in [RAW_DATA_SPEC, RAW_DATA_ARCHIVE]:
        if os.path.isdir(d):
            n = sum(1 for f in os.listdir(d) if f.endswith(".csv"))
            if n >= 7:
                return d
    return RAW_DATA_ARCHIVE if os.path.isdir(RAW_DATA_ARCHIVE) else RAW_DATA_SPEC


def load_csv(path: str, nrows: int = None, usecols: list = None) -> pd.DataFrame:
    """Load a single CSV into a DataFrame."""
    if not os.path.isfile(path):
        return pd.DataFrame()
    return pd.read_csv(path, nrows=nrows, usecols=usecols, low_memory=False)


def ensure_output_dirs(out_dirs: list) -> None:
    """Create output directories if they do not exist."""
    for d in out_dirs:
        os.makedirs(d, exist_ok=True)


def _load_spec_tables(base: str):
    """Load 7 tables as per spec (member_info, loan_details, loan_purpose, credit_history, account_info, settlement_status, hardship_flag)."""
    return {
        "member_info": load_csv(os.path.join(base, "member_info.csv"), nrows=MAX_ROWS),
        "loan_details": load_csv(os.path.join(base, "loan_details.csv"), nrows=MAX_ROWS),
        "loan_purpose": load_csv(os.path.join(base, "loan_purpose.csv"), nrows=MAX_ROWS),
        "credit_history": load_csv(os.path.join(base, "credit_history.csv"), nrows=MAX_ROWS),
        "account_info": load_csv(os.path.join(base, "account_info.csv"), nrows=MAX_ROWS),
        "settlement_status": load_csv(os.path.join(base, "settlement_status.csv"), nrows=MAX_ROWS),
        "hardship_flag": load_csv(os.path.join(base, "hardship_flag.csv"), nrows=MAX_ROWS),
    }


def _load_archive_tables(base: str):
    """Build 7 logical tables from archive/raw_data (step1 output) + loan.csv for missing columns."""
    # Available: member_info, loan_details, loan_purpose, credit_metrics, credit_balance, payment_status, application_type
    member_info = load_csv(os.path.join(base, "member_info.csv"), nrows=MAX_ROWS)
    loan_details = load_csv(os.path.join(base, "loan_details.csv"), nrows=MAX_ROWS)
    loan_purpose = load_csv(os.path.join(base, "loan_purpose.csv"), nrows=MAX_ROWS)
    credit_metrics = load_csv(os.path.join(base, "credit_metrics.csv"), nrows=MAX_ROWS)
    credit_balance = load_csv(os.path.join(base, "credit_balance.csv"), nrows=MAX_ROWS)
    payment_status = load_csv(os.path.join(base, "payment_status.csv"), nrows=MAX_ROWS)
    application_type = load_csv(os.path.join(base, "application_type.csv"), nrows=MAX_ROWS)

    # credit_history: member_id, dti, delinq_2yrs, earliest_cr_line, inq_last_6mths
    credit_history = credit_metrics.drop_duplicates(subset=["member_id"], keep="first").copy()
    if os.path.isfile(LOAN_CSV):
        try:
            loan_cols = load_csv(LOAN_CSV, nrows=MAX_ROWS, usecols=["member_id", "earliest_cr_line"])
            loan_cols = loan_cols.drop_duplicates(subset=["member_id"], keep="first")
            credit_history = credit_history.merge(loan_cols, on="member_id", how="left")
        except Exception:
            credit_history["earliest_cr_line"] = None
    else:
        credit_history["earliest_cr_line"] = None

    # account_info: member_id, open_acc, pub_rec, revol_bal, revol_util, total_acc
    account_info = credit_balance.drop_duplicates(subset=["member_id"], keep="first")
    open_acc = credit_metrics[["member_id", "open_acc"]].drop_duplicates(subset=["member_id"], keep="first")
    account_info = account_info.merge(open_acc, on="member_id", how="left")

    # settlement_status: id, loan_status, last_pymnt_d, last_pymnt_amnt (we have id, loan_status, last_pymnt_d; last_pymnt_amnt optional)
    settlement_status = payment_status.rename(columns={})
    if "last_pymnt_amnt" not in settlement_status.columns and os.path.isfile(LOAN_CSV):
        try:
            amnt = load_csv(LOAN_CSV, nrows=MAX_ROWS, usecols=["id", "last_pymnt_amnt"])
            settlement_status = settlement_status.merge(amnt, on="id", how="left")
        except Exception:
            settlement_status["last_pymnt_amnt"] = None
    elif "last_pymnt_amnt" not in settlement_status.columns:
        settlement_status["last_pymnt_amnt"] = None

    # hardship_flag: id, application_type, initial_list_status
    hardship_flag = application_type

    return {
        "member_info": member_info,
        "loan_details": loan_details,
        "loan_purpose": loan_purpose,
        "credit_history": credit_history,
        "account_info": account_info,
        "settlement_status": settlement_status,
        "hardship_flag": hardship_flag,
    }


def merge_all(df_list: dict, key_map: dict = None) -> pd.DataFrame:
    """
    Merge all tables with left joins. Main table = loan_details (id, member_id).
    key_map: optional { 'table_name': ('key',) } e.g. { 'loan_purpose': ('id',), 'member_info': ('member_id',) }.
    """
    key_map = key_map or {}
    main = df_list["loan_details"]
    if main.empty:
        return pd.DataFrame()

    # Left join on id
    for name in ["loan_purpose", "settlement_status", "hardship_flag"]:
        t = df_list.get(name)
        if t is not None and not t.empty and "id" in t.columns:
            keys = key_map.get(name, ("id",))
            main = main.merge(t.drop_duplicates(subset=["id"], keep="first"), on="id", how="left", suffixes=("", "_r"))

    # Left join on member_id (deduplicate right to avoid row explosion)
    for name in ["member_info", "credit_history", "account_info"]:
        t = df_list.get(name)
        if t is not None and not t.empty and "member_id" in t.columns:
            t = t.drop_duplicates(subset=["member_id"], keep="first")
            main = main.merge(t, on="member_id", how="left", suffixes=("", "_r"))

    # Drop duplicate columns (e.g. id_r, member_id_r) if any
    main = main[[c for c in main.columns if not c.endswith("_r")]]
    return main


def run_loader() -> pd.DataFrame:
    """Load 7 tables and return df_final. Used by pipeline and notebook."""
    ensure_output_dirs([os.path.join(PROJECT_ROOT, "outputs"), os.path.join(PROJECT_ROOT, "plots")])
    base = _raw_data_dir()
    spec_files = [
        os.path.join(base, f) for f in
        ["credit_history.csv", "account_info.csv", "settlement_status.csv", "hardship_flag.csv"]
    ]
    if all(os.path.isfile(p) for p in spec_files):
        tables = _load_spec_tables(base)
    else:
        tables = _load_archive_tables(base)

    for k, v in tables.items():
        if v.empty:
            print(f"[WARN] Empty table: {k}")
    df_merged = merge_all(tables)
    print(f"Merged shape: {df_merged.shape}")
    return df_merged


if __name__ == "__main__":
    df = run_loader()
    out_path = os.path.join(PROJECT_ROOT, "outputs", "df_raw.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
