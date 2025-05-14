from sentence_transformers import SentenceTransformer
import json
import faiss
import numpy as np
from sklearn.preprocessing import normalize


def load_json(path):
    with open(path, 'r', encoding="utf-8") as f:
        car_data = json.load(f)
        print(car_data)
    return car_data


def json_conv_vector(json_path, save_index_path, save_name_path):
    # 模型路径
    model_path = r"..\models\models--moka-ai--m3e-base\snapshots\764b537a0e50e5c7d64db883f2d2e051cbe3c64c"
    # 加载模型
    model = SentenceTransformer(model_path)

    # texts = ["奔驰E级 2025款 E 260 L", "宝马5系 530Li 豪华型"]
    # vectors = model.encode(texts)
    # print(len(vectors[0]))

    # 加载json数据
    body_car = load_json(json_path)

    # 设置余弦相似度索引（IP）
    index = faiss.IndexFlatIP(768)

    # 用于存储车型名称和对应的索引
    all_car_names = []
    all_car_vectors = []

    # 1.遍历主体车型数据，将车型名称转化为向量
    # for brand, series_dict in body_car.items():
    #     for series, cars in series_dict.items():
    #         for car in cars:
    #             all_car_names.append(car)  # 保存车型名称
    #             car_vector = model.encode([car])  # 获取车型名称的向量
    #             all_car_vectors.append(car_vector[0])  # 提取向量（模型返回的是二维数组）

    # 2.遍历客体字段数据，将字段名转化为向量
    for node, cols in body_car.items():
        for col in cols:
            all_car_names.append(col)
            car_vector = model.encode([col])
            all_car_vectors.append(car_vector[0])

    # 将所有车型向量转化为 numpy 数组
    car_vectors_np = normalize(np.array(all_car_vectors).astype(np.float32), norm="l2")

    # 将向量添加到 FAISS 索引
    index.add(car_vectors_np)

    # 保存 FAISS 索引文件和车型名称映射
    faiss.write_index(index, save_index_path)

    # 创建车型名称到索引的映射
    car_names_map = {i: name for i, name in enumerate(all_car_names)}
    with open(save_name_path, 'w', encoding='utf-8') as f:
        json.dump(car_names_map, f, ensure_ascii=False, indent=2)

    print("向量数据库已构建并保存,余弦相似度。")


# 车型数据库
body_json_path = r"../data/body_field_map.json"
object_json_path = r"../data/object_field_map.json"
# 存储向量文件路径
save_index_path = "../data/object_car_vectors_ip.index"
# 存储索引文件路径
save_name_path = r'../data/object_car_name.json'
# 运行
# json_conv_vector(object_json_path, save_index_path, save_name_path)
