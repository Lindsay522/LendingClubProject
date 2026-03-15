# -*- coding: utf-8 -*-
"""
Data Cleaning & Feature Engineering: clean_and_cast, add_features, risk_level.
"""

import os
import re
import pandas as pd
import numpy as np
from datetime import datetime

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")


def _pct_to_float(ser: pd.Series) -> pd.Series:
    """Convert strings like '10.5%' or '10.5' to float 0.105 or 10.5 (no /100 if no %)."""
    if ser.dtype != object:
        return ser
    s = ser.astype(str).str.replace("%", "", regex=False).str.strip()
    num = pd.to_numeric(s, errors="coerce")
    if ser.astype(str).str.contains("%", na=False).any():
        num = num / 100.0
    return num


def _parse_emp_length(ser: pd.Series) -> pd.Series:
    """Convert emp_length to numeric years: '10+ years' -> 10, '< 1 year' -> 0.5, 'n/a' -> NaN."""
    def one(s):
        if pd.isna(s) or str(s).strip().lower() in ("", "n/a", "na"):
            return np.nan
        s = str(s).strip().lower()
        if "10+" in s or "10 +" in s:
            return 10.0
        m = re.search(r"(\d+)\s*\+?\s*year", s)
        if m:
            return float(m.group(1))
        if "< 1" in s or "<1" in s:
            return 0.5
        return np.nan
    return ser.map(one)


def _parse_date_robust(ser: pd.Series, name: str = "") -> pd.Series:
    """Parse date column with multiple formats (e.g. Jan-1985, 2015-01, 01/15/2015)."""
    out = []
    for v in ser:
        if pd.isna(v) or str(v).strip() == "":
            out.append(pd.NaT)
            continue
        s = str(v).strip()
        for fmt in ["%b-%Y", "%Y-%m", "%m-%Y", "%b-%y", "%m/%d/%Y", "%Y-%m-%d", "%d-%b-%y"]:
            try:
                out.append(datetime.strptime(s, fmt))
                break
            except ValueError:
                continue
        else:
            out.append(pd.NaT)
    return pd.to_datetime(out, errors="coerce")


def clean_and_cast(df: pd.DataFrame) -> pd.DataFrame:
    """Convert mixed-type fields to numeric (int_rate, emp_length, etc.), handle missing values."""
    df = df.copy()
    # Percentage columns
    for col in ["int_rate", "revol_util"]:
        if col in df.columns:
            df[col] = _pct_to_float(df[col])

    # Employment length
    if "emp_length" in df.columns:
        df["emp_length"] = _parse_emp_length(df["emp_length"])

    # Numeric fill with median
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        df[col] = df[col].fillna(df[col].median())

    # Categorical fill with mode
    for col in df.select_dtypes(include=["object", "string"]).columns:
        mode_val = df[col].mode()
        df[col] = df[col].fillna(mode_val.iloc[0] if len(mode_val) else "")

    return df


def get_risk_level(int_rate: float, dti: float) -> str:
    """Categorical risk: Low / Medium / High based on int_rate and dti."""
    if pd.isna(int_rate):
        int_rate = 0
    if pd.isna(dti):
        dti = 0
    ir = float(int_rate)
    d = float(dti)
    score = (ir * 10) + (d / 10)  # rough combined
    if score < 15:
        return "Low"
    if score < 30:
        return "Medium"
    return "High"


def derive_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add time-derived columns if date cols exist (e.g. issue_d, earliest_cr_line)."""
    df = df.copy()
    if "earliest_cr_line" in df.columns:
        df["_earliest_dt"] = _parse_date_robust(df["earliest_cr_line"])
    if "issue_d" in df.columns:
        df["_issue_dt"] = _parse_date_robust(df["issue_d"])
    return df


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add: is_default, monthly_disposable_income, credit_line_age, risk_level.
    """
    df = df.copy()
    # is_default: 1 if loan_status in {'Charged Off','Late'}, else 0
    if "loan_status" in df.columns:
        ls = df["loan_status"].fillna("").astype(str).str.lower()
        df["is_default"] = (ls.str.contains("charged off") | ls.str.contains("late")).astype(int)
    else:
        df["is_default"] = 0

    # monthly_disposable_income = (annual_inc / 12) - installment
    inc = df.get("annual_inc")
    if inc is None:
        inc = pd.Series(np.nan, index=df.index)
    inst = df.get("installment", pd.Series(0, index=df.index))
    df["monthly_disposable_income"] = (inc.astype(float) / 12.0) - inst.astype(float)

    # credit_line_age: years between loan issuance and earliest_cr_line (or today if no issue_d)
    df = derive_time_features(df)
    if "_earliest_dt" in df.columns:
        ref = df["_issue_dt"] if "_issue_dt" in df.columns else pd.Timestamp.now()
        if "_issue_dt" in df.columns:
            ref = df["_issue_dt"]
            df["credit_line_age"] = (ref - df["_earliest_dt"]).dt.days / 365.25
        else:
            df["credit_line_age"] = (pd.Timestamp.now() - df["_earliest_dt"]).dt.days / 365.25
        df.drop(columns=["_earliest_dt"], inplace=True, errors="ignore")
    else:
        df["credit_line_age"] = np.nan
    if "_issue_dt" in df.columns:
        df.drop(columns=["_issue_dt"], inplace=True, errors="ignore")

    # risk_level: Low/Medium/High from int_rate and dti
    ir = df.get("int_rate", pd.Series(0, index=df.index))
    dti = df.get("dti", pd.Series(0, index=df.index))
    df["risk_level"] = [get_risk_level(a, b) for a, b in zip(ir, dti)]

    return df


def run_pipeline() -> pd.DataFrame:
    """Load raw merge output, clean, add features, save df_final."""
    from data_loader import run_loader

    os.makedirs(OUTPUTS_DIR, exist_ok=True)
    raw_path = os.path.join(OUTPUTS_DIR, "df_raw.csv")
    if os.path.isfile(raw_path):
        df = pd.read_csv(raw_path, low_memory=False)
    else:
        df = run_loader()
        df.to_csv(raw_path, index=False)

    df = clean_and_cast(df)
    df = add_features(df)
    out_path = os.path.join(OUTPUTS_DIR, "df_final.csv")
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    return df


if __name__ == "__main__":
    run_pipeline()
