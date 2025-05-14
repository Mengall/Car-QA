import json
import time
from collections import defaultdict
from query_data.QW_api import LLMExtract
from TextVector.Similar_match import SimilarExtract
from sentence_transformers import SentenceTransformer
from query_data.Rule_match import merge_same_node_fields, is_car_in_body, are_fields_valid, load_json_file

class QueryHandler:
    def __init__(self, model_path, body_index, body_json, object_index, object_json, body_path, object_path):
        self.model_path = model_path
        self.body_index = body_index
        self.body_json = body_json
        self.object_index = object_index
        self.object_json = object_json
        self.body_data = load_json_file(body_path)
        self.object_data = load_json_file(object_path)

    def format_dict(self, data):
        """ 格式化字典为 JSON 字符串 """
        return json.dumps(data, ensure_ascii=False, indent=4)

    def get_most_similar(self, sim_model, text, threshold=0.5, k=5):
        """ 获取最相似的项，返回名称和相似度 """
        try:
            vector_dict = sim_model.query_vector(text, k)
            if not vector_dict:
                return None, 0.0

            most_similar = max(vector_dict.items(), key=lambda x: x[1])
            if most_similar[1] >= threshold:
                return most_similar
            else:
                return None, most_similar[1]
        except Exception as e:
            print(f"[错误] 向量匹配失败：{e}")
            return None, 0.0

    def similar_match(self, llm_output):
        model = SentenceTransformer(self.model_path, device="cpu")
        body_llm = SimilarExtract(model, self.body_index, self.body_json)
        object_llm = SimilarExtract(model, self.object_index, self.object_json)
        print("向量模型当前模型所在设备：", next(model.parameters()).device)
        # 向量相似度匹配处理
        result_list = []  # 新增：用于保存最终结构化结果
        for data_list in llm_output:
            object_list = []  # 每个主体对应的客体列表
            max_similar_field, _ = self.get_most_similar(body_llm, data_list[0])

            for node_field_list in data_list[1:]:
                node = node_field_list['节点']
                field = None
                if node_field_list['字段'] and str(node_field_list['字段']).lower() != 'null':
                    field, _ = self.get_most_similar(object_llm, node_field_list['字段'])
                object_list.append({
                    "节点": node,
                    "字段": field
                })

            # ✅ 合并节点相同的字段
            merged = defaultdict(list)
            null_fields = []

            for item in object_list:
                node = item["节点"]
                field = item["字段"]

                if field is None or str(field).lower() == "null":
                    null_fields.append({"节点": node, "字段": "null"})
                else:
                    merged[node].append(field)

            object_list = []
            for node, fields in merged.items():
                if len(fields) == 1:
                    object_list.append({"节点": node, "字段": fields[0]})
                else:
                    object_list.append({"节点": node, "字段": fields})
            object_list.extend(null_fields)

            result = {
                "主体": max_similar_field,
                "客体": object_list
            }
            result_list.append(result)
        return result_list

    def convert_triplets_to_dict(self, llm_output):
        """
        将大模型或规则匹配输出格式：
        [['主体1', {'节点': 'xx', '字段': 'xx'}, {...}], ['主体2', {...}, {...}]]
        转换为统一格式：
        [{'主体': '主体1', '客体': [...]}]
        """
        formatted = []
        for item in llm_output:
            if isinstance(item, list) and len(item) >= 1:
                subject = item[0]
                objects = item[1:]
                formatted.append({
                    "主体": subject,
                    "客体": objects
                })
        return formatted

    def extract_information(self, question):
        """ 处理输入问题，返回处理结果 """
        start = time.time()
        # 大模型三元组提取
        llm = LLMExtract()
        llm_output = llm.get_api_modle(question)
        # 规则匹配
        if is_car_in_body(llm_output, self.body_data) and are_fields_valid(llm_output, self.object_data):
            result = merge_same_node_fields(llm_output)
            result = self.convert_triplets_to_dict(result)
            print("规则匹配结果：", result)
        # 向量相似度匹配
        else:
            result = self.similar_match(llm_output)
            print("向量匹配结果：", result)
        end = time.time()
        print(f"处理耗时: {end - start}秒")
        return result


if __name__ == "__main__":
    # 配置路径
    model_path = r"..\models\models--moka-ai--m3e-base\snapshots\764b537a0e50e5c7d64db883f2d2e051cbe3c64c"
    body_index = "../data/body_car_vectors_ip.index"
    body_json = "../data/body_car_name.json"
    object_index = "../data/object_car_vectors_ip.index"
    object_json = "../data/object_car_name.json"
    body_data = "../data/body_field_map.json"
    object_data = "../data/object_field_map.json"

    # 初始化 QueryHandler
    query_handler = QueryHandler(model_path, body_index, body_json, object_index, object_json, body_data, object_data)

    # 示例问题
    question = "奔驰E级 2025款 改款 E 260 L的颜色和发动机"
    results = query_handler.extract_information(question)

    # 打印最终结果
    print("最终提取结果：")
    print(results)
    print(json.dumps(results, ensure_ascii=False, indent=4))