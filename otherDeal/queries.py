# 模板设计
# 查询基本参数下的节点的一个或多个字段
def q_node_parm(text_list, node_param, fields=None):
    # 如果传入的 text_list 是单一字符串，转换为列表
    if isinstance(text_list, str):
        text_list = [text_list]
    # 如果传入的 fields 是单一字符串，转换为列表
    if isinstance(fields, str):
        fields = [fields]
    # 使用 IN 来支持多个车型名称
    text_str = ', '.join([f"'{item}'" for item in text_list])
    # 传入字段如果不为空，返回指定字段
    if fields:
        field_str = ', '.join([f"s.{field}" for field in fields])
        return f"""MATCH (n:`基本参数`)-[:包含]->(s:{node_param})
                               WHERE n.车型名称 IN [{text_str}]
                               RETURN n.车型名称 as 车型名称, {field_str}"""
    # 传入字段如果为空，返回所有字段
    return f"""MATCH (n:`基本参数`)-[:包含]->(s:{node_param})
                               WHERE n.车型名称 IN [{text_str}]
                               RETURN n.车型名称 as 车型名称, s"""

# 一个或多个基本信息
def q_basic_info(text_list, fields=None):
    # 如果传入的 text_list 是单一字符串，转换为列表
    if isinstance(text_list, str):
        text_list = [text_list]
    # 如果传入的 fields 是单一字符串，转换为列表
    if isinstance(fields, str):
        fields = [fields]
    # 使用 IN 来支持多个车型名称
    text_str = ', '.join([f"'{item}'" for item in text_list])
    # 如果非None
    if fields:
        field_str = ', '.join([f"n.{field}" for field in fields])
        return f"""MATCH (n:`基本参数`) WHERE n.车型名称 IN [{text_str}] RETURN n.车型名称 as 车型名称, {field_str}"""
    return f"""MATCH (n:`基本参数`) WHERE n.车型名称 IN {text_list} RETURN n"""

# 品牌->系列 系列->车型 系列->品牌 车型->系列 车型->品牌
# 品牌和品牌系列
# 奔驰有哪些系列？
def q_brand_series(text):
    return f"""MATCH (b:品牌 {{品牌: '{text}'}})-[:包含]->(n:品牌系列) RETURN n.品牌系列 as 品牌系列"""


# 某系列属于哪个品牌 奔驰E级属于哪个品牌？
def q_series_brand(text):
    return f"""MATCH (n:品牌)-[:包含]->(s:品牌系列 {{品牌系列: '{text}'}})RETURN n.品牌 as 品牌"""


# 某系列有哪些车型？
def q_series_car(text):
    return f"""MATCH (n:基本参数 {{品牌系列: '{text}'}}) RETURN n.车型名称 as 车型名称"""


# 车型的系列
def q_car_series(text):
    return f"""MATCH (n:品牌系列)-[:包含]->(s:基本参数 {{车型名称: '{text}'}}) RETURN n.品牌系列 as 品牌系列"""


# 车型的品牌
def q_car_brand(text):
    return f"""MATCH (n:品牌)-[:包含]->(b:品牌系列)-[:包含]->(s:基本参数 {{车型名称: '{text}'}})RETURN n.品牌 as 品牌"""

