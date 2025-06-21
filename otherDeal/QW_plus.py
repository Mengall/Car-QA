from openai import OpenAI
import json
import os
import time

client = OpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
)

def generate_response(example):
    prompt = json.dumps(example, ensure_ascii=False)
    try:
        completion = client.chat.completions.create(
            model="qwen-plus",
            messages=[
                {"role": "system", "content": "请帮我将用户输入的json内的所有内容，用人性化的自然语言的方式描述出来，输出的'车型名称'要与输入的名称一致，最好直接用'车型名称'字段的值开头，不要用'*'和'#'。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,  # 设置温度值（默认0.7，此处设为较低值以提高确定性）
            max_tokens=512,  # 限制生成的最大Token数
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print("API error:", e)
        return None

# 加载输入样本列表
with open("car_inputs.json", "r", encoding="utf-8") as f:
    examples = json.load(f)
num = 0
pairs = []
for example in examples:
    response = generate_response(example)
    print(response)
    if response:
        # cleaned_response = response.replace("\n\n", "\n")
        pairs.append({"input": example, "output": response})
        time.sleep(0.5)  # 限流
        num += 1
        print(num)

# 保存蒸馏样本
with open("distill_data.jsonl", "a", encoding="utf-8") as f:
    for pair in pairs:
        f.write(json.dumps(pair, ensure_ascii=False) + "\n")
print("success")