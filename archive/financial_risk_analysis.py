# -*- coding: utf-8 -*-
"""
Multi-Source Financial Risk Analysis & Feature Engineering
Processes fragmented Lending Club CSVs, merges, engineers features, cleans, and visualizes.
"""

import os
import sys
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIG: Paths (script directory = archive; raw_data and loan.csv live here)
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
RAW_DIR = os.path.join(SCRIPT_DIR, 'raw_data')
LOAN_CSV = os.path.join(SCRIPT_DIR, 'loan.csv')
MAX_ROWS = 50000  # Match step1_split: only first 50k rows

# ---------------------------------------------------------------------------
# TASK 1: Data Simulation & Merging (6 tables -> one master on ID)
# ---------------------------------------------------------------------------

def load_member_profile():
    """member_profile: ID, employment, home ownership, income."""
    loan_details = pd.read_csv(os.path.join(RAW_DIR, 'loan_details.csv'), nrows=MAX_ROWS)
    member_info = pd.read_csv(os.path.join(RAW_DIR, 'member_info.csv'), nrows=MAX_ROWS)
    # One row per member_id to avoid merge explosion
    member_info = member_info.drop_duplicates(subset=['member_id'], keep='first')
    profile = loan_details[['id', 'member_id']].merge(member_info, on='member_id', how='left')
    profile = profile.rename(columns={'id': 'ID'})[['ID', 'emp_title', 'emp_length', 'home_ownership', 'annual_inc']]
    profile.columns = ['ID', 'employment', 'emp_length', 'home_ownership', 'income']
    return profile

def load_loan_terms():
    """loan_terms: ID, amount, interest rate, term, grade."""
    df = pd.read_csv(os.path.join(RAW_DIR, 'loan_details.csv'), nrows=MAX_ROWS)
    df = df.rename(columns={'id': 'ID', 'loan_amnt': 'amount', 'int_rate': 'interest_rate'})
    return df[['ID', 'amount', 'interest_rate', 'term', 'grade']]

def load_credit_history():
    """credit_history: ID, earliest_cr_line, total_acc, pub_rec. earliest_cr_line from loan.csv."""
    loan_cols = pd.read_csv(LOAN_CSV, nrows=MAX_ROWS, usecols=['id', 'member_id', 'earliest_cr_line'], low_memory=False)
    credit_balance = pd.read_csv(os.path.join(RAW_DIR, 'credit_balance.csv'), nrows=MAX_ROWS)
    # One row per member to avoid merge explosion, then one row per loan
    credit_balance = credit_balance.drop_duplicates(subset=['member_id'], keep='first')
    merged = loan_cols.merge(credit_balance, on='member_id', how='left')
    merged = merged.rename(columns={'id': 'ID'})
    return merged[['ID', 'earliest_cr_line', 'total_acc', 'pub_rec']]

def load_current_delinq():
    """current_delinq: ID, delinq_2yrs, inq_last_6mths."""
    loan_details = pd.read_csv(os.path.join(RAW_DIR, 'loan_details.csv'), nrows=MAX_ROWS)
    credit_metrics = pd.read_csv(os.path.join(RAW_DIR, 'credit_metrics.csv'), nrows=MAX_ROWS)
    credit_metrics = credit_metrics.drop_duplicates(subset=['member_id'], keep='first')
    merged = loan_details[['id', 'member_id']].merge(
        credit_metrics[['member_id', 'delinq_2yrs', 'inq_last_6mths']], on='member_id', how='left'
    )
    return merged.rename(columns={'id': 'ID'})[['ID', 'delinq_2yrs', 'inq_last_6mths']]

def load_payment_status():
    """payment_status: ID, total_pymnt, last_pymnt_d, loan_status."""
    df = pd.read_csv(os.path.join(RAW_DIR, 'payment_status.csv'), nrows=MAX_ROWS)
    return df.rename(columns={'id': 'ID'})

def load_geo_info():
    """geo_info: ID, zip_code, addr_state."""
    df = pd.read_csv(os.path.join(RAW_DIR, 'loan_purpose.csv'), nrows=MAX_ROWS)
    return df.rename(columns={'id': 'ID'})[['ID', 'zip_code', 'addr_state']]

def build_master_df():
    """Merge all 6 tables on ID into df_final."""
    print("Task 1: Loading and merging 6 tables...", flush=True)
    member_profile = load_member_profile()
    loan_terms = load_loan_terms()
    credit_history = load_credit_history()
    current_delinq = load_current_delinq()
    payment_status = load_payment_status()
    geo_info = load_geo_info()

    df_final = loan_terms.merge(payment_status, on='ID', how='left')
    df_final = df_final.merge(geo_info, on='ID', how='left')
    df_final = df_final.merge(member_profile, on='ID', how='left')
    df_final = df_final.merge(credit_history, on='ID', how='left')
    df_final = df_final.merge(current_delinq, on='ID', how='left')

    # Add installment and dti for feature engineering
    loan_det = pd.read_csv(os.path.join(RAW_DIR, 'loan_details.csv'), nrows=MAX_ROWS)[['id', 'member_id', 'installment']]
    cred_met = pd.read_csv(os.path.join(RAW_DIR, 'credit_metrics.csv'), nrows=MAX_ROWS)[['member_id', 'dti']].drop_duplicates(subset=['member_id'], keep='first')
    loan_det = loan_det.merge(cred_met, on='member_id', how='left')
    df_final = df_final.merge(loan_det[['id', 'installment', 'dti']].rename(columns={'id': 'ID'}), on='ID', how='left')

    print(f"  df_final shape: {df_final.shape}", flush=True)
    return df_final

# ---------------------------------------------------------------------------
# TASK 2: Advanced Feature Engineering
# ---------------------------------------------------------------------------

def add_calculated_columns(df):
    """Add is_default, credit_age_years, installment_to_income_ratio, risk_score."""
    # 1. is_default: 1 if Charged Off or Late, else 0
    if 'loan_status' in df.columns:
        df['is_default'] = df['loan_status'].fillna('').astype(str).str.lower().apply(
            lambda x: 1 if ('charged off' in x or 'late' in x) else 0
        )
    else:
        df['is_default'] = 0

    # 2. credit_age_years: years from earliest_cr_line to today
    if 'earliest_cr_line' in df.columns:
        def parse_earliest_cr(s):
            try:
                if pd.isna(s) or str(s).strip() == '':
                    return np.nan
                # e.g. "Jan-1985" or "1985-01"
                s = str(s).strip()
                for fmt in ['%b-%Y', '%Y-%m', '%m-%Y', '%b-%y']:
                    try:
                        return datetime.strptime(s, fmt)
                    except ValueError:
                        continue
                return np.nan
            except Exception:
                return np.nan

        df['_earliest_dt'] = df['earliest_cr_line'].apply(parse_earliest_cr)
        today = pd.Timestamp.now()
        df['credit_age_years'] = df['_earliest_dt'].apply(
            lambda x: (today - x).days / 365.25 if pd.notna(x) else np.nan
        )
        df.drop(columns=['_earliest_dt'], inplace=True)
    else:
        df['credit_age_years'] = np.nan

    # 3. installment_to_income_ratio = monthly_installment / (annual_inc/12)
    inc = df.get('income', df.get('annual_inc', pd.Series(np.nan, index=df.index)))
    if inc is None:
        inc = pd.Series(np.nan, index=df.index)
    monthly_inc = inc.replace(0, np.nan) / 12.0
    df['installment_to_income_ratio'] = np.where(
        monthly_inc.notna() & (monthly_inc > 0),
        df['installment'].astype(float) / monthly_inc,
        np.nan
    )

    # 4. risk_score: weighted combination of grade, inq_last_6mths, dti (higher = riskier)
    grade_map = {'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'F': 6, 'G': 7}
    df['_grade_num'] = df['grade'].fillna('').astype(str).str.upper().str.strip().map(grade_map).fillna(0)
    inq = df['inq_last_6mths'].fillna(0).astype(float)
    dti = df['dti'].fillna(0).astype(float)
    df['risk_score'] = 0.4 * df['_grade_num'] + 0.3 * np.minimum(inq, 20) / 20.0 * 10 + 0.3 * np.minimum(dti, 100) / 100.0 * 10
    df.drop(columns=['_grade_num'], inplace=True)
    return df

# ---------------------------------------------------------------------------
# TASK 3: Data Cleaning & Analysis
# ---------------------------------------------------------------------------

def _pct_to_float(ser):
    """Convert strings like '10.5%' to 0.105."""
    if ser.dtype != 'object':
        return ser
    s = ser.astype(str).str.replace('%', '', regex=False).str.strip()
    return pd.to_numeric(s, errors='coerce') / 100.0

def clean_data(df):
    """Fill numeric with median, categorical with mode; convert percentage strings to float."""
    # Convert known percentage columns
    for col in ['interest_rate', 'int_rate', 'revol_util']:
        if col in df.columns and df[col].dtype == 'object':
            df[col] = _pct_to_float(df[col])

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(df[col].median())
        elif df[col].dtype == 'object':
            # Try convert percentage-like strings
            s = df[col].astype(str).str.replace('%', '', regex=False).str.strip()
            num = pd.to_numeric(s, errors='coerce')
            if num.notna().sum() > len(df) * 0.1:
                df[col] = num / 100.0
                df[col] = df[col].fillna(df[col].median())

    for col in df.select_dtypes(include=['object']).columns:
        if col in df.columns:
            mode_val = df[col].mode()
            df[col] = df[col].fillna(mode_val.iloc[0] if len(mode_val) else '')
    return df

def run_analysis(df):
    """Group by grade and addr_state -> average default rate."""
    if 'is_default' not in df.columns or 'grade' not in df.columns or 'addr_state' not in df.columns:
        return None
    agg = df.groupby(['grade', 'addr_state'], dropna=False).agg(
        default_rate=('is_default', 'mean'),
        count=('is_default', 'size')
    ).reset_index()
    return agg

# ---------------------------------------------------------------------------
# TASK 4: Visualization (Seaborn)
# ---------------------------------------------------------------------------

def plot_default_rate_by_grade(df, out_dir):
    """Bar chart: Default Rate by Loan Grade."""
    if 'grade' not in df.columns or 'is_default' not in df.columns:
        return
    rate = df.groupby('grade', dropna=False)['is_default'].mean().reset_index(name='default_rate')
    rate = rate.sort_values('grade')
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=rate, x='grade', y='default_rate', color='steelblue', edgecolor='black')
    ax.set_xlabel('Loan Grade')
    ax.set_ylabel('Default Rate')
    ax.set_title('Default Rate by Loan Grade')
    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, '01_default_rate_by_grade.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved: 01_default_rate_by_grade.png")

def plot_correlation_heatmap(df, out_dir):
    """Heatmap: Correlation between income, loan amount, and default status."""
    cols = ['income', 'amount', 'is_default']
    rename = {'income': 'income', 'amount': 'loan_amnt', 'is_default': 'is_default'}
    use = [c for c in cols if c in df.columns]
    if len(use) < 2:
        return
    sub = df[use].copy()
    sub.columns = [rename.get(c, c) for c in use]
    corr = sub.astype(float).corr()
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0, ax=ax, square=True)
    ax.set_title('Correlation: Income, Loan Amount, Default Status')
    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, '02_correlation_heatmap.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved: 02_correlation_heatmap.png")

def plot_dti_boxplot(df, out_dir):
    """Boxplot: DTI distribution for Defaulted vs Non-Defaulted."""
    if 'dti' not in df.columns or 'is_default' not in df.columns:
        return
    df_plot = df[['dti', 'is_default']].dropna()
    df_plot['Defaulted'] = df_plot['is_default'].map({0: 'No', 1: 'Yes'})
    fig, ax = plt.subplots(figsize=(6, 5))
    sns.boxplot(data=df_plot, x='Defaulted', y='dti', palette={'No': 'lightgreen', 'Yes': 'coral'})
    ax.set_xlabel('Defaulted')
    ax.set_ylabel('DTI')
    ax.set_title('DTI Distribution: Defaulted vs Non-Defaulted')
    plt.tight_layout()
    fig.savefig(os.path.join(out_dir, '03_dti_boxplot.png'), dpi=150, bbox_inches='tight')
    plt.close()
    print("  Saved: 03_dti_boxplot.png")

# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    if not os.path.isdir(RAW_DIR):
        print(f"[ERR] raw_data not found: {RAW_DIR}")
        return
    out_dir = os.path.join(SCRIPT_DIR, 'output')
    os.makedirs(out_dir, exist_ok=True)

    # Task 1
    df_final = build_master_df()

    # Task 2
    print("Task 2: Feature engineering...")
    df_final = add_calculated_columns(df_final)

    # Task 3
    print("Task 3: Data cleaning and analysis...")
    df_final = clean_data(df_final)
    agg = run_analysis(df_final)
    if agg is not None:
        agg_path = os.path.join(out_dir, 'default_rate_by_grade_state.csv')
        agg.to_csv(agg_path, index=False)
        print(f"  Saved: {agg_path}")

    # Task 4
    print("Task 4: Visualizations...")
    plot_default_rate_by_grade(df_final, out_dir)
    plot_correlation_heatmap(df_final, out_dir)
    plot_dti_boxplot(df_final, out_dir)

    # Save final merged dataset (optional)
    out_csv = os.path.join(out_dir, 'df_final.csv')
    df_final.to_csv(out_csv, index=False)
    print(f"\nDone. df_final shape: {df_final.shape}")
    print(f"Outputs: {out_dir}")

if __name__ == '__main__':
    main()
