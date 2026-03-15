# Multi-Source Financial Risk Analysis (Lending Club)

End-to-end pipeline: merge 7 fragmented CSV tables → clean → feature engineering → analysis & visualization.

## Data dictionary (7 tables)

| Table | Key | Columns |
|-------|-----|--------|
| **member_info** | member_id | emp_title, emp_length, home_ownership, annual_inc |
| **loan_details** | id, member_id | loan_amnt, term, int_rate, installment, grade [, sub_grade] |
| **loan_purpose** | id | purpose, title, zip_code, addr_state |
| **credit_history** | member_id | dti, delinq_2yrs, earliest_cr_line, inq_last_6mths |
| **account_info** | member_id | open_acc, pub_rec, revol_bal, revol_util, total_acc |
| **settlement_status** | id | loan_status, last_pymnt_d [, last_pymnt_amnt] |
| **hardship_flag** | id | application_type, initial_list_status |

- **Merge**: Main table = `loan_details`. Left join on `id` for loan_purpose, settlement_status, hardship_flag; left join on `member_id` for member_info, credit_history, account_info.
- **is_default**: 1 if `loan_status` in {'Charged Off', 'Late'}, else 0.
- **risk_level**: Low/Medium/High from int_rate and dti.

## Assumptions

- Raw data lives in `data/raw_data/` (spec) or `archive/raw_data/` (step1_split output). The loader auto-detects and, for archive layout, builds credit_history (earliest_cr_line from `archive/loan.csv`), account_info (from credit_balance + open_acc), settlement_status (payment_status), hardship_flag (application_type).
- First 50,000 rows are used when reading CSVs to control memory.
- Missing numeric values: filled with column median; categorical: filled with mode.
- Percentages (e.g. `int_rate` "10.5%") are converted to float (0.105). `emp_length` is parsed to numeric years.

## Environment

- Python 3.8+
- pandas, numpy, seaborn, matplotlib

```bash
pip install pandas numpy seaborn matplotlib
```

## Running steps

### Phase A: Generate df_final and plots

1. **Step 1 (split) – already done**  
   - `archive/step1_split.py` splits `archive/loan.csv` into 7 tables under `archive/raw_data/`.

2. **Step 2 (merge)**  
   ```bash
   python data_loader.py
   ```
   - Loads 7 tables from `data/raw_data` or `archive/raw_data`, merges with left joins, saves `outputs/df_raw.csv`.

3. **Step 3 (clean & features)**  
   ```bash
   python feature_engineering.py
   ```
   - Cleans types and missing values, adds is_default, monthly_disposable_income, credit_line_age, risk_level. Saves `outputs/df_final.csv`.

4. **Step 4 (analysis & plots)**  
   ```bash
   python analysis.py
   ```
   - Computes default rate by grade, saves 3 plots to `plots/` and report to `outputs/`.

### Phase B: Check results

- `outputs/df_final.csv` – merged and engineered dataset.
- `plots/default_by_grade.png` – default rate by loan grade.
- `plots/loan_amount_by_default.png` – loan amount distribution (defaulted vs non-defaulted).
- `plots/correlation_heatmap.png` – correlation of numeric features.
- `outputs/default_rate_by_grade.csv` – summary table.
- `notebooks/analysis.ipynb` – notebook to reproduce loading, features, and visualizations.

## Code structure

- **data_loader.py**: `load_csv`, `merge_all`, `ensure_output_dirs`, `run_loader`
- **feature_engineering.py**: `clean_and_cast`, `add_features`, `get_risk_level`, `derive_time_features`, `run_pipeline`
- **analysis.py**: `compute_default_by_grade`, `plot_default_by_grade`, `plot_loan_amount_distribution`, `plot_correlation_heatmap`, `save_report`, `run_analysis`
- **notebooks/analysis.ipynb**: Data loading, df_final inspection, feature steps, plots, conclusions

## Outputs & paths

| Output | Path |
|--------|------|
| Merged (raw) | outputs/df_raw.csv |
| Final dataset | outputs/df_final.csv |
| Default by grade | outputs/default_rate_by_grade.csv |
| Plot: default by grade | plots/default_by_grade.png |
| Plot: loan amount by default | plots/loan_amount_by_default.png |
| Plot: correlation | plots/correlation_heatmap.png |
