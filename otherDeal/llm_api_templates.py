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

def generate_jsonl_from_csv(engine_csv_path, basic_info_csv_path, output_path, sample_n=None, selected_columns=None):
    # 读取发动机CSV
    df_engine = pd.read_csv(engine_csv_path)
    # 读取基本参数CSV
    df_basic = pd.read_csv(basic_info_csv_path)
    df_basic = df_basic.iloc[:, [0, 2]]

    # 合并数据：通过 CAR_ID 左连接
    df_merged = df_engine.merge(df_basic, on="CAR_ID", how="left")

    # 如果需要采样
    if sample_n is not None and sample_n < len(df_merged):
        df_merged = df_merged.sample(n=sample_n)

    all_inputs = []
    for _, row in df_merged.iterrows():
        record = format_vehicle_description(row, selected_columns=selected_columns)
        if record:
            all_inputs.append(record)

    # 写入 JSONL 文件
    with open(output_path, 'a', encoding='utf-8') as f:
        f.write("[\n")
        for i, item in enumerate(all_inputs):
            json_str = json.dumps(item, ensure_ascii=False)
            f.write(json_str)
            if i != len(all_inputs) - 1:
                f.write(",\n")  # 对象间换行加逗号
        f.write("\n]")

selected_columns = ['车型名称','发动机型号','排量_mL','排量_L','最大马力_Ps','最大功率_kW','最大功率转速_rpm']
# 示例调用 基本参数、发动机、变速箱、颜色、选装包、车身、电池、主动安全、被动安全、四驱-越野、外后视镜、外观-防盗、天窗-玻璃、屏幕-系统、底盘转向
# 座椅配置、方向盘-内后视镜、智能化配置、特色配置、电动机、电池-充电、空调-冰箱、车内充电、车外灯光、车轮制动、音响-车内灯光
generate_jsonl_from_csv(
    engine_csv_path="../spiders/cleaned-csv-data/音响-车内灯光.csv",
    basic_info_csv_path="../spiders/cleaned-csv-data/基本参数.csv",
    output_path="../test.json",
    sample_n=30,
    # selected_columns=selected_columns  # 可指定感兴趣字段
)

print("successed")
