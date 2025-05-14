import pandas as pd
from collections import defaultdict
import json
import chardet

def detect_encoding(file_path):
    """自动检测 CSV 文件编码"""
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

brand = r"spiders/cleaned-csv-data/品牌系列.csv"
car = r"spiders/cleaned-csv-data/基本参数.csv"

# 读取CSV文件
brand_series_df = pd.read_csv(brand, encoding=detect_encoding(brand))
model_df = pd.read_csv(car, encoding=detect_encoding(car))

# 创建品牌 → 品牌系列 → [车型] 的嵌套结构
brand_dict = defaultdict(lambda: defaultdict(list))

# 建立 品牌系列 → 所有车型 的映射
series_to_models = defaultdict(list)
for _, row in model_df.iterrows():
    # print(row)
    series = row['品牌系列']
    model = row['车型名称']
    series_to_models[series].append(model)

# 建立 品牌 → 品牌系列 → 所有车型 的映射
for _, row in brand_series_df.iterrows():
    brand = row['品牌']
    series = row['品牌系列']
    models = series_to_models.get(series, [])
    brand_dict[brand][series].extend(models)

# 可选：转换为普通字典
brand_dict = {k: dict(v) for k, v in brand_dict.items()}

# 将字典保存为JSON文件
with open('../data/body_field_map.json', 'w', encoding='utf-8') as f:
    json.dump(brand_dict, f, ensure_ascii=False, indent=2)

print("数据已保存为品牌_车型_mapping.json")
