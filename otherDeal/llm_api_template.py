import pandas as pd
import json


def is_valid_value(value):
    """检查字段值是否有效（即非空且不是'无'）"""
    return pd.notna(value) and str(value).strip() != "无"

def format_vehicle_description(row, selected_columns=None):
    if 'CAR_ID' in row.index:
        row = row.drop(labels='CAR_ID')

    if selected_columns is not None:
        row = row[selected_columns]

    input_parts = {}
    for col in row.index:
        if is_valid_value(row[col]):
            input_parts[col] = row[col]

    return input_parts


def generate_json_with_all_inputs(csv_path, output_path, sample_n=None, selected_columns=None):
    df = pd.read_csv(csv_path)

    if sample_n is not None and sample_n < len(df):
        df = df.sample(n=sample_n)

    all_inputs = []
    for _, row in df.iterrows():
        record = format_vehicle_description(row, selected_columns=selected_columns)
        if record:
            all_inputs.append(record)

    with open(output_path, 'a', encoding='utf-8') as f:
        f.write("[\n")
        for i, item in enumerate(all_inputs):
            json_str = json.dumps(item, ensure_ascii=False)
            f.write(json_str)
            if i != len(all_inputs) - 1:
                f.write(",\n")  # 对象间换行加逗号
        f.write("\n]")

    print("✅ Finished writing JSON")


# 示例：选择字段
selected_fields = ['车型名称','厂商指导价_元']
generate_json_with_all_inputs(
    "../spiders/cleaned-csv-data/基本参数.csv",
    "../car_inputs.json",
    sample_n=20,
    selected_columns=selected_fields
)
