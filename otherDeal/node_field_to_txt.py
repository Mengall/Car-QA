import json
import jieba

# 读取JSON文件并将其写入TXT文件，同时替换空格为下划线
def read_json_and_write_to_txt(json_file_path, txt_file_path):
    with open(json_file_path, 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # 打开TXT文件并写入内容
    with open(txt_file_path, 'a', encoding='utf-8') as txt_file:
       for k, v in data.items():
            for category, fields in v.items():
                # 替换空格为下划线并写入
                # category = category
                txt_file.write(f"{category.replace(':','')} 100 series\n")
                for field in fields:
                    # 替换空格为下划线并写入
                    field = field
                    txt_file.write(f"{field}\n")
                txt_file.write("\n")
    print("写入成功.")

# 输入文件路径
json_file_path = "../data/body_field_map.json"
txt_file_path = "../data/jieba_node_field.txt"

# 调用函数
read_json_and_write_to_txt(json_file_path, txt_file_path)


