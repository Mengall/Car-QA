import json
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from bert_score import score
from tqdm import tqdm
import argparse
from peft import PeftModel
import os

path = "../models"


def load_eval_data(path):
    with open(path, 'r', encoding='utf-8') as f:
        return [json.loads(line.strip()) for line in f]


def generate_output(model, tokenizer, input_text, max_new_tokens=512):
    prompt = f"指令：请根据以下车辆信息生成简洁的自然语言描述，输出结构为output值的结构。\n输入：{input_text}\n输出："
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=1024).to("cuda")
    outputs = model.generate(**inputs,
                             max_new_tokens=max_new_tokens,
                             do_sample=True,
                             top_p=0.9,
                             repetition_penalty=1.1
                             )
    return tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True).strip()


def evaluate(base_model_path, lora_model_path, eval_data_path, lang="zh"):
    print(f"Loading model from: {base_model_path}")
    tokenizer = AutoTokenizer.from_pretrained(base_model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(base_model_path,
                                                      trust_remote_code=True,
                                                      torch_dtype=torch.float16).to("cuda")
    # model = PeftModel.from_pretrained(base_model, lora_model_path)

    eval_data = load_eval_data(eval_data_path)
    print(f"Loaded {len(eval_data)} samples from {eval_data_path}")

    candidates, references, output_records = [], [], []

    for sample in tqdm(eval_data, desc="Generating..."):
        input_text = sample["input"]
        reference = sample["output"].strip()
        candidate = generate_output(model, tokenizer, input_text)

        candidates.append(candidate)
        references.append(reference)

        output_records.append({
            "input": input_text,
            "reference": reference,
            "candidate": candidate
        })

    print("Calculating BERTScore...")
    P, R, F1 = score(candidates, references, lang=lang, model_type="bert-base-chinese", verbose=True)

    precision = P.mean().item()
    recall = R.mean().item()
    f1_score = F1.mean().item()

    # 添加每条样本的 P、R、F1
    for i in range(len(output_records)):
        output_records[i]["precision"] = round(P[i].item(), 4)
        output_records[i]["recall"] = round(R[i].item(), 4)
        output_records[i]["f1"] = round(F1[i].item(), 4)

    # 保存到文件
    output_file = os.path.splitext(eval_data_path)[0] + "base_evaluate.jsonl"
    with open(output_file, "w", encoding="utf-8") as out_f:
        for record in output_records:
            print(json.dumps(record, ensure_ascii=False))
            out_f.write(json.dumps(record, ensure_ascii=False) + "\n")
        # 添加最终整体 BERTScore
        summary = {
            "type": "bert_score_summary",
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1": round(f1_score, 4)
        }
        print(summary)

        out_f.write(json.dumps(summary, ensure_ascii=False) + "\n")
        print(f"Saved all generation outputs and scores to: {output_file}")

    return f1_score


if __name__ == "__main__":
    if __name__ == "__main__":
        parser = argparse.ArgumentParser()
        parser.add_argument("--base_model_path", type=str, default="../models/Qwen-llm1.5-1.8B",
                            help="Path to base model")
        parser.add_argument("--lora_model_path", type=str, default="../models/Lora_Qwen_llm/5-16best",
                            help="Path to LoRA fine-tuned model")
        parser.add_argument("--eval_data", type=str, default="../data/lora_data/test/new_car_finetune_data.jsonl",
                            help="Path to eval data (.jsonl)")
        parser.add_argument("--lang", type=str, default="zh", help="Language code (e.g., 'zh' for Chinese)")
        args = parser.parse_args()
        evaluate(args.base_model_path, args.lora_model_path, args.eval_data, args.lang)
