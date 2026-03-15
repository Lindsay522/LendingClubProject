# 不依赖 pandas，只用 Python 标准库拆分 loan.csv（大文件友好）
import csv
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
input_file = os.path.join(SCRIPT_DIR, 'loan.csv')
output_dir = os.path.join(SCRIPT_DIR, 'raw_data')
MAX_ROWS = 50000  # 只处理前 N 行

if not os.path.exists(input_file):
    print(f"❌ 找不到 loan.csv，当前查找路径: {input_file}")
    exit(1)
os.makedirs(output_dir, exist_ok=True)

tables = {
    'member_info.csv': ['member_id', 'emp_title', 'emp_length', 'home_ownership', 'annual_inc'],
    'loan_details.csv': ['id', 'member_id', 'loan_amnt', 'term', 'int_rate', 'installment', 'grade'],
    'loan_purpose.csv': ['id', 'purpose', 'title', 'zip_code', 'addr_state'],
    'credit_metrics.csv': ['member_id', 'dti', 'delinq_2yrs', 'inq_last_6mths', 'open_acc'],
    'credit_balance.csv': ['member_id', 'pub_rec', 'revol_bal', 'revol_util', 'total_acc'],
    'payment_status.csv': ['id', 'loan_status', 'total_pymnt', 'last_pymnt_d'],
    'application_type.csv': ['id', 'application_type', 'initial_list_status']
}

print(f"正在读取: {input_file}（前 {MAX_ROWS} 行）")

try:
    with open(input_file, 'r', encoding='utf-8', errors='replace', newline='') as f:
        reader = csv.reader(f)
        header = next(reader)
        col_index = {name: i for i, name in enumerate(header)}

    for filename, want_cols in tables.items():
        available = [c for c in want_cols if c in col_index]
        if not available:
            print(f"⚠ 跳过 {filename}（没有匹配列）")
            continue
        indices = [col_index[c] for c in available]
        out_path = os.path.join(output_dir, filename)
        count = 0
        with open(input_file, 'r', encoding='utf-8', errors='replace', newline='') as fin:
            reader = csv.reader(fin)
            header = next(reader)
            with open(out_path, 'w', encoding='utf-8', newline='') as fout:
                writer = csv.writer(fout)
                writer.writerow(available)
                for row in reader:
                    if count >= MAX_ROWS:
                        break
                    writer.writerow([row[i] if i < len(row) else '' for i in indices])
                    count += 1
        print(f"✅ 已生成: {filename}（{count} 行）")

    print("\n恭喜！碎片表已全部生成在 raw_data 文件夹中。")

except Exception as e:
    print(f"❌ 出错了: {e}")
    import traceback
    traceback.print_exc()
