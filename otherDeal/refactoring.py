from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# 路径配置
base_model_path = "../models/Qwen-llm1.5-1.8B"  # 原始模型，可以是本地路径或 Hugging Face 名
lora_path = "../models/Lora_Qwen_llm"  # LoRA 微调保存的路径
output_path = "../models/Qwen-llm1.5-1.8b-merge"  # 合并后的保存路径

# 加载原模型
model = AutoModelForCausalLM.from_pretrained(base_model_path, torch_dtype="auto")

# 加载 LoRA 并合并
model = PeftModel.from_pretrained(model, lora_path)
model = model.merge_and_unload()  # 🚨 关键：合并 LoRA 权重

# 保存合并后的模型
model.save_pretrained(output_path)

# 同时保存 tokenizer
tokenizer = AutoTokenizer.from_pretrained(base_model_path)
tokenizer.save_pretrained(output_path)
