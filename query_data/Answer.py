# 导入所需模块
import time
from neo4j import GraphDatabase  # 用于连接 Neo4j 图数据库
from query_data.Extract import QueryHandler  # 自定义类：用于从问题中抽取结构化信息
from otherDeal import queries  # 自定义模块：包含 Cypher 查询语句生成函数
import os
from query_data.llama_answer import LoadModel  # 自定义类：加载 LLaMA 模型并进行推理
import re
import time
from query_data.Rule_match import get_series
import json

# 定义核心处理类
class CarQueryProcessor:
    def __init__(self, neo4j_url, username, password, model_path, body_index, body_json, object_index, object_json,
                 body_path, object_path):
        # 初始化数据库连接
        self.driver = GraphDatabase.driver(neo4j_url, auth=(username, password))
        # 初始化问题抽取器（用向量匹配抽取主体、客体、节点、字段）
        self.query_handler = QueryHandler(model_path, body_index, body_json, object_index, object_json, body_path,
                                          object_path)
        # 初始化 LLM 模型加载器
        self.loadModel = LoadModel()
        self.model, self.tokenizer = self.loadModel.load_lora_model()  # 模型只加载一次
        # 定义合法节点类型列表，用于判断是否可查询
        self.node_categories = [
            "主动安全", "发动机", "变速箱", "四驱_越野", "外后视镜", "外观_防盗", "天窗_玻璃", "屏幕_系统",
            "底盘转向", "座椅配置", "方向盘_内后视镜", "智能化配置", "特色配置", "电动机", "电池_充电", "空调_冰箱", "被动安全",
            "车内充电", "车外灯光", "车身", "车轮制动", "选装包", "音响_车内灯光", "颜色", "驾驶功能", "驾驶操控", "驾驶硬件"]
        self.car_brand = ["奔驰", "宝马", "比亚迪", "大众", "奥迪", "本田", "保时捷", "特斯拉", "红旗", "丰田", "别克", "小米汽车", "吉利汽车"]
        self.car_series = get_series()  # 所有系列

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

    def get_brand_series_car(self, data):
        query_list = []
        for items in data:
            merge_item = {}
            items = items.get("查询结果")
            for item in items:
                car = item.get("车型名称")
                series = item.get("品牌系列")


    # 判断是否是有效的节点类别
    def is_valid_node(self, node_name):
        return node_name in self.node_categories

    # 根据节点和字段构造查询 品牌->系列 系列->车型 系列->品牌 车型->系列 车型->品牌
    def handle_query(self, car_name, node_name, node_field):
        # 系列查车型
        if car_name in self.car_series and node_field == "车型名称":
            query = queries.q_series_car(car_name)
            result = self.query_car_info(query)  # 查询函数，返回结果或 None
            answer = car_name + "系列的车型包括：\n" + "\n".join(
                ["\t" + item.get("车型名称", "") for item in result]
            )
            return {"其他查询": answer}
        # 车辆基本信息
        elif node_name == "基本参数":
            query = queries.q_basic_info(car_name, node_field)
        # 品牌查系列
        elif car_name in self.car_brand and node_name == "品牌系列":
            query = queries.q_brand_series(car_name)
            result = self.query_car_info(query)  # 查询函数，返回结果或 None
            answer = car_name + "品牌的系列包括：\n" + "\n".join(
                ["\t" + item.get("品牌系列") for item in result]
            )
            return {"其他查询": answer}
        # 车型查系列
        elif node_name == "品牌系列":
            query = queries.q_car_series(car_name)
            result = self.query_car_info(query)
            answer = car_name + "的系列是：" + "\n".join(
                [item.get("品牌系列") for item in result]
            )
            return {"其他查询": answer}
        # 系列查品牌
        elif car_name in self.car_series and node_name == "品牌":
            # 先尝试根据 品牌系列查询品牌
            query = queries.q_series_brand(car_name)
            result = self.query_car_info(query)
            answer = car_name + "系列的品牌是：" + "\n".join(
                [item.get("品牌") for item in result]
            )
            return {"其他查询": answer}
        # 车型查品牌
        elif node_name == "品牌":
            query = queries.q_car_brand(car_name)
            result = self.query_car_info(query)
            answer = car_name + "的品牌是：" + "\n".join(
                [item.get("品牌") for item in result]
            )
            return {"其他查询": answer}
        # 车辆其他配置
        elif self.is_valid_node(node_name):
            query = queries.q_node_parm(car_name, node_name, node_field)
        else:
            return None
        raw_result = self.query_car_info(query)
        return self.clean_result_keys(raw_result)

    # 从自然语言问题中抽取结构化查询信息（车名、节点、字段）
    def extract_question_result(self, question):
        return self.query_handler.extract_information(question)

    # 遍历结构化查询条件并查询结果
    def batch_query_from_question(self, question):
        try:
            structured_data = self.extract_question_result(question)
            print("三元组提取结果：", structured_data)
            # structured_data是非结构化数据，返回None
            if not structured_data or not isinstance(structured_data, list):
                return None
            all_results = []
            # print("大模型API+抽取结果：", structured_data)
            for data in structured_data:
                car = data['主体']
                single_car_result = {
                    "车型名称": car,
                    "查询结果": []
                }
                for obj in data['客体']:
                    node = obj.get('节点')
                    field = obj.get('字段')
                    # 如果字段是'null'，将其置为 None 或者直接跳过
                    if field == 'null':
                        field = None
                    print(f"查询：{car} -> {node} - {field}")
                    s_time = time.time()
                    query_result = self.handle_query(car, node, field)
                    print("查询结果：", query_result)
                    if isinstance(query_result, dict) and query_result.get("其他查询"):
                        return query_result
                    # all_results.extend(query_result)  # 合并查询结果
                    # 合并查询结果
                    if isinstance(query_result, list):
                        single_car_result["查询结果"].extend(query_result)
                    else:
                        single_car_result["查询结果"].append(query_result)
                    print(f"耗时：{time.time() - s_time:.2f} 秒\n")
                # 每个车型查询完后追加到最终列表
                all_results.append(single_car_result)
            # print('查询结果：', all_results)
            print("查询结果：", json.dumps(all_results, indent=2, ensure_ascii=False))
            # if  all_results["查询结果"]:


            # 初始化一个空字典
            answers = []
            for entry in all_results:
                merged = {}
                car_param = entry.get("查询结果", list)
                # print(car_param)
                for item in car_param:
                    car_name = item.get("车型名称", "")
                    s = item.get("s", dict)
                    n = item.get("n", dict)
                    if car_name:
                        merged["车型名称"] = car_name
                        # 合并除"车型名称"外的其他字段
                    for key, value in item.items():
                        if key != "车型名称" and value is not None:
                            if isinstance(value, dict):
                                merged.update(value)  # 展开字典合并
                            else:
                                merged[key] = value  # 直接添加非字典值
                    if isinstance(s, dict):
                        merged.update(s)
                    if isinstance(n, dict):
                        merged.update(n)

                # 删除值为"无"的字段
                cleaned = {k: v for k, v in merged.items() if v != "无"}
                answers.append({"配置查询": cleaned})
            # print("输出结果：", answers)
            return answers
        except Exception as e:
            print(e)

    # 基于 LLM 模型生成自然语言回答
    def llm_answer(self, text):
        # print("输入：", text)
        if not text:
            return "请输入汽车领域相关的问题！"
        elif isinstance(text, dict) and text["其他查询"]:
            return text["其他查询"]
        elif isinstance(text, list) and text[0]["配置查询"]:
            prompt = f"""请根据以下'输入'字段中的JSON格式车辆信息生成简洁的自然语言描述。生成的结果应该以'输出'字段的形式呈现：\n输入：{text}\n输出："""
            result = self.loadModel.infer(prompt, self.model, self.tokenizer)
            print("生成结果：", result)
            result = self.cleanOutput(result)
            # print("处理结果：", result)
        else:
            return "暂无信息"
        return result

    # 去掉字典值为 无 的数据
    def remove_none_values(d):
        return {k: v for k, v in d.items() if v != "无"}

    # 提取 LLM 输出中的最终结果
    def cleanOutput(self, output):
        answer = re.search(r'输出：(.*)', output, re.DOTALL).group(1).strip()
        answer = answer.replace("*", "x")
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
        print('\n问题：', text)
        result = processor.llm_answer(text)
        print('\n回答：', result)

