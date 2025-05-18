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

    input_parts = []
    for col in row.index:
        if is_valid_value(row[col]):
            input_parts.append(f"{col}：{row[col]}")
    input_text = ",".join(input_parts)

    desc = []

    if is_valid_value(row.get("品牌系列")):
        desc.append(f"该车属于{row['品牌系列']}系列")
    if is_valid_value(row.get("车型名称")):
        desc.append(f"，这款 {row['车型名称']} 在安全气囊配置上较为完善。")
    if is_valid_value(row.get("主_副驾驶座安全气囊")):
        desc.append(f"配备了主/副驾驶座安全气囊（{row['主_副驾驶座安全气囊']}）")
    if is_valid_value(row.get("前_后排侧气囊")):
        desc.append(f"，前/后排侧气囊为（{row['前_后排侧气囊']}）")
    if is_valid_value(row.get("前_后排头部气囊_气帘")):
        desc.append(f"，前/后排头部气囊（气帘）配置为（{row['前_后排头部气囊_气帘']}）")
    if is_valid_value(row.get("膝部气囊")):
        desc.append(f"，膝部气囊配置为（{row['膝部气囊']}）")
    if is_valid_value(row.get("前排中间气囊")):
        desc.append(f"，前排中间气囊：{row['前排中间气囊']}")
    if is_valid_value(row.get("被动行人保护")):
        desc.append(f"，具备被动行人保护功能（{row['被动行人保护']}）")
    if is_valid_value(row.get("后排正向安全气囊")):
        desc.append(f"，后排正向安全气囊：{row['后排正向安全气囊']}")
    if is_valid_value(row.get("缺气保用轮胎")):
        desc.append(f"，配备缺气保用轮胎：{row['缺气保用轮胎']}")
    if is_valid_value(row.get("后排中央安全气囊")):
        desc.append(f"，后排中央安全气囊：{row['后排中央安全气囊']}")
    if is_valid_value(row.get("副驾驶座垫式气囊")):
        desc.append(f"，副驾驶座垫式气囊：{row['副驾驶座垫式气囊']}")

    output_text = "".join(desc).rstrip("，。") + "。"

    return {
        "instruction": "请根据以下车辆信息生成简洁的自然语言描述。",
        "input": input_text,
        "output": output_text
    }

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

    # 写入 JSONL 文件
    with open(output_path, 'a', encoding='utf-8') as f:
        for _, row in df_merged.iterrows():
            record = format_vehicle_description(row, selected_columns=selected_columns)
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

selected_columns = ['车型名称','发动机型号','排量_mL','排量_L','最大马力_Ps','最大功率_kW','最大功率转速_rpm']
# 示例调用
generate_jsonl_from_csv(
    engine_csv_path="../spiders/cleaned-csv-data/被动安全.csv",
    basic_info_csv_path="../spiders/cleaned-csv-data/基本参数.csv",
    output_path="car_finetune_data.jsonl",
    sample_n=100,
    # selected_columns=selected_columns  # 可指定感兴趣字段
)

print("successed")
