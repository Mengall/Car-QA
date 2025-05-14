import requests
import re
import os
import csv


def replace_symbols(text):
    """替换 ● 和 ○ 并去除首尾空格"""
    return text.replace("●", "(标配)").replace("○", "(选配)").replace("\t", "").strip()


def process_string(s):
    """规范化字符串：
    - 替换 ° 为 "度"
    - 替换两个汉字、字母或数字之间的符号为下划线
    - 删除符号两边只有一个汉字、字母或数字的符号
    """
    s = re.sub(r'°', '度', s)
    s = re.sub(r'(?<=[\u4e00-\u9fffA-Za-z0-9])[^\w\u4e00-\u9fff]+(?=[\u4e00-\u9fffA-Za-z0-9])', '_', s)
    s = re.sub(r'(?<=[\u4e00-\u9fffA-Za-z0-9])[^\w\u4e00-\u9fff]|[^\w\u4e00-\u9fff](?=[\u4e00-\u9fffA-Za-z0-9])', '', s)
    return s


def write_to_csv(file_name, headers, data):
    """写入 CSV 文件，如果不存在则创建并写入表头"""
    file_exists = os.path.exists(file_name)

    with open(file_name, mode='a', newline='') as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(headers)  # 写入表头

        writer.writerows(data)  # 写入数据

#品牌：奔驰-36 宝马-15 比亚迪-75 大众-1 奥迪-33 本田-14 奔腾-95 吉利银河-575 红旗-91 丰田-3 别克-38 小米-489 吉利-25
def get_car_data(page,brand_id,output_dir = "car-csv-data"):
    """获取汽车数据并写入 CSV"""
    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36'
    }

    url = f'https://www.autohome.com.cn/_next/data/nextweb-prod-c_1.0.152-p_1.35.1/price/brandid_{brand_id}/x-x-x-x-{page}.json?filter=brandid_{brand_id}&query=x-x-x-x-{page}'
    resp = requests.get(url=url, headers=headers)
    resp.encoding = "utf-8"

    car_data = resp.json()
    car_list = car_data['pageProps']['seriesList']['seriesgrouplist']
    print(car_list)
    print("品牌 ID:", brand_id)

    os.makedirs(output_dir, exist_ok=True)  # 创建存储目录
    for car in car_list:
        series_id = car['seriesid']
        car_id_list = car['specids']

        print("系列 ID:", series_id)
        print("汽车 ID:", car_id_list)

        param_url = f'https://car-web-api.autohome.com.cn/car/param/getParamConf?mode=1&site=1&seriesid={series_id}'
        resp = requests.get(url=param_url, headers=headers)
        resp.encoding = "utf-8"
        car_info = resp.json()

        brand = car_info['result']['bread']['brandname']
        brand_series = car_info['result']['bread']['seriesname']
        title_list = car_info['result']['titlelist']
        data_list = car_info['result']['datalist']

        print("品牌:", brand)
        print("品牌系列:", brand_series)

        # **写入品牌系列 CSV**
        brand_series_data = [[brand_id, series_id,brand, brand_series]]
        brand_tabel = os.path.join(output_dir,"品牌系列.csv")
        write_to_csv(brand_tabel, headers=["ID", "系列ID","品牌", "品牌系列"], data=brand_series_data)

        # **处理参数数据**
        for title in title_list:
            name = title['itemtype'].replace("/", "-")  # 处理文件名
            file_name = f"{output_dir}/{name}.csv"

            # new_headers = [process_string(item["itemname"]) for item in title["items"]]
            new_headers = [item["itemname"] for item in title["items"]]
            new_title_ids = [item['titleid'] for item in title["items"]]

            # **检查 CSV 文件是否存在**
            file_exists = os.path.exists(file_name)
            existing_headers = []

            if file_exists:
                with open(file_name, mode="r", newline="", encoding="utf-8-sig") as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    if rows:
                        existing_headers = rows[0]  # 取第一行作为表头

            # **确保 "ID" 和 "CAR_ID" 在表头最前**
            existing_headers_cleaned = [h for h in existing_headers if h not in ["CAR_ID", "品牌系列"]]
            updated_headers = ["CAR_ID", "品牌系列"] + list(dict.fromkeys(existing_headers_cleaned + new_headers))

            # **如果表头变更，重写 CSV 并补全旧数据**
            if updated_headers != existing_headers:
                with open(file_name, mode="w", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow(updated_headers)  # 写入新的表头
                    print(f"更新表头: {updated_headers}")

                    if file_exists and len(rows) > 1:
                        for row in rows[1:]:  # 跳过表头
                            row_dict = dict(zip(existing_headers, row))  # 旧数据转字典
                            new_row = [row_dict.get(h, "") for h in updated_headers]  #补全数据
                            writer.writerow(new_row)

            # **写入新数据**
            with open(file_name, mode="a", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)

                id_num = 0  # 维持 ID 逻辑
                for car_data in data_list:
                    data_dict = {item['titleid']: item for item in car_data['paramconflist']}  # 构建字典映射

                    try:
                        row_data = {
                            "CAR_ID": car_id_list[id_num],  # 保持 ID
                            "品牌系列": brand_series
                        }

                        for title_id, field_name in zip(new_title_ids, new_headers):
                            if title_id in data_dict:
                                full_name = data_dict[title_id]
                                if full_name.get('itemname'):
                                    item_name = full_name['itemname']
                                elif full_name.get('sublist'):
                                    item_name = ",".join(
                                        k.get('value', '') + k.get('name', '') for k in full_name['sublist'])
                                elif full_name.get('colorinfo') and 'list' in full_name['colorinfo']:
                                    item_name = ",".join(y.get('name', '') for y in full_name['colorinfo']['list'])
                                else:
                                    item_name = "无"

                                # **调试打印**
                                # print(f"字段: {field_name}, 原始值: {item_name}")

                                row_data[field_name] = replace_symbols(item_name.replace("\t", "").strip())
                            else:
                                row_data[field_name] = "无"

                        # **确保数据顺序一致**
                        final_row = [row_data.get(h, "") for h in updated_headers]
                        writer.writerow(final_row)

                        id_num += 1  # 递增 ID

                    except IndexError:
                        print(f"错误：id_num ({id_num}) 超出 car_id 长度 ({len(car_id_list)})，停止递增")

            print(f"数据已追加: {file_name}")
            print("=" * 25)

    print("=" * 25)


if __name__ == "__main__":
    #[id,page] 宝马-15 比亚迪-75 大众-1 奥迪-33 本田-14 保时捷-40 特斯拉-133 红旗-91 丰田-3 别克-38 小米-489 吉利-25
    datas = {"奔驰": [36,6], "宝马": [15,5], "比亚迪": [75,4], "大众": [1,4], "奥迪": [33,4], "本田": [14,3], "保时捷": [40,2],
             "特斯拉": [133,2], "红旗": [91,3], "丰田": [3,4], "别克": [38,2], "小米": [489,2], "吉利": [25,3]}
    for key,data in datas.items():
        print(key)
        for page in range(1,data[1]):
            get_car_data(page,data[0])
            # print(page,data[0])