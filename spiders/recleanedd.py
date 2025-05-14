import os
import pandas as pd
import chardet
# 设置要遍历的文件夹路径
folder_path = "./car-csv-data"  # 根据你的目录结构修改

def detect_encoding(file_path):
    """自动检测文件编码"""
    with open(file_path, 'rb') as file:
        raw_data = file.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        # 尝试用 chardet 失败时备用编码
        try:
            with open(file_path, mode='r', encoding=encoding) as f:
                f.read(100)  # 读取文件的一部分来确认编码是否正确
            return encoding
        except UnicodeDecodeError:
            print(f"编码 {encoding} 无法正确解码，尝试使用 utf-8")
            return 'utf-8'
k = 0
# 遍历该文件夹下所有 CSV 文件
for filename in os.listdir(folder_path):
    if filename.endswith(".csv"):
        file_path = os.path.join(folder_path, filename)
        print(f"处理文件: {file_path}")

        try:
            # 读取 CSV 文件
            df = pd.read_csv(file_path, encoding=detect_encoding(file_path))  # 如遇编码问题可换成 'gbk', 'utf-8-sig' 等

            # 获取并打印原始表头
            original_columns = df.columns.tolist()
            print("原始表头:", original_columns)
            k+=1
            print(k)
            # === 🔧 在这里写你的表头预处理逻辑 ===
            # 例如：重命名、去除空格、统一大小写等
            # df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

            # === ✅ 可选：保存处理后的文件（比如另存为 _processed.csv） ===
            # new_file_path = file_path.replace(".csv", "_processed.csv")
            # df.to_csv(new_file_path, index=False)

        except Exception as e:
            print(f"⚠️ 处理文件出错: {file_path}，原因: {e}")
