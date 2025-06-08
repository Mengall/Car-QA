import json
import os


def load_json_file(file_path, encoding='utf-8'):
    if not os.path.exists(file_path):
        print(f"[错误] 文件不存在: {file_path}")
        return None

    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"[错误] JSON 解码失败: {e}")
    except Exception as e:
        print(f"[错误] 读取 JSON 文件时发生异常: {e}")

    return None


def get_series():
    series_list = []
    datas = load_json_file("../data/body_field_map.json", encoding="utf-8")
    for values in datas.values():
        for series in values.keys():
            series_list.append(series)
    return series_list


def is_car_in_body(data, body_data):
    """
    检查所有车辆是否在 body_data 的值中
    """
    all_car_names = set()
    for brand, field_list in body_data.items():
        all_car_names.add(brand)
        for series, car_list in field_list.items():
            # print(series)
            all_car_names.add(series)
            all_car_names.update(car_list)

    for car in data:
        car_name = car[0]
        if car_name not in all_car_names:
            print(f"[错误] 车型 '{car_name}' 不存在于 body_data 中")
            return False

    return True


def are_fields_valid(data, object_data):
    """
    检查所有字段是否存在于 object_data 中对应节点
    """
    for car in data:
        for field_info in car[1:]:
            node = field_info.get("节点")
            field = field_info.get("字段")

            if field in ["null", None]:  # 跳过无效字段
                continue

            if node not in object_data:
                print(f"[错误] 节点 '{node}' 不存在于 object_data 中")
                return False

            if field not in object_data[node]:
                print(f"[错误] 字段 '{field}' 不存在于 object_data['{node}'] 中")
                return False
    return True


def merge_same_node_fields(data):
    result = []
    for car in data:
        car_name = car[0]
        merged_fields = {}
        null_fields = []

        for field_info in car[1:]:
            node = field_info.get("节点")
            field = field_info.get("字段")

            if field is None:
                null_fields.append(field_info)
                continue

            if node not in merged_fields:
                merged_fields[node] = []
            merged_fields[node].append(field)

        new_car = [car_name]
        for node, fields in merged_fields.items():
            if len(fields) == 1:
                new_car.append({"节点": node, "字段": fields[0]})
            else:
                new_car.append({"节点": node, "字段": fields})

        new_car.extend(null_fields)
        result.append(new_car)

    return result


def process_data_if_valid(data, body_data, object_data):
    print("[原始数据]")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    print("\n[验证是否在 body_data 中]")
    print(is_car_in_body(data, body_data))
    print("\n[验证字段是否在 object_data 中]")
    print(are_fields_valid(data, object_data))

    if is_car_in_body(data, body_data) and are_fields_valid(data, object_data):
        merged_data = merge_same_node_fields(data)
        # print("\n[合并后的数据]")
        # for car in merged_data:
        #     print(json.dumps(car, ensure_ascii=False, indent=2))
        return merged_data
    else:
        print("\n[数据无效，未处理]")
        return None


# # 示例数据
# a = [['保时捷911 2025款 Carrera 3.0T', {'节点': '基本参数', '字段': '长_宽_高_mm'}, {'节点': '基本参数', '字段': '上市时间'},
#        {'节点': '发动机', '字段': None}]]
# data = [
#     ['保时捷911 2025款 Carrera 3.0T', {'节点': '颜色', '字段': '内饰颜色'}, {'节点': '发动机', '字段': 'null'},
#      {'节点': '颜色', '字段': '外观颜色'}],
#     ['Panamera新能源 2023款 Panamera 4S E-Hybrid Sport Turismo 2.9T',
#      {'节点': '颜色', '字段': '内饰颜色'}, {'节点': '座椅配置', '字段': 'null'},
#      {'节点': '基本参数', '字段': '长_宽_高_mm'}]
# ]
# a1 = [['奔驰E级', {'节点': '品牌'}], ['奔驰', {'节点': '品牌系列'}]]
#
#
# # 载入外部 JSON 数据
# o = load_json_file("../data/object_field_map.json")
# b = load_json_file("../data/body_field_map.json")
#
# # 处理数据
# process_data_if_valid(a1, b, o)