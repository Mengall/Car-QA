import pandas as pd
def is_valid_value(value):
    """检查字段值是否有效（即非空且不是'无'）"""
    return pd.notna(value) and str(value).strip() != "无"

#发动机
def format_vehicle_description(row, selected_columns=None):
    if 'CAR_ID' in row.index:
        row = row.drop(labels='CAR_ID')

    if selected_columns is not None:
        row = row[selected_columns]

    input_parts = []
    for col in row.index:
        if is_valid_value(row[col]):
            input_parts.append(f"{col}：{row[col]}")
    input_text = ",".join(input_parts)

    desc = []

    # 品牌与发动机型号
    if is_valid_value(row.get("车型名称")):
        desc.append(f"这款 {row['车型名称']}")
    if is_valid_value(row.get("品牌系列")):
        desc.append(f" 属于{row['品牌系列']}系列，")

    if is_valid_value(row.get("发动机型号")):
        desc.append(f"搭载型号为{row['发动机型号']}的发动机。")

    # 排量与进气形式
    if is_valid_value(row.get("排量_L")):
        desc.append(f"排量为{row['排量_L']}L，")
    if is_valid_value(row.get("进气形式")):
        desc.append(f"采用{row['进气形式']}；")

    # 发动机结构
    if is_valid_value(row.get("发动机布局")):
        desc.append(f"发动机布局为{row['发动机布局']}，")
    if is_valid_value(row.get("气缸排列形式")):
        desc.append(f"气缸排列形式为{row['气缸排列形式']}，")
    if is_valid_value(row.get("气缸数_个")):
        desc.append(f"共{row['气缸数_个']}个气缸，")
    if is_valid_value(row.get("每缸气门数_个")):
        desc.append(f"每缸{row['每缸气门数_个']}气门，")
    if is_valid_value(row.get("缸径_mm")):
        desc.append(f"缸径为{row['缸径_mm']}毫米，")
    if is_valid_value(row.get("配气机构")):
        desc.append(f"采用{row['配气机构']}配气机构，")
    if is_valid_value(row.get("行程_mm")):
        desc.append(f"行程{row['行程_mm']}毫米；")

    # 动力参数
    if is_valid_value(row.get("最大马力_Ps")):
        desc.append(f"最大马力为{row['最大马力_Ps']}Ps，")
    if is_valid_value(row.get("最大功率_kW")):
        desc.append(f"最大功率为{row['最大功率_kW']}kW，")
    if is_valid_value(row.get("最大净功率_kW")):
        desc.append(f"最大净功率为{row['最大净功率_kW']}kW，")
    if is_valid_value(row.get("最大扭矩_N_m")):
        desc.append(f"峰值扭矩为{row['最大扭矩_N_m']}N·m，")
    if is_valid_value(row.get("最大功率转速_rpm")):
        desc.append(f"最大功率转速为{row['最大功率转速_rpm']}rpm，")
    if is_valid_value(row.get("最大扭矩转速_rpm")):
        desc.append(f"最大扭矩转速范围为{row['最大扭矩转速_rpm']}rpm。")

    # 能源与供油
    if is_valid_value(row.get("能源类型")):
        desc.append(f"能源类型为{row['能源类型']}，")
    if is_valid_value(row.get("燃油标号")):
        desc.append(f"推荐使用{row['燃油标号']}汽油，")
    if is_valid_value(row.get("最低燃油标号")):
        desc.append(f"最低燃油标号为{row['最低燃油标号']}汽油，")
    if is_valid_value(row.get("供油方式")):
        desc.append(f"供油方式为{row['供油方式']}；")

    # 材料与环保
    if is_valid_value(row.get("缸盖材料")):
        desc.append(f"缸盖材料为{row['缸盖材料']}，")
    if is_valid_value(row.get("缸体材料")):
        desc.append(f"缸体材料为{row['缸体材料']}，")
    if is_valid_value(row.get("环保标准")):
        desc.append(f"符合{row['环保标准']}排放标准；")

    # 其他信息
    if is_valid_value(row.get("压缩比")):
        desc.append(f"压缩比为{row['压缩比']}，")
    if is_valid_value(row.get("发动机特有技术")):
        desc.append(f"搭载了{row['发动机特有技术']}技术。")

    output_text = "".join(desc).rstrip("，；。") + "。"

    return {
        "instruction": "请根据以下车辆信息生成简洁的自然语言描述。",
        "input": input_text,
        "output": output_text
    }
#主动安全
def format_vehicle_description(row, selected_columns=None):
    if 'CAR_ID' in row.index:
        row = row.drop(labels='CAR_ID')

    if selected_columns is not None:
        row = row[selected_columns]

    input_parts = []
    for col in row.index:
        if is_valid_value(row[col]):
            input_parts.append(f"{col}：{row[col]}")
    input_text = ",".join(input_parts)

    desc = []

    # 品牌与发动机型号
    if is_valid_value(row.get("车型名称")):
        desc.append(f"{row['车型名称']}")
    if is_valid_value(row.get("品牌系列")):
        desc.append(f" 属于{row['品牌系列']}系列，标配了多项主动安全配置，保障日常驾驶的稳定与安全。")

    if is_valid_value(row.get("ABS防抱死")):
        desc.append("包含：ABS防抱死系统")
    if is_valid_value(row.get("制动力分配_EBD_CBC等")):
        desc.append("、EBD/CBC制动力分配系统")
    if is_valid_value(row.get("刹车辅助_EBA_BAS_BA等")):
        desc.append("、EBA/BAS/BA刹车辅助系统")
    if is_valid_value(row.get("牵引力控制_ASR_TCS_TRC等")):
        desc.append("、ASR/TCS/TRC牵引力控制系统")
    if is_valid_value(row.get("车身稳定控制_ESC_ESP_DSC等")):
        desc.append("、ESC/ESP/DSC车身稳定控制系统")

    if is_valid_value(row.get("胎压监测功能")):
        desc.append("，具备胎压监测功能")
    if is_valid_value(row.get("安全带未系提醒")):
        desc.append("，全车安全带未系提醒")
    if is_valid_value(row.get("ISOFIX儿童座椅接口")):
        desc.append("，ISOFIX儿童座椅接口")
    if is_valid_value(row.get("车道偏离预警系统")):
        desc.append("，车道偏离预警系统")
    if is_valid_value(row.get("主动刹车_主动安全系统")):
        desc.append("，主动刹车系统")
    if is_valid_value(row.get("疲劳驾驶提示")):
        desc.append("，疲劳驾驶提示")
    if is_valid_value(row.get("前方碰撞预警")):
        desc.append("，前方碰撞预警")
    if is_valid_value(row.get("内置行车记录仪")):
        desc.append("，内置行车记录仪")
    if is_valid_value(row.get("道路救援呼叫")):
        desc.append("，道路救援呼叫")

    if is_valid_value(row.get("DOW开门预警")):
        desc.append("，DOW开门预警")
    if is_valid_value(row.get("后方碰撞预警")):
        desc.append("，后方碰撞预警")
    if is_valid_value(row.get("低速行车警告")):
        desc.append("，低速行车警告")
    if is_valid_value(row.get("哨兵模式_千里眼")):
        desc.append("，哨兵模式/千里眼")
    if is_valid_value(row.get("防侧翻系统")):
        desc.append("，防侧翻系统")
    if is_valid_value(row.get("移动物体预警系统")):
        desc.append("，移动物体预警系统")

    output_text = "".join(desc).rstrip("，。") + "。"

    return {
        "instruction": "请根据以下车辆信息生成简洁的自然语言描述。",
        "input": input_text,
        "output": output_text
    }
#被动安全
def format_vehicle_description(row, selected_columns=None):
    if 'CAR_ID' in row.index:
        row = row.drop(labels='CAR_ID')

    if selected_columns is not None:
        row = row[selected_columns]

    input_parts = []
    for col in row.index:
        if is_valid_value(row[col]):
            input_parts.append(f"{col}：{row[col]}")
    input_text = ",".join(input_parts)

    desc = []

    if is_valid_value(row.get("品牌系列")):
        desc.append(f"该车属于{row['品牌系列']}系列")
    if is_valid_value(row.get("车型名称")):
        desc.append(f"，这款 {row['车型名称']} 在安全气囊配置上较为完善。")
    if is_valid_value(row.get("主_副驾驶座安全气囊")):
        desc.append(f"配备了主/副驾驶座安全气囊（{row['主_副驾驶座安全气囊']}）")
    if is_valid_value(row.get("前_后排侧气囊")):
        desc.append(f"，前/后排侧气囊为（{row['前_后排侧气囊']}）")
    if is_valid_value(row.get("前_后排头部气囊_气帘")):
        desc.append(f"，前/后排头部气囊（气帘）配置为（{row['前_后排头部气囊_气帘']}）")
    if is_valid_value(row.get("膝部气囊")):
        desc.append(f"，膝部气囊配置为（{row['膝部气囊']}）")
    if is_valid_value(row.get("前排中间气囊")):
        desc.append(f"，前排中间气囊：{row['前排中间气囊']}")
    if is_valid_value(row.get("被动行人保护")):
        desc.append(f"，具备被动行人保护功能（{row['被动行人保护']}）")
    if is_valid_value(row.get("后排正向安全气囊")):
        desc.append(f"，后排正向安全气囊：{row['后排正向安全气囊']}")
    if is_valid_value(row.get("缺气保用轮胎")):
        desc.append(f"，配备缺气保用轮胎：{row['缺气保用轮胎']}")
    if is_valid_value(row.get("后排中央安全气囊")):
        desc.append(f"，后排中央安全气囊：{row['后排中央安全气囊']}")
    if is_valid_value(row.get("副驾驶座垫式气囊")):
        desc.append(f"，副驾驶座垫式气囊：{row['副驾驶座垫式气囊']}")

    output_text = "".join(desc).rstrip("，。") + "。"

    return {
        "instruction": "请根据以下车辆信息生成简洁的自然语言描述。",
        "input": input_text,
        "output": output_text
    }
#车身
def format_vehicle_description(row, selected_columns=None):
    if 'CAR_ID' in row.index:
        row = row.drop(labels='CAR_ID')

    if selected_columns is not None:
        row = row[selected_columns]

    input_parts = []
    for col in row.index:
        if is_valid_value(row[col]):
            input_parts.append(f"{col}：{row[col]}")
    input_text = ",".join(input_parts)

    desc = []

    if is_valid_value(row.get("车型名称")):
        desc.append(f"{row['车型名称']} ")
    if is_valid_value(row.get("品牌系列")):
        desc.append(f"属于{row['品牌系列']}系列。")

    if is_valid_value(row.get("长度_mm")):
        desc.append(f"车长为{row['长度_mm']}毫米")
    if is_valid_value(row.get("宽度_mm")):
        desc.append(f"，车宽为{row['宽度_mm']}毫米")
    if is_valid_value(row.get("高度_mm")):
        desc.append(f"，车高为{row['高度_mm']}毫米")
    if is_valid_value(row.get("轴距_mm")):
        desc.append(f"，轴距为{row['轴距_mm']}毫米")
    if is_valid_value(row.get("前轮距_mm")):
        desc.append(f"，前轮距为{row['前轮距_mm']}毫米")
    if is_valid_value(row.get("后轮距_mm")):
        desc.append(f"，后轮距为{row['后轮距_mm']}毫米")
    if is_valid_value(row.get("接近角__")):
        desc.append(f"，接近角为{row['接近角__']}度")
    if is_valid_value(row.get("离去角__")):
        desc.append(f"，离去角为{row['离去角__']}度")
    if is_valid_value(row.get("车身结构")):
        desc.append(f"，车身结构为{row['车身结构']}")
    if is_valid_value(row.get("车门开启方式")):
        desc.append(f"，车门开启方式为{row['车门开启方式']}")
    if is_valid_value(row.get("车门数_个")):
        desc.append(f"，共{row['车门数_个']}个车门")
    if is_valid_value(row.get("座位数_个")):
        desc.append(f"，提供{row['座位数_个']}个座位")
    if is_valid_value(row.get("油箱容积_L")):
        desc.append(f"，油箱容积为{row['油箱容积_L']}升")
    if is_valid_value(row.get("后备厢容积_L")):
        desc.append(f"，后备厢容积为{row['后备厢容积_L']}升")
    if is_valid_value(row.get("风阻系数_Cd")):
        desc.append(f"，风阻系数为{row['风阻系数_Cd']}")
    if is_valid_value(row.get("最小离地间隙_mm")):
        desc.append(f"，最小离地间隙为{row['最小离地间隙_mm']}毫米")
    if is_valid_value(row.get("最大涉水深度_mm")):
        desc.append(f"，最大涉水深度为{row['最大涉水深度_mm']}毫米")
    if is_valid_value(row.get("最小转弯半径_m")):
        desc.append(f"，最小转弯半径为{row['最小转弯半径_m']}米")
    if is_valid_value(row.get("满载最小离地间隙_mm")):
        desc.append(f"，满载时最小离地间隙为{row['满载最小离地间隙_mm']}毫米")
    if is_valid_value(row.get("纵向通过角__")):
        desc.append(f"，纵向通过角为{row['纵向通过角__']}度")
    if is_valid_value(row.get("最大爬坡度__")):
        desc.append(f"，最大爬坡度为{row['最大爬坡度__']}度")
    if is_valid_value(row.get("最大载重质量_kg")):
        desc.append(f"，最大载重质量为{row['最大载重质量_kg']}公斤")
    if is_valid_value(row.get("后排车门开启方式")):
        desc.append(f"，后排车门开启方式为{row['后排车门开启方式']}")
    if is_valid_value(row.get("前备厢容积_L")):
        desc.append(f"，前备厢容积为{row['前备厢容积_L']}升")
    if is_valid_value(row.get("最大爬坡角度__")):
        desc.append(f"，最大爬坡角度为{row['最大爬坡角度__']}度")
    if is_valid_value(row.get("空载最小离地间隙_mm")):
        desc.append(f"，空载时最小离地间隙为{row['空载最小离地间隙_mm']}毫米")
    if is_valid_value(row.get("氢瓶容积_L")):
        desc.append(f"，氢瓶容积为{row['氢瓶容积_L']}升")

    output_text = "".join(desc).rstrip("，。") + "。"

    return {
        "instruction": "请根据以下车辆信息生成简洁的自然语言描述。",
        "input": input_text,
        "output": output_text
    }
#颜色

#天窗
def format_vehicle_description(row, selected_columns=None):
    if 'CAR_ID' in row.index:
        row = row.drop(labels='CAR_ID')

    if selected_columns is not None:
        row = row[selected_columns]

    input_parts = []
    for col in row.index:
        if is_valid_value(row[col]):
            input_parts.append(f"{col}：{row[col]}")
    input_text = ",".join(input_parts)

    desc = []

    if is_valid_value(row.get("品牌系列")):
        desc.append(f"该车属于{row['品牌系列']}系列")
    if is_valid_value(row.get("车型名称")):
        desc.append(f"，这款 {row['车型名称']}")

    if is_valid_value(row.get("天窗类型")):
        desc.append(f"，配备了{row['天窗类型']}天窗")
    if is_valid_value(row.get("前_后电动车窗")):
        desc.append(f"，前后电动车窗配置为{row['前_后电动车窗']}")
    if is_valid_value(row.get("车窗一键升降功能")):
        desc.append(f"，配备了车窗一键升降功能：{row['车窗一键升降功能']}")
    if is_valid_value(row.get("车窗防夹手功能")):
        desc.append(f"，配有车窗防夹手功能：{row['车窗防夹手功能']}")
    if is_valid_value(row.get("侧窗多层隔音玻璃")):
        desc.append(f"，侧窗配备了{row['侧窗多层隔音玻璃']}")
    if is_valid_value(row.get("后风挡遮阳帘")):
        desc.append(f"，配备了{row['后风挡遮阳帘']}后风挡遮阳帘")
    if is_valid_value(row.get("后排侧窗遮阳帘")):
        desc.append(f"，配有{row['后排侧窗遮阳帘']}后排侧窗遮阳帘")
    if is_valid_value(row.get("车内化妆镜")):
        desc.append(f"，车内化妆镜配置：{row['车内化妆镜']}")
    if is_valid_value(row.get("后雨刷")):
        desc.append(f"，配备了{row['后雨刷']}后雨刷")
    if is_valid_value(row.get("感应雨刷功能")):
        desc.append(f"，配有感应雨刷功能：{row['感应雨刷功能']}")
    if is_valid_value(row.get("后排侧隐私玻璃")):
        desc.append(f"，配有{row['后排侧隐私玻璃']}后排侧隐私玻璃")
    if is_valid_value(row.get("可加热喷水嘴")):
        desc.append(f"，配备了可加热喷水嘴：{row['可加热喷水嘴']}")
    if is_valid_value(row.get("星空天窗")):
        desc.append(f"，配有{row['星空天窗']}星空天窗")
    if is_valid_value(row.get("光感天幕")):
        desc.append(f"，配有{row['光感天幕']}光感天幕")

    output_text = "".join(desc).rstrip("，。") + "。"

    return {
        "instruction": "请根据以下车辆信息生成简洁的自然语言描述。",
        "input": input_text,
        "output": output_text
    }
#屏幕
def format_vehicle_description(row, selected_columns=None):
    if 'CAR_ID' in row.index:
        row = row.drop(labels='CAR_ID')

    if selected_columns is not None:
        row = row[selected_columns]

    input_parts = []
    for col in row.index:
        if is_valid_value(row[col]):
            input_parts.append(f"{col}：{row[col]}")
    input_text = ",".join(input_parts)

    desc = []

    if is_valid_value(row.get("品牌系列")):
        desc.append(f"该车属于{row['品牌系列']}系列")
    if is_valid_value(row.get("车型名称")):
        desc.append(f"，这款 {row['车型名称']}")

    if is_valid_value(row.get("中控彩色屏幕")):
        desc.append(f"，配备了{row['中控彩色屏幕']}中控彩色屏幕")
    if is_valid_value(row.get("中控屏幕尺寸")):
        desc.append(f"，中控屏幕尺寸为{row['中控屏幕尺寸']}")
    if is_valid_value(row.get("副驾娱乐屏尺寸")):
        desc.append(f"，副驾娱乐屏尺寸为{row['副驾娱乐屏尺寸']}")
    if is_valid_value(row.get("蓝牙_车载电话")):
        desc.append(f"，支持蓝牙车载电话功能：{row['蓝牙_车载电话']}")
    if is_valid_value(row.get("手机互联_映射")):
        desc.append(f"，支持手机互联映射功能：{row['手机互联_映射']}")
    if is_valid_value(row.get("语音识别控制系统")):
        desc.append(f"，配备了{row['语音识别控制系统']}语音识别控制系统")
    if is_valid_value(row.get("语音助手唤醒词")):
        desc.append(f"，语音助手唤醒词为：{row['语音助手唤醒词']}")
    if is_valid_value(row.get("语音免唤醒词")):
        desc.append(f"，支持语音免唤醒词功能：{row['语音免唤醒词']}")
    if is_valid_value(row.get("语音分区域唤醒识别")):
        desc.append(f"，支持语音分区域唤醒识别：{row['语音分区域唤醒识别']}")
    if is_valid_value(row.get("语音连续识别")):
        desc.append(f"，支持语音连续识别功能：{row['语音连续识别']}")
    if is_valid_value(row.get("可见即可说")):
        desc.append(f"，配备可见即可说功能：{row['可见即可说']}")
    if is_valid_value(row.get("手势控制")):
        desc.append(f"，支持手势控制功能：{row['手势控制']}")
    if is_valid_value(row.get("应用商店")):
        desc.append(f"，车载系统配备了{row['应用商店']}应用商店")
    if is_valid_value(row.get("车载智能系统")):
        desc.append(f"，配备了{row['车载智能系统']}车载智能系统")
    if is_valid_value(row.get("车机智能芯片")):
        desc.append(f"，搭载{row['车机智能芯片']}车机智能芯片")
    if is_valid_value(row.get("后排控制多媒体")):
        desc.append(f"，后排可以控制多媒体系统：{row['后排控制多媒体']}")
    if is_valid_value(row.get("中控屏幕类型")):
        desc.append(f"，中控屏幕类型为：{row['中控屏幕类型']}")
    if is_valid_value(row.get("中控屏幕分辨率")):
        desc.append(f"，中控屏幕分辨率为：{row['中控屏幕分辨率']}")
    if is_valid_value(row.get("中控屏幕像素密度")):
        desc.append(f"，中控屏幕像素密度为：{row['中控屏幕像素密度']}")
    if is_valid_value(row.get("面部识别")):
        desc.append(f"，配备面部识别功能：{row['面部识别']}")
    if is_valid_value(row.get("后排液晶屏幕")):
        desc.append(f"，配备后排液晶屏幕：{row['后排液晶屏幕']}")
    if is_valid_value(row.get("触屏振动反馈")):
        desc.append(f"，支持触屏振动反馈：{row['触屏振动反馈']}")
    if is_valid_value(row.get("多指飞屏操控")):
        desc.append(f"，支持多指飞屏操控：{row['多指飞屏操控']}")
    if is_valid_value(row.get("后排液晶屏幕尺寸")):
        desc.append(f"，后排液晶屏幕尺寸为：{row['后排液晶屏幕尺寸']}")
    if is_valid_value(row.get("后排多媒体屏幕数量")):
        desc.append(f"，后排多媒体屏幕数量为：{row['后排多媒体屏幕数量']}")
    if is_valid_value(row.get("副驾屏幕类型")):
        desc.append(f"，副驾屏幕类型为：{row['副驾屏幕类型']}")
    if is_valid_value(row.get("副驾屏幕像素密度")):
        desc.append(f"，副驾屏幕像素密度为：{row['副驾屏幕像素密度']}")
    if is_valid_value(row.get("车机系统内存_GB")):
        desc.append(f"，车机系统内存为：{row['车机系统内存_GB']} GB")
    if is_valid_value(row.get("车机系统存储_GB")):
        desc.append(f"，车机系统存储为：{row['车机系统存储_GB']} GB")
    if is_valid_value(row.get("可翻转中控屏幕")):
        desc.append(f"，配备可翻转中控屏幕：{row['可翻转中控屏幕']}")
    if is_valid_value(row.get("车载电视")):
        desc.append(f"，配备车载电视：{row['车载电视']}")
    if is_valid_value(row.get("旋转大屏")):
        desc.append(f"，配备旋转大屏：{row['旋转大屏']}")
    if is_valid_value(row.get("中控液晶屏分屏显示")):
        desc.append(f"，支持中控液晶屏分屏显示：{row['中控液晶屏分屏显示']}")
    if is_valid_value(row.get("DeepSeek应用")):
        desc.append(f"，配备DeepSeek应用：{row['DeepSeek应用']}")
    if is_valid_value(row.get("中控下屏幕尺寸")):
        desc.append(f"，中控下屏幕尺寸为：{row['中控下屏幕尺寸']}")
    if is_valid_value(row.get("车载CD_DVD")):
        desc.append(f"，配备车载CD/DVD：{row['车载CD_DVD']}")
    if is_valid_value(row.get("后排液晶屏幕分辨率")):
        desc.append(f"，后排液晶屏幕分辨率为：{row['后排液晶屏幕分辨率']}")
    if is_valid_value(row.get("声纹识别")):
        desc.append(f"，配备声纹识别功能：{row['声纹识别']}")
    if is_valid_value(row.get("后排液晶屏幕类型")):
        desc.append(f"，后排液晶屏幕类型为：{row['后排液晶屏幕类型']}")
    if is_valid_value(row.get("副驾屏幕分辨率")):
        desc.append(f"，副驾屏幕分辨率为：{row['副驾屏幕分辨率']}")

    output_text = "".join(desc).rstrip("，。") + "。"

    return {
        "instruction": "请根据以下车辆信息生成简洁的自然语言描述。",
        "input": input_text,
        "output": output_text
    }
#电池
def format_vehicle_description(row, selected_columns=None):
    if 'CAR_ID' in row.index:
        row = row.drop(labels='CAR_ID')

    if selected_columns is not None:
        row = row[selected_columns]

    input_parts = []
    for col in row.index:
        if is_valid_value(row[col]):
            input_parts.append(f"{col}：{row[col]}")
    input_text = ",".join(input_parts)

    desc = []

    if is_valid_value(row.get("品牌系列")):
        desc.append(f"该车属于{row['品牌系列']}系列")
    if is_valid_value(row.get("车型名称")):
        desc.append(f"，这款 {row['车型名称']}")

    if is_valid_value(row.get("电池类型")):
        desc.append(f"，标配{row['电池类型']}")
    if is_valid_value(row.get("WLTC纯电续航里程_km")):
        desc.append(f"，WLTC工况下的纯电续航为{row['WLTC纯电续航里程_km']}公里")
    if is_valid_value(row.get("电池能量_kWh")):
        desc.append(f"，电池容量为{row['电池能量_kWh']}千瓦时")
    if is_valid_value(row.get("快充功能")):
        desc.append(f"，快充功能：{row['快充功能']}")
    if is_valid_value(row.get("电池快充时间_小时")):
        desc.append(f"，快充时间约为{row['电池快充时间_小时']}小时")
    if is_valid_value(row.get("电池慢充时间_小时")):
        desc.append(f"，慢充时间约为{row['电池慢充时间_小时']}小时")
    if is_valid_value(row.get("电池快充电量范围__")):
        desc.append(f"，快充电量范围：{row['电池快充电量范围__']}%")
    if is_valid_value(row.get("电池慢充电量范围__")):
        desc.append(f"，慢充电量范围：{row['电池慢充电量范围__']}%")
    if is_valid_value(row.get("慢充接口位置")):
        desc.append(f"，慢充接口位于{row['慢充接口位置']}")
    if is_valid_value(row.get("快充接口位置")):
        desc.append(f"，快充接口位于{row['快充接口位置']}")
    if is_valid_value(row.get("电芯品牌")):
        desc.append(f"，电芯品牌为{row['电芯品牌']}")
    if is_valid_value(row.get("电池冷却方式")):
        desc.append(f"，采用{row['电池冷却方式']}冷却")
    if is_valid_value(row.get("百公里耗电量_kWh_100km")):
        desc.append(f"，百公里耗电量为{row['百公里耗电量_kWh_100km']}千瓦时")
    if is_valid_value(row.get("CLTC纯电续航里程_km")):
        desc.append(f"，CLTC工况续航为{row['CLTC纯电续航里程_km']}公里")
    if is_valid_value(row.get("电池能量密度_Wh_kg")):
        desc.append(f"，电池能量密度为{row['电池能量密度_Wh_kg']} Wh/kg")
    if is_valid_value(row.get("快充功率_kW")):
        desc.append(f"，快充功率为{row['快充功率_kW']} kW")
    if is_valid_value(row.get("换电")):
        desc.append(f"，支持换电：{row['换电']}")
    if is_valid_value(row.get("电池组质保")):
        desc.append(f"，电池组质保：{row['电池组质保']}")
    if is_valid_value(row.get("NEDC纯电续航里程_km")):
        desc.append(f"，NEDC工况续航为{row['NEDC纯电续航里程_km']}公里")
    if is_valid_value(row.get("电池特有技术")):
        desc.append(f"，电池特有技术：{row['电池特有技术']}")
    if is_valid_value(row.get("对外交流放电功率_kW")):
        desc.append(f"，对外交流放电功率为{row['对外交流放电功率_kW']} kW")
    if is_valid_value(row.get("高压快充")):
        desc.append(f"，支持高压快充：{row['高压快充']}")
    if is_valid_value(row.get("高压平台V")):
        desc.append(f"，高压平台为{row['高压平台V']}V")
    if is_valid_value(row.get("CLTC综合续航_km")):
        desc.append(f"，CLTC综合续航为{row['CLTC综合续航_km']}公里")
    if is_valid_value(row.get("NEDC综合续航_km")):
        desc.append(f"，NEDC综合续航为{row['NEDC综合续航_km']}公里")
    if is_valid_value(row.get("对外放电最低允许值__")):
        desc.append(f"，对外放电最低允许电量为{row['对外放电最低允许值__']}%")
    if is_valid_value(row.get("WLTC综合续航_km")):
        desc.append(f"，WLTC综合续航为{row['WLTC综合续航_km']}公里")
    if is_valid_value(row.get("WLTP纯电续航里程_km")):
        desc.append(f"，WLTP纯电续航为{row['WLTP纯电续航里程_km']}公里")
    if is_valid_value(row.get("充电桩价格元")):
        desc.append(f"，充电桩价格为{row['充电桩价格元']}元")
    if is_valid_value(row.get("对外直流放电功率_kW")):
        desc.append(f"，对外直流放电功率为{row['对外直流放电功率_kW']} kW")

    output_text = "".join(desc).rstrip("，。") + "。"

    return {
        "instruction": "请根据以下车辆信息生成简洁的自然语言描述。",
        "input": input_text,
        "output": output_text
    }