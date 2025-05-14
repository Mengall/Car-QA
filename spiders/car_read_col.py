import chardet
import os
import csv
def detect_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
        return result['encoding']

def get_csv_headers(folder_path):
    for filename in os.listdir(folder_path):
        if filename.endswith('.csv'):
            file_path = os.path.join(folder_path, filename)
            encoding = detect_encoding(file_path)  # 自动检测文件编码
            with open(file_path, mode='r', encoding=encoding) as f:
                reader = csv.reader(f)
                headers = next(reader)
                print(f"{filename}")
                # print(" ".join(headers))

if __name__ == "__main__":
    folder_path = 'cleaned-csv-data'  # 替换为你的文件夹路径
    get_csv_headers(folder_path)
