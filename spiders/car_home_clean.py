import os
import csv
import chardet
import re

# 定义文件夹路径
folder_path = 'car-csv-data'
new_folder_path = 'cleaned1-csv-data'


def detect_encoding(file_path):
    """自动检测文件编码"""
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        try:
            with open(file_path, mode='r', encoding=encoding) as f:
                f.read(100)
            return encoding
        except UnicodeDecodeError:
            print(f"编码 {encoding} 无法正确解码，尝试使用 utf-8")
            return 'utf-8'


def process_column_name(column_name):
    """清洗字段名"""
    column_name = column_name.strip().replace("\t", "")
    column_name = re.sub(r'[（）]', '', column_name)
    column_name = re.sub(r'\((.*?)\)', r'_\1', column_name)
    column_name = column_name.replace(' ', '_')
    column_name = column_name.replace('.', '_').replace("+", "_")
    column_name = re.sub(r'[^a-zA-Z0-9_\u4e00-\u9fa5]', '_', column_name)
    return column_name


def fillna(row):
    """填充缺失值为空替换为 '无'"""
    return [cell if cell != '' else '无' for cell in row]


def process_csv_files(input_folder, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    csv_files = [f for f in os.listdir(input_folder) if f.endswith('.csv')]

    for csv_file in csv_files:
        file_path = os.path.join(input_folder, csv_file)
        encoding = detect_encoding(file_path)
        print(f"文件 {csv_file} 编码为: {encoding}")

        try:
            with open(file_path, mode='r', encoding=encoding) as file:
                csv_reader = csv.reader(file)
                header = next(csv_reader)

                cleaned_header = []
                seen_columns = set()
                kept_indices = []

                for i, column in enumerate(header):
                    cleaned_name = process_column_name(column)
                    if cleaned_name == '经销商报价':
                        continue
                    if cleaned_name in seen_columns:
                        continue
                    seen_columns.add(cleaned_name)
                    cleaned_header.append(cleaned_name)
                    kept_indices.append(i)

                new_file_path = os.path.join(output_folder, csv_file)
                with open(new_file_path, mode='w', encoding=encoding, newline='') as new_file:
                    csv_writer = csv.writer(new_file)
                    csv_writer.writerow(cleaned_header)

                    for row in csv_reader:
                        filled_row = fillna(row)
                        cleaned_row = [filled_row[i] for i in kept_indices]
                        csv_writer.writerow(cleaned_row)

                print(f"文件 {csv_file} 已保存到新文件夹 {output_folder}")

        except Exception as e:
            print(f"处理文件 {csv_file} 时出错: {e}")


# 执行清洗流程
process_csv_files(folder_path, new_folder_path)
