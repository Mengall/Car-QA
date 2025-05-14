from neo4j import GraphDatabase
from otherDeal import queries

class CarQueryProcessor:
    def __init__(self, neo4j_url, username, password):
        self.driver = GraphDatabase.driver(neo4j_url, auth=(username, password))
        self.node_categories = [
            "主动安全", "发动机", "变速箱", "四驱_越野", "外后视镜", "外观_防盗", "天窗_玻璃", "屏幕_系统",
            "底盘转向", "座椅配置", "方向盘_内后视镜", "智能化配置", "特色配置", "电动机", "电池_充电", "空调_冰箱", "被动安全",
            "车内充电", "车外灯光", "车身", "车轮制动", "选装包", "音响_车内灯光", "颜色", "驾驶功能", "驾驶操控", "驾驶硬件"
        ]

    def clean_result_keys(self, raw_results):
        def clean_dict(d):
            cleaned = {}
            for key, value in d.items():
                new_key = key.replace('n.', '').replace('s.', '')
                if new_key in {'CAR_ID', '系列ID', 'ID'}:
                    continue
                if isinstance(value, dict):
                    value = clean_dict(value)
                cleaned[new_key] = value
            return cleaned
        return [clean_dict(entry) for entry in raw_results]

    def query_car_info(self, query):
        with self.driver.session() as session:
            result = session.run(query)
            parsed_results = []
            for record in result:
                entry = {}
                for key in record.keys():
                    value = record[key]
                    entry[key] = dict(value.items()) if hasattr(value, 'items') else value
                parsed_results.append(entry)
            return parsed_results

    def is_valid_node(self, node_name):
        return node_name in self.node_categories

    def handle_query(self, car_name, node_name, node_field):
        if self.is_valid_node(node_name):
            query = queries.q_node_parm(car_name, node_name, node_field)
        elif node_name == "基本参数":
            query = queries.q_basic_info(car_name, node_field)
        else:
            return []
        raw_result = self.query_car_info(query)
        return self.clean_result_keys(raw_result)

if __name__ == "__main__":
    processor = CarQueryProcessor(
        neo4j_url="bolt://localhost:7687",
        username="neo4j",
        password="neo4j0000"
    )

    # 示例
    car_name = "奔驰E级 2025款 改款 E 260 L"
    node_name = "颜色"
    node_field = None

    result = processor.handle_query(car_name, node_name, node_field)
    print(result)
#{'车型名称': '迈巴赫S级 2025款 改款 S 480 4MATIC', '品牌系列': '迈巴赫S级', '厂商指导价_元': '146.80万', '厂商': '梅赛德斯-迈巴赫', '级别': '大型车', '能源类型': '汽油+48V轻混系统', '环保标准': '国VI', '上市时间': '2025.03'}