import pandas as pd
import json


def is_valid_value(value):
    """检查字段值是否有效（即非空且不是'无'）"""
    return pd.notna(value) and str(value).strip() != "无"

def format_vehicle_description(row, selected_columns=None):
    # 如果行数据中包含 'CAR_ID' 字段，先删除它
    if 'CAR_ID' in row.index:
        row = row.drop(labels='CAR_ID')

    # 如果提供了自定义字段，则只保留这些字段
    if selected_columns is not None:
        row = row[selected_columns]

    # 将字段组合成输入部分（文本内容）
    input_parts = []
    for col in row.index:
        if is_valid_value(row[col]):  # 使用 is_valid_value 过滤“无”值
            input_parts.append(f"{col}：{row[col]}")
    input_text = ",".join(input_parts)

    # 拼接车辆描述的输出部分
    desc = []

    # 品牌系列、车型、厂商、级别、上市时间、价格
    if is_valid_value(row.get("车型名称")):
        desc.append(f"这款 {row['车型名称']}")
    if is_valid_value(row.get("品牌系列")):
        desc.append(f" 属于{row['品牌系列']}系列，")

    if is_valid_value(row.get("厂商")):
        desc.append(f"由{row['厂商']}生产，")
    if is_valid_value(row.get("级别")):
        desc.append(f"级别为{row['级别']}")
    if is_valid_value(row.get("上市时间")):
        desc.append(f"，于{row['上市时间']}上市")
    price = row.get("厂商指导价_元")  # 确保字段名一致
    if is_valid_value(price):
        if "万" not in str(price):
            price = f"{float(price) / 10000:.2f}万"
        desc.append(f"，官方指导价为{price}元")
    if is_valid_value(row.get("能源类型")):
        desc.append(f"，能源类型为{row['能源类型']}")
    if is_valid_value(row.get("环保标准")):
        desc.append(f"，环保标准{row['环保标准']}")
    # 能源类型 环保标准 NEDC综合油耗_L_100km 实测电池快充电量范围__

    # 动力、变速箱
    if is_valid_value(row.get("发动机")):
        desc.append(f"。\n动力方面：搭载了{row['发动机']}发动机")
    if is_valid_value(row.get("变速箱")):
        desc.append(f"，配备{row['变速箱']}变速箱")

    # 基本性能
    if is_valid_value(row.get("车身结构")):
        desc.append(f"。\n基本性能：车身结构为{row['车身结构']}")
    if is_valid_value(row.get("长_宽_高_mm")):
        desc.append(f"，车身尺寸为{row['长_宽_高_mm']}（长×宽×高）")
    if is_valid_value(row.get("官方0_50km_h加速_s")):
        desc.append(f"，官方50公里加速为{row['官方0_50km_h加速_s']}秒")
    if is_valid_value(row.get("官方0_100km_h加速_s")):
        desc.append(f"，官方百公里加速为{row['官方0_100km_h加速_s']}秒")
    if is_valid_value(row.get("最高车速_km_h")):
        desc.append(f"，最高时速可达{row['最高车速_km_h']}km/h")
    if is_valid_value(row.get("WLTC综合油耗_L_100km")):
        desc.append(f"，WLTC综合油耗为{row['WLTC综合油耗_L_100km']}L/100km")
    if is_valid_value(row.get("实测油耗_L_100km")):
        desc.append(f"，实测油耗为{row['实测油耗_L_100km']}L/100km")

    # 新能源相关
    if is_valid_value(row.get("电动机_Ps")):
        desc.append(f"。\n新能源相关有：电动机最大功率为{row['电动机_Ps']}马力")
    if is_valid_value(row.get("NEDC纯电续航里程_km")):
        desc.append(f"，NEDC纯电续航为{row['NEDC纯电续航里程_km']}公里")

    # 其他性能指标
    if is_valid_value(row.get("最大功率_kW")):
        desc.append(f"。\n其他性能指标：最大功率为{row['最大功率_kW']}kW")
    if is_valid_value(row.get("最大扭矩_N_m")):
        desc.append(f"，最大扭矩为{row['最大扭矩_N_m']}N·m")
    if is_valid_value(row.get("整备质量_kg")):
        desc.append(f"，整备质量为{row['整备质量_kg']}kg")
    if is_valid_value(row.get("最大满载质量_kg")):
        desc.append(f"，最大满载质量为{row['最大满载质量_kg']}kg")
    if is_valid_value(row.get("WLTC纯电续航里程_km")):
        desc.append(f"，WLTC纯电续航为{row['WLTC纯电续航里程_km']}公里")
    if is_valid_value(row.get("电池快充时间_小时")):
        desc.append(f"，电池快充时间为{row['电池快充时间_小时']}小时")
    if is_valid_value(row.get("电池慢充时间_小时")):
        desc.append(f"，电池慢充时间为{row['电池慢充时间_小时']}小时")
    if is_valid_value(row.get("电池快充电量范围__")):
        desc.append(f"，电池快充电量范围为{row['电池快充电量范围__']}（%）")

    # 油电综合和能耗
    if is_valid_value(row.get("NEDC综合油耗_L_100km")):
        desc.append(f"。\n油电综合和能耗：NEDC综合油耗为{row['NEDC综合油耗_L_100km']}L/100km")
    if is_valid_value(row.get("油电综合燃料消耗量_L_100km")):
        desc.append(f"，油电综合燃料消耗量为{row['油电综合燃料消耗量_L_100km']}L/100km")
    if is_valid_value(row.get("电能当量燃料消耗量_L_100km")):
        desc.append(f"，电能当量燃料消耗量为{row['电能当量燃料消耗量_L_100km']}L/100km")
    if is_valid_value(row.get("最低荷电状态油耗_L_100kmWLTC")):
        desc.append(f"，最低荷电状态油耗为{row['最低荷电状态油耗_L_100kmWLTC']}L/100km")
    if is_valid_value(row.get("CLTC纯电续航里程_km")):
        desc.append(f"，CLTC纯电续航为{row['CLTC纯电续航里程_km']}公里")
    if is_valid_value(row.get("最低荷电状态油耗_L_100km")):
        desc.append(f"，最低荷电状态油耗为{row['最低荷电状态油耗_L_100km']}L/100km")
    if is_valid_value(row.get("最低荷电状态油耗_L_100kmCLTC")):
        desc.append(f"，最低荷电状态油耗为{row['最低荷电状态油耗_L_100kmCLTC']}L/100km")
    if is_valid_value(row.get("官方100_0km_h制动_m")):
        desc.append(f"，官方100-0km/h制动为{row['官方100_0km_h制动_m']}米")

    # 实测数据
    if is_valid_value(row.get("实测0_100km_h加速_s")):
        desc.append(f"。\n实测数据：实测百公里加速为{row['实测0_100km_h加速_s']}秒")
    if is_valid_value(row.get("实测100_0km_h制动_m")):
        desc.append(f"，实测100-0km/h制动为{row['实测100_0km_h制动_m']}米")
    if is_valid_value(row.get("实测油耗_L_100km")):
        desc.append(f"，实测油耗为{row['实测油耗_L_100km']}L/100km")
    if is_valid_value(row.get("实测续航里程_km")):
        desc.append(f"，实测续航里程为{row['实测续航里程_km']}公里")
    if is_valid_value(row.get("实测电池快充电量范围__")):
        desc.append(f"，实测电池快充电量范围为{row['实测电池快充电量范围__']}")
    if is_valid_value(row.get("实测快充时间_小时")):
        desc.append(f"，实测快充时间为{row['实测快充时间_小时']}小时")
    # if is_valid_value(row.get("实测最低荷电状态油耗_L_100km")):
    #     desc.append(f"，实测最低荷电状态油耗为{row['实测最低荷电状态油耗_L_100kmNEDC']}L/100km")
    if is_valid_value(row.get("实测平均电耗_kWh_100km")):
        desc.append(f"，实测平均电耗为{row['实测平均电耗_kWh_100km']}kWh/100km")


    # 其他字段
    if is_valid_value(row.get("整车质保")):
        desc.append(f"。\n其他：提供{row['整车质保']}整车质保")
    if is_valid_value(row.get("准拖挂车总质量_kg")):
        desc.append(f"，准拖挂车总质量为{row['准拖挂车总质量_kg']}kg")
    if is_valid_value(row.get("首任车主质保政策")):
        desc.append(f"，首任车主质保政策为{row['首任车主质保政策']}")


    # 拼接完成描述
    output_text = "".join(desc).rstrip("，。") + "。"
    print(output_text)
    return {
        "instruction": "请根据以下车辆信息生成简洁的自然语言描述，输出结构为output值的结构。",
        "input": input_text,
        "output": output_text
    }



def generate_jsonl_from_csv(csv_path, output_path, sample_n=None, selected_columns=None):
    # 读取CSV文件
    df = pd.read_csv(csv_path)

    # 如果需要采样数据
    if sample_n is not None and sample_n < len(df):
        df = df.sample(n=sample_n)

    # 打开输出文件，并逐行生成JSONL
    with open(output_path, 'a', encoding='utf-8') as f:
        for _, row in df.iterrows():
            record = format_vehicle_description(row, selected_columns=selected_columns)
            # print(record)
            f.write(json.dumps(record, ensure_ascii=False) + '\n')

#{'车型名称': '奔驰E级 2025款 改款 E 260 L', '品牌系列': '奔驰E级', '厂商指导价_元': '45.18万', '厂商': '北京奔驰', '级别': '中大型车', '能源类型': '汽油+48V轻混系统', '环保标准': '国VI', '上市时间': '2025.03'}
# 示例：选择自定义字段生成描述
selected_fields = ['车型名称','厂商指导价_元']
generate_jsonl_from_csv(
    "../spiders/cleaned-csv-data/基本参数.csv",
    "car_finetune_data.jsonl",
    sample_n=5,
    selected_columns=selected_fields
)

print("successed")