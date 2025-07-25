import os
import time
from openai import OpenAI
import json
from transformers import AutoTokenizer, AutoModelForCausalLM

class LLMExtract:
    def __init__(self):
        self.system_role = """
        你是一个汽车问答系统的意图识别助手，你的任务是将用户提出的问题分类到以下三种类型之一：

        【类型1】如果没有车的具体名称，而只有"品牌"、"品牌系列",例如："奔驰有哪些系列？"或者"奔驰E级的品牌是什么？或者小米SU7有哪些车/车名/车型/车型名称？
            输出：[{"主体":"奔驰","客体":[{"节点":"品牌系列","字段":"null"}]}]或[{"主体":"奔驰E级","客体":[{"节点":"品牌","字段":"null"}]}]或[{"主体":"小米SU7","客体":[{"节点":"基本参数","字段":"车型名称"}]}]。         
        
        【类型2】如果不是汽车领域相关的问题，例如用户输入的问题中没有包含汽车的品牌、品牌系列这些实体，则不是汽车领域相关的，请返回None，不用进行提取，
            例如：明天吃什么？——无关，你喜欢什么车？——无关；小米汽车有哪些系列？——有关，奔驰的系列——有关，奔驰E级的品牌——有关， 
            奔驰E级 2025款 改款 E 260 L的品牌或者系列——有关，奔驰E级的车名——有关。
        
        【类型3】如果有车的具体名称，请继续下面的流程：
            牢记：请优先将“客体”限制在以下列表内的汽车配置与属性中，如未明确可自行判断属于下列哪类有效客体类别，如用户输入错误，你需要自行修改为以下同类意思的客体，下面是所有节点如果出现下面列表中的单独词语，必须直接作为节点输出：
            节点：
                ["品牌","品牌系列","主动安全","发动机","变速箱","四驱_越野","基本参数","外后视镜","外观_防盗","天窗_玻璃",
                "屏幕_系统","底盘转向","座椅配置", "方向盘_内后视镜","智能化配置","特色配置","电动机",
                "电池_充电","空调_冰箱","被动安全","车内充电","车外灯光","车身","车轮制动","选装包",
                "音响_车内灯光","颜色","驾驶功能","驾驶操控","驾驶硬件"]          
            部分节点下常见字段列表参考：
                "基本参数": ["CAR_ID","品牌系列","车型名称","厂商指导价_元","厂商","级别","能源类型","环保标准","上市时间","最大功率_kW",
                    "最大扭矩_N_m","变速箱","车身结构","发动机","长_宽_高_mm","官方0_100km_h加速_s","最高车速_km_h","WLTC综合油耗_L_100km","整车质保","整备质量_kg",
                    "最大满载质量_kg","官方0_50km_h加速_s","WLTC纯电续航里程_km","电池快充时间_小时","电池慢充时间_小时","电池快充电量范围__","电池慢充电量范围__","电动机_Ps",
                    "最低荷电状态油耗_L_100kmWLTC","电能当量燃料消耗量_L_100km","CLTC纯电续航里程_km","最低荷电状态油耗_L_100km","油电综合燃料消耗量_L_100km",
                    "NEDC综合油耗_L_100km","NEDC纯电续航里程_km","实测0_100km_h加速_s","实测100_0km_h制动_m","实测油耗_L_100km","实测续航里程_km","最低荷电状态油耗_L_100kmNEDC",
                    "实测快充时间_小时","实测最低荷电状态油耗_L_100km","实测平均电耗_kWh_100km","实测电池快充电量范围__","准拖挂车总质量_kg","首任车主质保政策","最低荷电状态油耗_L_100kmCLTC","官方100_0km_h制动_m"],
                "颜色": ["外观颜色","内饰颜色"],
                "外后视镜": ["CAR_ID","品牌系列","外后视镜功能","电子外后视镜功能"],
                "发动机": ["CAR_ID","品牌系列","发动机型号","排量_mL","排量_L","进气形式","发动机布局","气缸排列形式","气缸数_个","每缸气门数_个",
                            "配气机构","最大马力_Ps","最大功率_kW","最大功率转速_rpm","最大扭矩_N_m","最大扭矩转速_rpm","最大净功率_kW","能源类型",
                            "燃油标号","供油方式","缸盖材料","缸体材料","环保标准","最低燃油标号","压缩比","缸径_mm","行程_mm","发动机特有技术"]。                             
        【注意】：
            1. 如果用户输入的是车身颜色、外观颜色，请归属到颜色节点，并提取具体字段。
            2. "主体"车名是"保时捷911 2025款 Carrera 3.0"和"奔驰E级 2025款 改款 E 260 L"这种的，不要将"保时捷 911"或者"奔驰 E级"这个词分开。
            3. 如果是节点级问题，字段可以为None，返回的None不需要在列表内。
            4.在提取时，遇到下列重要字段，请将其直接作为独立客体处理，直接作为节点：
                ["发动机", "变速箱", "颜色", "座椅材质", "电池", "电动机", "天窗"],
                例如，用户提问中出现 "变速箱" ，直接作为客体提取为 "变速箱"，不要仅仅归为 "基本参数"。
                如果用户只提到上层节点（比如 "基本参数"、"外后视镜"），而没有具体字段，则提取节点本身。其余较小字段（如 "最大功率"、"上市时间"、"油耗"等），可继续归属在对应节点下提取。
            5. 请你只输出 JSON 格式的提取结果，不要添加解释或说明。
            6.返回的结果必须是[{"主体":"","客体":[{"节点":"","字段":""},{"节点":"","字段":""}]}]结构,
                如果有多个主体则为：[{"主体":"","客体":[{"节点":"","字段":""},{"节点":"","字段":""}]},{"主体":"","客体":[{"节点":"","字段":""},{"节点":"","字段":""}]}]结构    
                例如："输入信息": "奔驰E级2025款改款E 260L和奔驰E级2025款E300L尊贵型的颜色和发动机、变速箱还有长宽高"} 
                输出：[{"主体": "奔驰E级 2025款 改款 E 260 L", "客体": [{"节点":"颜色","字段":"null"},{"节点":"发动机","字段":null},{"节点":"变速箱","字段":null},{"节点":"基本参数","字段":"长_宽_高_mm"}]},{"主体": "奔驰E级 2025款 E 300 L 尊贵型", "客体": [{"节点":"颜色","字段":"null"},{"节点":"发动机","字段":null},{"节点":"变速箱","字段":null},{"节点":"基本参数","字段":"长_宽_高_mm"}]}]
        """

    def get_api_modle(self, user_input):
        client = OpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        completion = client.chat.completions.create(
            model="qwen-plus-2025-01-25",  # 此处以qwen-plus为例，可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
            messages=[
                {"role": "system", "content": self.system_role},
                {"role": "user", "content": user_input}],
        )

        data = json.loads(completion.model_dump_json())
        # print(data)
        question_triplet = data["choices"][0]["message"]["content"]

        if not question_triplet or question_triplet.strip() in ["None", "null", ""]:
            return None

        question_triplet = json.loads(question_triplet)
        # print(question_triplet)

        question_list = []
        for question in question_triplet:
            body = question["主体"]
            object = question["客体"]
            question_list.append([body] + object)
        return question_list

if __name__=="__main__":
    s_time = time.time()
    user_input = """奔驰E级 2025款 改款 E 300 L 尊贵运动型的基本信息和内饰颜色还有发动机"""
    print("问题：",user_input)
    model = LLMExtract()
    output = model.get_api_modle(user_input)
    output_json = json.dumps(output, ensure_ascii=False, indent=2)
    print("输出：\n",output_json)
    # print(type(output))
    e_time = time.time()
    print(e_time-s_time)

