import os
import csv
import json
import chardet

def detect_encoding(file_name):
    with open(file_name, "rb") as f:
        result = chardet.detect(f.read())
        return result['encoding']

csv_folder = "../spiders/cleaned-csv-data"
output_path = "../data/object_field_map.json"  # ✅ 改为具体的 JSON 文件

# 创建输出目录（如果不存在）
os.makedirs(os.path.dirname(output_path), exist_ok=True)

node_field_map = {}

for filename in os.listdir(csv_folder):
    if filename.endswith(".csv"):
        node_name = os.path.splitext(filename)[0]
        file_path = os.path.join(csv_folder, filename)

        try:
            with open(file_path, "r", encoding=detect_encoding(file_path)) as f:
                reader = csv.reader(f)
                headers = next(reader)
                node_field_map[node_name] = headers
        except Exception as e:
            print(f"构建失败：{filename}，错误信息：{e}")

# ✅ 写入 JSON 文件
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(node_field_map, f, ensure_ascii=False, indent=2)

print(f"✅ JSON 已保存至 {output_path}")
