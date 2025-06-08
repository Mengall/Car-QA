from neo4j import GraphDatabase
from otherDeal import queries
from Rule_match import get_series
class CarQueryProcessor:
    def __init__(self, neo4j_url, username, password):
        self.driver = GraphDatabase.driver(neo4j_url, auth=(username, password))
        self.node_categories = [
            "主动安全", "发动机", "变速箱", "四驱_越野", "外后视镜", "外观_防盗", "天窗_玻璃", "屏幕_系统",
            "底盘转向", "座椅配置", "方向盘_内后视镜", "智能化配置", "特色配置", "电动机", "电池_充电", "空调_冰箱", "被动安全",
            "车内充电", "车外灯光", "车身", "车轮制动", "选装包", "音响_车内灯光", "颜色", "驾驶功能", "驾驶操控", "驾驶硬件"
        ]
        self.car_brand = ["奔驰", "宝马", "比亚迪", "大众", "奥迪", "本田", "保时捷", "特斯拉", "红旗", "丰田", "别克", "小米汽车", "吉利汽车"]
        self.car_series = get_series()

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
        if node_field == "车型名称":
            query = queries.q_series_car(car_name)
        elif self.is_valid_node(node_name):
            query = queries.q_node_parm(car_name, node_name, node_field)
        elif node_name == "基本参数":
            query = queries.q_basic_info(car_name, node_field)
        elif node_name == "品牌系列":
            query = queries.q_brand_series(car_name)
            result = self.query_car_info(query)  # 查询函数，返回结果或 None
            if not result:  # 如果第一个查询没查到，再用车型名称查品牌系列
                query = queries.q_car_series(car_name)
                result = self.query_car_info(query)
            return result
        elif node_name == "品牌":
            # 先尝试根据 品牌系列 查询品牌
            query = queries.q_series_brand(car_name)
            result = self.query_car_info(query)  # 查询函数，返回结果或 None
            if not result:  # 如果第一个查询没查到，再用车型名称查品牌
                query = queries.q_car_brand(car_name)
                result = self.query_car_info(query)
            return result
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
    node_name = "品牌"
    node_field = None

    result = processor.handle_query(car_name, node_name, node_field)
    print(result)
#基本参数
# [{'n': {'车身结构': '4门5座三厢车', '首任车主质保政策': '无', '最低荷电状态油耗_L_100kmWLTC': '无', '官方100_0km_h制动_m': '无', '变速箱': '无', '实测油耗_L_100km': '无', '实测快充时间_小时': '无', '厂商': '小米汽车', '长_宽_高_mm': '4997*1963*1455', '实测电池快充电量范围__': '无', '官方0_50km_h加速_s': '无', '上市时间': '2024.03', '电池慢充时间_小时': '无', '最大扭矩_N_m': '400', 'NEDC纯电续航里程_km': '无', '准拖挂车总质量_kg': '无', '实测最低荷电状态油耗_L_100km': '无', '最低荷电状态油耗_L_100kmNEDC': '无', '实测0_100km_h加速_s': '无', '最大功率_kW': '220', '最高车速_km_h': '210', '实测续航里程_km': '无', '油电综合燃料消耗量_L_100km': '无', '整备质量_kg': '1980', '环保标准': '无', '品牌系列': '小米SU7', '发动机': '无', 'WLTC纯电续航里程_km': '无', '电池快充时间_小时': '0.42', '车型名称': '小米SU7 2024款 700km 后驱长续航智驾版', '级别': '中大型车', '实测平均电耗_kWh_100km': '无', '整车质保': '(标配)五年或10万公里', '实测100_0km_h制动_m': '无', '最大满载质量_kg': '2430', 'CLTC纯电续航里程_km': '700', '厂商指导价_元': '21.59万', '最低荷电状态油耗_L_100km': '无', '能源类型': '纯电动', '电能当量燃料消耗量_L_100km': '1.39', 'WLTC综合油耗_L_100km': '无', '电池慢充电量范围__': '无', '电池快充电量范围__': '10-80', 'NEDC综合油耗_L_100km': '无', '官方0_100km_h加速_s': '5.28', '电动机_Ps': '299', '最低荷电状态油耗_L_100kmCLTC': '无'}}]
# [{'车型名称': '小米SU7 2024款 700km 后驱长续航智驾版', '厂商指导价_元': '21.59万', '厂商': '小米汽车', '级别': '中大型车', '能源类型': '纯电动'}]
#其他配置
# [{'车型名称': '小米SU7 2024款 700km 后驱长续航智驾版', 's': {'内饰颜色': '曜石黑,银河灰,暮光红,迷雾紫,米灰色', '品牌系列': '小米SU7', '外观颜色': '海湾蓝,橄榄绿,雅灰,霞光紫,熔岩橙,寒武岩灰,流星蓝,珍珠白,钻石黑,璀璨洋红'}}]
# [{'车型名称': '小米SU7 2024款 700km 后驱长续航智驾版', '内饰颜色': '曜石黑,银河灰,暮光红,迷雾紫,米灰色'}]
#品牌系列
# [{'品牌系列': '小米SU7'}, {'品牌系列': '小米SU7 Ultra'}]
#品牌
# [{'品牌': '小米汽车'}]
#所有车型
# [{'车型名称': '小米SU7 2024款 700km 后驱长续航智驾版'}, {'车型名称': '小米SU7 2024款 830km 后驱超长续航高阶智驾Pro版'}, {'车型名称': '小米SU7 2024款 800km 四驱超长续航高阶智驾Max版'}]
