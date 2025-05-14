import os
import pandas as pd
import chardet
from neo4j import GraphDatabase
import re
import numpy as np
from datetime import datetime

# 连接到 Neo4j 数据库
URI = "bolt://localhost:7687"  # 你的 Neo4j 地址
USERNAME = "neo4j"  # 你的用户名
PASSWORD = "neo4j0000"  # 你的密码
path = "cleaned-csv-data"

# 连接 Neo4j
driver = GraphDatabase.driver(URI, auth=(USERNAME, PASSWORD))


def detect_encoding(file_path):
    """自动检测 CSV 文件编码"""
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read())
    return result['encoding']

def sanitize_neo4j_string(input_string):
    # 将 `-` 替换为 `_`
    sanitized_string = input_string.replace('-', '_')
    return sanitized_string

def load_csv_to_neo4j(file_path, node_label):
    """
    读取 CSV 文件并导入 Neo4j，每个 CSV 作为一个节点类型，列作为属性
    """
    encoding = detect_encoding(file_path)

    try:
        df = pd.read_csv(file_path, encoding=encoding, sep=",", dtype=str)
    except Exception as e:
        print(f"读取 {file_path} 失败: {e}")
        return

    # 清理列名，防止非法字符导致 Cypher 语法错误
    # df.columns = [sanitize_neo4j_string(col) for col in df.columns]

    with driver.session() as session:
        for i, row in df.iterrows():
            clean_row = {k: v if pd.notna(v) else "无" for k, v in row.items()}

            properties = ", ".join(f"`{col}`: ${col}" for col in df.columns)  # 使用反引号包围列名

            query = f"""
            MERGE (n:{node_label} {{ {properties} }})
            """
            try:
                session.run(query, clean_row)
                # print(f"[{node_label}] 成功导入第 {i + 1} 行")
                # print(query)
                # print(f"成功导入一行数据到 {node_label} 节点。")
            except Exception as e:
                print(f"插入失败: {e} (文件: {file_path})")

def import_all_csv(folder_path):
    """
    遍历文件夹中的所有 CSV 文件并导入 Neo4j
    """
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".csv"):
            file_path = os.path.join(folder_path, file_name)
            # 通过去掉扩展名来得到节点标签名称
            node_label = sanitize_neo4j_string(os.path.splitext(file_name)[0])  # 以文件名作为节点名称
            print(f"正在导入 {file_name}（编码: {detect_encoding(file_path)}）到 Neo4j 节点 {node_label} ...")
            load_csv_to_neo4j(file_path, node_label)
    print("所有 CSV 文件导入完成！")


# 运行导入脚本
import_all_csv(path)

# 关闭数据库连接
driver.close()
