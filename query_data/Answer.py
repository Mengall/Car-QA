# 导入所需模块
import time
from neo4j import GraphDatabase  # 用于连接 Neo4j 图数据库
from query_data.Extract import QueryHandler  # 自定义类：用于从问题中抽取结构化信息
from otherDeal import queries  # 自定义模块：包含 Cypher 查询语句生成函数
import os
from query_data.llama_answer import LoadModel  # 自定义类：加载 LLaMA 模型并进行推理
import re
import time

# 定义核心处理类
class CarQueryProcessor:
    def __init__(self, neo4j_url, username, password, model_path, body_index, body_json, object_index, object_json, body_path, object_path):
        # 初始化数据库连接
        self.driver = GraphDatabase.driver(neo4j_url, auth=(username, password))
        # 初始化问题抽取器（用向量匹配抽取主体、客体、节点、字段）
        self.query_handler = QueryHandler(model_path, body_index, body_json, object_index, object_json, body_path, object_path)
        # 初始化 LLM 模型加载器
        self.loadModel = LoadModel()
        self.model, self.tokenizer = self.loadModel.load_lora_model()  # 模型只加载一次
        # 定义合法节点类型列表，用于判断是否可查询
        self.node_categories = [
            "主动安全", "发动机", "变速箱", "四驱_越野", "外后视镜", "外观_防盗", "天窗_玻璃", "屏幕_系统",
            "底盘转向", "座椅配置", "方向盘_内后视镜", "智能化配置", "特色配置", "电动机", "电池_充电", "空调_冰箱", "被动安全",
            "车内充电", "车外灯光", "车身", "车轮制动", "选装包", "音响_车内灯光", "颜色", "驾驶功能", "驾驶操控", "驾驶硬件"
        ]

    # 清洗从数据库查询出来的字段名称
    def clean_result_keys(self, raw_results):
        def clean_dict(d):
            cleaned = {}
            for key, value in d.items():
                # 去除前缀 n. 或 s.
                new_key = key.replace('n.', '').replace('s.', '')
                # 排除特定字段
                if new_key in {'CAR_ID', '系列ID', 'ID'}:
                    continue
                # 如果值是字典，则递归清洗
                if isinstance(value, dict):
                    value = clean_dict(value)
                cleaned[new_key] = value
            return cleaned

        return [clean_dict(entry) for entry in raw_results]

    # 使用 Cypher 语句查询 Neo4j 数据库
    def query_car_info(self, query):
        with self.driver.session() as session:
            result = session.run(query)
            parsed_results = []

            for record in result:
                entry = {}
                for key in record.keys():
                    value = record[key]
                    # 如果是属性节点对象则转为字典
                    entry[key] = dict(value.items()) if hasattr(value, 'items') else value
                parsed_results.append(entry)

            return parsed_results

    # 判断是否是有效的节点类别
    def is_valid_node(self, node_name):
        return node_name in self.node_categories

    # 根据节点和字段构造查询
    def handle_query(self, car_name, node_name, node_field):
        if node_name == "基本参数":
            query = queries.q_basic_info(car_name, node_field)
        elif self.is_valid_node(node_name):
            query = queries.q_node_parm(car_name, node_name, node_field)
        else:
            return "暂无信息"

        raw_result = self.query_car_info(query)
        return self.clean_result_keys(raw_result)

    # 从自然语言问题中抽取结构化查询信息（车名、节点、字段）
    def extract_question_result(self, question):
        return self.query_handler.extract_information(question)

    # 遍历结构化查询条件并查询结果
    def batch_query_from_question(self, question):
        structured_data = self.extract_question_result(question)
        all_results = []
        print("大模型API+抽取结果：", structured_data)
        for data in structured_data:
            car = data['主体']
            for obj in data['客体']:
                node = obj['节点']
                field = obj['字段']
                # 如果字段是'null'，将其置为 None 或者直接跳过
                if field == 'null':
                    field = None
                print(f"查询：{car} -> {node} - {field}")
                s_time = time.time()
                query_result = self.handle_query(car, node, field)
                all_results.extend(query_result)  # 合并查询结果
                print(f"耗时：{time.time() - s_time:.2f} 秒\n")

        print('查询结果：', all_results)

        # 格式化结果为简洁结构
        answers = []
        for entry in all_results:
            car_name = entry.get("车型名称", "")
            s = entry.get('s', {})
            n = entry.get('n', {})
            answer = {"车型名称": car_name} if car_name else {}

            for source in [s, n]:
                for key, value in source.items():
                    if value != "无":
                        answer[key] = value

            # 保留其他字段
            for key, value in entry.items():
                if key not in ("s", "n", "车型名称") and value != "无":
                    answer[key] = value
            answers.append(answer)
        return answers

    # 基于 LLM 模型生成自然语言回答
    def llm_answer(self, text):
        prompt = f"""请根据以下'输入'字段中的JSON格式车辆信息生成简洁的自然语言描述。生成的结果应该以'输出'字段的形式呈现：\n输入：{text}\n输出："""
        result = self.loadModel.infer(prompt, self.model, self.tokenizer)
        print("生成结果：", result)
        result = self.cleanOutput(result)
        # print("处理结果：", result)
        return result

    # 提取 LLM 输出中的最终结果
    def cleanOutput(self, output):
        answer = re.search(r'输出：(.*)', output, re.DOTALL).group(1).strip()
        return answer


# 入口函数
if __name__ == "__main__":
    # 初始化查询处理器
    processor = CarQueryProcessor(
        neo4j_url="bolt://localhost:7687",
        username="neo4j",
        password="neo4j0000",
        model_path=r"..\models\models--moka-ai--m3e-base\snapshots\764b537a0e50e5c7d64db883f2d2e051cbe3c64c",
        body_index="../data/body_car_vectors_ip.index",
        body_json="../data/body_car_name.json",
        object_index="../data/object_car_vectors_ip.index",
        object_json="../data/object_car_name.json",
        body_path="../data/body_field_map.json",
        object_path="../data/object_field_map.json"
    )

    # 进入交互式提问循环
    while True:
        question = input("请输入问题：\n")
        text = processor.batch_query_from_question(question)
        print(text)
        result = processor.llm_answer(text)
        print(result)
