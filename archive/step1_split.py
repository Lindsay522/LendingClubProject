import pandas as pd
import os

# 脚本所在目录（这样无论从哪运行都能找到 loan.csv）
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 原始大文件路径
input_file = os.path.join(SCRIPT_DIR, 'loan.csv')
# 存放拆分后小文件的文件夹
output_dir = os.path.join(SCRIPT_DIR, 'raw_data')

if not os.path.exists(input_file):
    print(f"[ERR] 找不到 loan.csv，当前查找路径: {input_file}")
    exit(1)

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print(f"正在读取: {input_file}")
print("仅限前50000行，请稍候...")

try:
    # 只读取前50000行，防止内存崩溃
    df = pd.read_csv(input_file, nrows=50000, low_memory=False)

    # 定义学姐要求的“多表”结构
    tables = {
        'member_info.csv': ['member_id', 'emp_title', 'emp_length', 'home_ownership', 'annual_inc'],
        'loan_details.csv': ['id', 'member_id', 'loan_amnt', 'term', 'int_rate', 'installment', 'grade'],
        'loan_purpose.csv': ['id', 'purpose', 'title', 'zip_code', 'addr_state'],
        'credit_metrics.csv': ['member_id', 'dti', 'delinq_2yrs', 'inq_last_6mths', 'open_acc'],
        'credit_balance.csv': ['member_id', 'pub_rec', 'revol_bal', 'revol_util', 'total_acc'],
        'payment_status.csv': ['id', 'loan_status', 'total_pymnt', 'last_pymnt_d'],
        'application_type.csv': ['id', 'application_type', 'initial_list_status']
    }

    # 开始拆分并保存
    for filename, cols in tables.items():
        # 只保留表中存在的列
        available_cols = [c for c in cols if c in df.columns]
        df[available_cols].to_csv(os.path.join(output_dir, filename), index=False)
        print(f"[OK] 已生成: {filename}")

    print("\n恭喜！7个碎片表已全部生成在 raw_data 文件夹中。")

except Exception as e:
    print(f"[ERR] 出错了: {e}")
    print(f"请确保 loan.csv 在脚本同目录: {SCRIPT_DIR}")
