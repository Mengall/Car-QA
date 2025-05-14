import gradio as gr
import random
import time
from query_data.Answer import CarQueryProcessor

# === 初始化配置 ===
processor = CarQueryProcessor(
    neo4j_url="bolt://localhost:7687",
    username="neo4j",
    password="neo4j0000",
    model_path=r"..\models\models--moka-ai--m3e-base\snapshots\764b537a0e50e5c7d64db883f2d2e051cbe3c64c",
    body_index="../data/body_car_vectors_ip.index",
    body_json="../data/body_car_name.json",
    object_index="../data/object_car_vectors_ip.index",
    object_json="../data/object_car_name.json",
    body_path="../data/body_field_map.json",
    object_path="../data/object_field_map.json"
)
# load_model = processor.loadModel()
# model, tokenizer = load_model.
# # === 示例问题 ===
# question = "奔驰E级 2025款 改款 E 260 L 的基本参数"
# prompt = processor.batch_query_from_question(question)
# answer = processor.llm_answer(prompt, model)

with gr.Blocks() as demo:
    chatbot = gr.Chatbot(type="messages")
    msg = gr.Textbox()
    clear = gr.Button("Clear")

    def user(user_message, history: list):
        return "", history + [{"role": "user", "content": user_message}]


    def bot(history: list):
        user_message = history[-1]["content"]
        try:
            start_time = time.time()  # ⏱️ 开始计时

            prompt = processor.batch_query_from_question(user_message)
            answer = processor.llm_answer(prompt)

            end_time = time.time()  # ⏱️ 结束计时
            duration = end_time - start_time
            print(f"[INFO] 查询耗时：{duration:.2f} 秒")

        except Exception as e:
            answer = f"[ERROR] 处理问题时出错：{str(e)}"
        history.append({"role": "assistant", "content": ""})
        for ch in answer:
            history[-1]["content"] += ch
            yield history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: None, None, chatbot, queue=False)

if __name__ == "__main__":
    demo.launch(share=True)