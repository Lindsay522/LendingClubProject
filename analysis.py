# -*- coding: utf-8 -*-
"""
Analysis & Visualization: default rate by grade, correlation heatmap, loan_amnt distribution.
"""

import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")
PLOTS_DIR = os.path.join(PROJECT_ROOT, "plots")


def compute_default_by_grade(df: pd.DataFrame) -> pd.DataFrame:
    """Default rate per grade."""
    if "grade" not in df.columns or "is_default" not in df.columns:
        return pd.DataFrame()
    return df.groupby("grade", as_index=False).agg(
        default_rate=("is_default", "mean"),
        count=("is_default", "size")
    ).sort_values("grade")


def plot_default_by_grade(df: pd.DataFrame, save_path: str = None) -> None:
    """Bar chart: default rate by grade. Saves to plots/default_by_grade.png."""
    rate = compute_default_by_grade(df)
    if rate.empty:
        return
    save_path = save_path or os.path.join(PLOTS_DIR, "default_by_grade.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(data=rate, x="grade", y="default_rate", color="steelblue", edgecolor="black")
    ax.set_xlabel("Loan Grade")
    ax.set_ylabel("Default Rate")
    ax.set_title("Default Rate by Loan Grade")
    plt.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_loan_amount_distribution(df: pd.DataFrame, save_path: str = None) -> None:
    """Distribution of loan_amnt for defaulted vs non-defaulted. Saves to plots/loan_amount_by_default.png."""
    if "loan_amnt" not in df.columns or "is_default" not in df.columns:
        return
    save_path = save_path or os.path.join(PLOTS_DIR, "loan_amount_by_default.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    df_plot = df[["loan_amnt", "is_default"]].dropna()
    df_plot["Defaulted"] = df_plot["is_default"].map({0: "No", 1: "Yes"})
    fig, ax = plt.subplots(figsize=(7, 5))
    sns.histplot(data=df_plot, x="loan_amnt", hue="Defaulted", bins=30, kde=True, alpha=0.5, ax=ax)
    ax.set_xlabel("Loan Amount")
    ax.set_ylabel("Count")
    ax.set_title("Loan Amount Distribution: Defaulted vs Non-Defaulted")
    plt.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_correlation_heatmap(df: pd.DataFrame, save_path: str = None) -> None:
    """Correlation heatmap among numeric features. Saves to plots/correlation_heatmap.png."""
    save_path = save_path or os.path.join(PLOTS_DIR, "correlation_heatmap.png")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    num = df.select_dtypes(include="number")
    if num.shape[1] < 2:
        return
    # Limit columns if too many
    if num.shape[1] > 20:
        num = num.iloc[:, :20]
    corr = num.corr()
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(corr, annot=False, fmt=".2f", cmap="RdBu_r", center=0, ax=ax, square=True)
    ax.set_title("Correlation Heatmap (Numeric Features)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    fig.savefig(save_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def save_report(df: pd.DataFrame, report_path: str = None) -> None:
    """Save a brief summary (default by grade table) to report_path."""
    report_path = report_path or os.path.join(OUTPUTS_DIR, "default_rate_by_grade.csv")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    rate = compute_default_by_grade(df)
    if not rate.empty:
        rate.to_csv(report_path, index=False)
        print(f"Saved: {report_path}")


def run_analysis() -> None:
    """Load df_final, generate 3 plots and report."""
    from feature_engineering import run_pipeline

    df_path = os.path.join(OUTPUTS_DIR, "df_final.csv")
    if os.path.isfile(df_path):
        df = pd.read_csv(df_path, low_memory=False)
    else:
        df = run_pipeline()

    os.makedirs(PLOTS_DIR, exist_ok=True)
    plot_default_by_grade(df)
    plot_loan_amount_distribution(df)
    plot_correlation_heatmap(df)
    save_report(df)


if __name__ == "__main__":
    run_analysis()
