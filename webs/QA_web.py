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

with gr.Blocks(title="CAR-QA", css="""
    .container { width: 90%; max-width: 90%; margin: 0 auto; }
    #chatbot { height: 400px }
""") as demo:
    with gr.Column(elem_classes="container"):
        gr.HTML("""
            <div style="text-align: center; margin-bottom: 1rem">
                <h1 style="color: #2f80ed; margin-bottom: 0.5rem">🚗 智能汽车问答系统</h1>
                <p style="color: #666; font-size: 0.9rem">您的专业汽车咨询助手，为您解答各类汽车相关问题</p>
            </div>
        """)
        
        initial_message = [{
            "role": "assistant",
            "content": "👋 您好！我是汽车问答助手。\n我可以回答关于汽车的各种问题，例如：\n- 奔驰E级 2025款 改款 E 260 L 的基本参数\n- 宝马3系的动力性能如何\n请问您想了解什么？"
        }]
        
        chatbot = gr.Chatbot(
            value=initial_message, 
            type="messages",
            height=400,  # 调整高度
            container=True,
            elem_classes="chatbot"
        )
        
        with gr.Row(elem_classes="input-row"):
            msg = gr.Textbox(
                placeholder="请输入您的问题...", 
                label="问题输入",
                scale=9
            )
            with gr.Column(scale=1):
                submit = gr.Button("发送", variant="primary")
                clear = gr.Button("清空", variant="secondary")

    def user(user_message, history):
        history = history or []
        history.append({"role": "user", "content": user_message})
        return "", history

    def bot(history):
        if not history:
            return history
            
        user_message = history[-1]["content"]
        try:
            start_time = time.time()
            prompt = processor.batch_query_from_question(user_message)
            answer = processor.llm_answer(prompt)
            end_time = time.time()
            print(f"[INFO] 查询耗时：{end_time - start_time:.2f} 秒")
        except Exception as e:
            answer = f"[ERROR] 处理问题时出错：{str(e)}"
            
        history.append({"role": "assistant", "content": answer})
        yield history

    msg.submit(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    submit.click(user, [msg, chatbot], [msg, chatbot], queue=False).then(
        bot, chatbot, chatbot
    )
    clear.click(lambda: [], None, chatbot, queue=False)

if __name__ == "__main__":
    demo.launch(share=True)