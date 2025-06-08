from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, DataCollatorForLanguageModeling, Trainer
from peft import LoraConfig, TaskType, get_peft_model
from datasets import Dataset
import json
import torch
import os, sys
import logging
from datetime import datetime

tokenizer = AutoTokenizer.from_pretrained("./models/Qwen-llm1.5-1.8B", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("./models/Qwen-llm1.5-1.8B",
                                             torch_dtype=torch.float16,
                                             trust_remote_code=True,
                                             low_cpu_mem_usage=False  # 防止出现 meta tensor
                                             )
# 禁用 sliding_window 或不启用 sdpa / FlashAttention

model.to("cuda")
# model.config.sliding_window = None
# for name, module in model.named_modules():
#     if isinstance(module, torch.nn.Linear):
#         print(name)

lora_config = LoraConfig(
    r=8,
    lora_alpha=32,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # 微调哪些模块, 还有"gate_proj", "up_proj", "down_proj"
    lora_dropout=0.05,
    bias="none",
    task_type=TaskType.CAUSAL_LM
)
model = get_peft_model(model, lora_config)


def setup_logger(log_dir="./logs", log_prefix="train_log"):
    os.makedirs(log_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_path = os.path.join(log_dir, f"{log_prefix}_{timestamp}.log")

    logger = logging.getLogger(log_prefix)  # 指定名称，避免 root logger 重复
    logger.setLevel(logging.INFO)

    # 清理已有 handler，避免重复写入和多个日志文件
    if logger.hasHandlers():
        logger.handlers.clear()

    # 文件日志
    file_handler = logging.FileHandler(log_path, mode='w', encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # 控制台日志
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


def load_data():
    with open("./data/lora_data/train/car_finetune_data.jsonl", 'r', encoding='utf-8') as f:
        lines = f.readlines()
        return [json.loads(line.strip()) for line in lines]


def process(data):
    # prompt = f"""指令：{data['instruction']}\n输入：{data['input']}\n输出：{data['output']}"""
    prompt = f"""指令：请根据以下车辆信息生成简洁的自然语言描述，输出结构为output值的结构。\n输入：{data['input']}\n输出：{data['output']}"""
    # prompt = f"""指令：请根据以下'输入'字段中的JSON内的所有内容，用人性化的自然语言的方式描述出来。生成的结果作为'输出'字段的结果：\n输入：{data['input']}\n输出：{data['output']}"""
    encoded = tokenizer(prompt, truncation=True, padding="max_length", max_length=512)
    encoded["labels"] = encoded["input_ids"]
    return encoded


def add_labels(example):
    example["labels"] = example["input_ids"]
    return example

if __name__ == "__main__":
    logger = setup_logger(log_dir="./logs", log_prefix="car_finetune")
    logger.info("加载数据中...")

    load_data = load_data()
    logger.info(f"加载完成，共 {len(load_data)} 条样本")

    dataset = Dataset.from_list(load_data).map(process)
    logger.info("数据编码完成，开始训练...")
    # dataset = dataset.map(add_labels)  # 用于计算损失

    training_args = TrainingArguments(
        output_dir="./models/Lora_Qwen_llm",  # 模型保存目录
        per_device_train_batch_size=2,  # 每个GPU的batch size
        gradient_accumulation_steps=4,  # 梯度累积步数，相当于总batch size = 2 x 4 = 8
        num_train_epochs=3,  # 训练轮数
        logging_steps=10,  # 日志记录步数
        save_steps=100,  # 每200步保存一次
        save_total_limit=4,  # 最多保留2个checkpoint，旧的会被删除
        fp16=True,  # 使用混合精度训练（需要GPU支持）
        learning_rate=5e-5,  # 学习率 5e-5
        warmup_steps=50,  # 预热步数
        lr_scheduler_type="linear",  # 学习率调度策略
        report_to="tensorboard",  # 日志输出到 tensorboard
        logging_dir="./logs"  # tensorboard 日志目录
    )


    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False  # 不使用 Masked Language Model
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        tokenizer=tokenizer,
        data_collator=data_collator,
        # label_names=["labels"]  # 显式指定 label 字段名
    )
    trainer.train()
    logger.info("训练完成，保存模型中...")

    model.save_pretrained("./models/Lora_Qwen_llm")
    tokenizer.save_pretrained("./models/Lora_Qwen_llm")
    logger.info("模型和分词器保存完成 ✅")