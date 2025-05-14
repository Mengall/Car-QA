from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, DataCollatorForLanguageModeling, Trainer
from peft import LoraConfig, TaskType, get_peft_model
from datasets import Dataset
import json
import torch
from torch.utils.tensorboard import SummaryWriter

tokenizer = AutoTokenizer.from_pretrained("./models/Qwen-llm1.5-1.8B", trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained("./models/Qwen-llm1.5-1.8B",
                                             torch_dtype=torch.float16,
                                             trust_remote_code=True,
                                             low_cpu_mem_usage=False  # 防止出现 meta tensor
                                             )
model.to("cuda")

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


def load_data():
    with open("./data/car_finetune_data.jsonl", 'r', encoding='utf-8') as f:
        lines = f.readlines()
        return [json.loads(line.strip()) for line in lines]


def process(data):
    # prompt = f"""请根据以下'输入'字段中的JSON格式车辆信息生成简洁的自然语言描述。生成的结果应该以'输出'字段的形式呈现：\n输入：{data['input']}\n输出：{data['output']}"""
    prompt = f"""指令：{data['instruction']}\n输入：{data['input']}\n输出：{data['output']}"""
    encoded = tokenizer(prompt, truncation=True, padding="max_length", max_length=512)
    encoded["labels"] = encoded["input_ids"]
    return encoded


def add_labels(example):
    example["labels"] = example["input_ids"]
    return example

if __name__ == "__main__":
    load_data = load_data()
    dataset = Dataset.from_list(load_data).map(process)
    # dataset = dataset.map(add_labels)  # 用于计算损失

    training_args = TrainingArguments(
        output_dir="./models/Lora_Qwen_llm",  # 模型保存目录
        per_device_train_batch_size=2,  # 每个GPU的batch size
        gradient_accumulation_steps=4,  # 梯度累积步数，相当于总batch size = 2 x 4 = 8
        num_train_epochs=3,  # 训练轮数
        logging_steps=10,  # 日志记录步数
        save_steps=200,  # 每200步保存一次
        save_total_limit=2,  # 最多保留2个checkpoint，旧的会被删除
        fp16=True,  # 使用混合精度训练（需要GPU支持）
        learning_rate=2e-4,  # 学习率
        warmup_steps=20,  # 预热步数
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

    model.save_pretrained("./models/Lora_Qwen_llm")
    tokenizer.save_pretrained("./models/Lora_Qwen_llm")
