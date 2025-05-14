from sentence_transformers import SentenceTransformer
import json
import faiss
import numpy as np
from sklearn.preprocessing import normalize
from typing import Dict


class SimilarExtract:
    def __init__(self, model, index_path: str, json_path: str):
        self.model = model
        self.index_path = index_path
        self.json_path = json_path
        self.index, self.name_map = self.load_index()

    def load_index(self):
        # 加载 FAISS 索引和对应名称映射
        index = faiss.read_index(self.index_path)
        with open(self.json_path, 'r', encoding='utf-8') as f:
            name_map = json.load(f)
        return index, name_map

    def query_vector(self, user_input: str, k: int = 5) -> Dict[str, float]:
        # 获取归一化的句向量
        input_vector = normalize(
            self.model.encode([user_input], convert_to_numpy=True).astype(np.float32),
            norm='l2'
        )
        distances, indices = self.index.search(input_vector, k)

        result_vector = {}
        # print(f"「{user_input}」相似度：")
        for i, idx in enumerate(indices[0]):
            if str(idx) in self.name_map:
                car_name = self.name_map[str(idx)]
                similarity_score = distances[0][i]
                # print(f"{i + 1}. {car_name}, 相似度: {similarity_score:.4f}")
                result_vector[car_name] = round(float(similarity_score), 4)
        return result_vector

    def max_similar(self, vector_dict: Dict[str, float]):
        if vector_dict:
            most_similar_car = max(vector_dict, key=vector_dict.get)
            similarity_score = vector_dict[most_similar_car]
            return most_similar_car, similarity_score
        else:
            print("未找到相似结果。")
            return None, None

# if __name__ == "__main__":
#     model_path = r"..\models\models--moka-ai--m3e-base\snapshots\764b537a0e50e5c7d64db883f2d2e051cbe3c64c"
#
#     body_index = "../data/body_car_vectors_ip.index"
#     body_json = "../data/body_car_name.json"
#     object_index = "../data/object_car_vectors_ip.index"
#     object_json = "../data/object_car_name.json"
#     model = SentenceTransformer(model_path, device="cpu")
#     llm = SimilarExtract(model, object_index, object_json)
#     # 用户输入
#     user_input = "颜色"
#     vector_dict = llm.query_vector(user_input)
#     print(vector_dict)
#     print(llm.max_similar(vector_dict))

