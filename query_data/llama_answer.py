import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
# -*- coding: utf-8 -*-
import os
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from peft import PeftModel
import time


class LoadModel:
    def __init__(self):
        self.base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../models/Qwen-llm1.5-1.8B"))
        self.lora_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../models/Lora_Qwen_llm/5-16best"))

    def load_base_model(self):
        model = AutoModelForCausalLM.from_pretrained(
            self.base_path, trust_remote_code=True,
            torch_dtype=torch.float16
        ).cuda()
        print("向量模型当前模型所在设备：", next(model.parameters()).device)
        tokenizer = AutoTokenizer.from_pretrained(
            self.base_path, trust_remote_code=True
        )
        return model, tokenizer

    def load_lora_model(self):
        base_model, tokenizer = self.load_base_model()
        lora_model = PeftModel.from_pretrained(base_model, self.lora_path)
        # lora_model = torch.compile(lora_model)  # 加速推理
        return lora_model, tokenizer

    def infer(self, prompt, model, tokenizer):
        s_time = time.time()
        inputs = tokenizer(prompt, return_tensors="pt")
        inputs = {k: v.cuda() for k, v in inputs.items()}

        model.eval()
        with torch.inference_mode():
            outputs = model.generate(
                **inputs,
                max_new_tokens=512,
                do_sample=True,
                top_p=0.9,  # 0.85 0.95
                # temperature=0.2,  # 0.9 0.45
                repetition_penalty=1.1,  # 1.2 1.2
            )
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        e_time = time.time()
        print(e_time - s_time)  # 12.134304523468018秒
        return response


if __name__ == "__main__":
    # text = {"品牌系列": "途锐", "车型名称": "途锐 2023款 3.0TSI 锐尊版", "厂商指导价_元": "77.38万", "厂商": "大众(进口)", "级别": "中大型SUV","上市时间": "2023.06", "长_宽_高_mm": "4878*1984*1697"}

    # 加载模型，只加载一次
    model_loader = LoadModel()
    model, tokenizer = model_loader.load_lora_model()

    # 循环提问
    while True:
        text = input("请输入车辆信息（JSON）：\n")
        if text.strip().lower() in {"exit", "quit"}:
            print("已退出对话。")
            break
        prompt = f"""请根据以下'输入'字段中的JSON格式车辆信息生成简洁的自然语言描述。生成的结果应该以'输出'字段的形式呈现：\n输入：{text}\n输出："""
        # prompt = f"""指令：请根据以下'输入'字段中的JSON内的所有内容，用人性化的自然语言的方式描述出来。生成的结果作为'输出'字段的结果：\n输入：{text}\n输出："""
        result = model_loader.infer(prompt, model, tokenizer)
        print("模型输出：", result)
        # print("该问题有", len(text), "个属性")
        # # 构造提示词并推理
        # if isinstance(text, list):
        #     if len(text) == 1:
        #         prompt = f"""请根据以下'输入'字段中的JSON格式车辆信息生成简洁的自然语言描述。生成的结果应该以'输出'字段的形式呈现：\n输入：{text}\n输出："""
        #         generate_result = self.loadModel.infer(prompt, self.model, self.tokenizer)
        #         # print("生成结果：\n", generate_result)
        #         clean_result = self.cleanOutput(generate_result)
        #         print("处理结果：\n", clean_result)
        #         return clean_result
        #     elif len(text) >= 2:
        #         for data in text:
        #             prompt = f"""请根据以下'输入'字段中的JSON格式车辆信息生成简洁的自然语言描述。生成的结果应该以'输出'字段的形式呈现：\n输入：{data}\n输出："""
        #             generate_result = self.loadModel.infer(prompt, self.model, self.tokenizer)
        #             # print("生成结果：", generate_result)
        #             clean_result = self.cleanOutput(generate_result)
        #             # print("处理结果：", clean_result)
        #             results += clean_result + "\n"
        #         print("最终结果：\n",results)
        #         return results
        # return "暂无信息"