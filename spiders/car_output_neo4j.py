from neo4j import GraphDatabase
import json

# 连接到 Neo4j 数据库
url = "bolt://localhost:7687"  # Neo4j 的连接地址
username = "neo4j"
password = "neo4j0000"  # 填入密码
driver = GraphDatabase.driver(url, auth=(username, password))


# 查询 Neo4j 中的所有节点和关系
def query_graph(driver):
    with driver.session() as session:
        # 运行查询，立即获取所有数据
        result = session.run("MATCH (n)-[r]->(m) RETURN n, r, m")
        return result.data()  # 使用 .data() 获取所有记录


# 将 Node 或 Relationship 对象转为字典
def convert_node_to_dict(node):
    return dict(node.items()) if node is not None else {}

def convert_relationship_to_dict(relationship):
    # 如果是 Relationship 对象，直接转换为字典
    if hasattr(relationship, 'items'):
        return dict(relationship.items()) if relationship is not None else {}
    # 如果是元组类型，处理为一个空字典
    elif isinstance(relationship, tuple):
        return {}  # 可以根据实际需要修改，或者提取元组中的其他信息
    return {}


# 转换查询结果为 JSON 格式
def convert_to_json(result):
    data = []
    for record in result:
        node1 = convert_node_to_dict(record.get("n"))
        relationship = convert_relationship_to_dict(record.get("r"))
        node2 = convert_node_to_dict(record.get("m"))

        data.append({
            "node1": node1,  # 提取节点1的属性
            "relationship": relationship,  # 提取关系的属性
            "node2": node2  # 提取节点2的属性
        })
    return json.dumps(data, indent=4, ensure_ascii=False)


# 执行查询并导出为 JSON
result = query_graph(driver)
json_data = convert_to_json(result)

# 将结果保存到文件
with open("../data/car_graph_data.json", "w",encoding="utf-8") as json_file:
    json_file.write(json_data)
print("neo4j所有关系已导出为json")
# 关闭数据库连接
driver.close()
