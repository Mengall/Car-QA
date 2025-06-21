import os
import sys
import time
import streamlit as st
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.schema import HumanMessage, AIMessage
from langchain_community.chat_models import ChatOpenAI

# 添加项目根目录到 sys.path，确保 query_data 可被导入
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from query_data.Answer import CarQueryProcessor  # 此时必须保证 query_data 目录有 __init__.py


# ==== 初始化 processor，只初始化一次 ====
if "processor" not in st.session_state:
    st.session_state.processor = CarQueryProcessor(
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

# ==== 初始化 LangChain 模型 ====
if "llm" not in st.session_state:
    st.session_state.llm = ChatOpenAI(
        openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
        openai_api_base="https://dashscope.aliyuncs.com/compatible-mode/v1",
        model_name="qwen-plus-2025-04-28"
    )

# ==== 初始化 Streamlit 页面 ====
st.set_page_config(page_title="🚗 智能汽车问答系统", layout="wide")
st.title("🚗 智能汽车问答系统")
st.markdown("##### 您的专业汽车咨询助手，为您解答各类汽车相关问题")

# ==== 初始化聊天历史与 memory ====
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "👋 您好！我是汽车问答助手。\n我可以回答关于汽车的各种问题，例如：\n- 奔驰E级 2025款 改款 E 260 L 的基本参数\n- 宝马3系的动力性能如何\n请问您想了解什么？"}
    ]

if "memory" not in st.session_state:
    st.session_state.memory = ConversationBufferMemory(return_messages=True)

# ==== ConversationChain 支持多轮对话 ====
conversation = ConversationChain(
    llm=st.session_state.llm,
    memory=st.session_state.memory,
    verbose=True
)

# ==== 显示历史记录 ====
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).markdown(msg["content"])

# ==== 用户输入 ====
user_input = st.chat_input("请输入您的问题")

if user_input:
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        start = time.time()
        prompt = st.session_state.processor.batch_query_from_question(user_input)
        answer = st.session_state.processor.llm_answer(prompt)
        print(f"[INFO] 总耗时: {time.time() - start:.2f}s")
    except Exception as e:
        answer = f"[ERROR] 处理问题时出错：{str(e)}"

    # 存入 LangChain memory（支持多轮上下文）
    st.session_state.memory.chat_memory.add_user_message(user_input)
    st.session_state.memory.chat_memory.add_ai_message(answer)

    # 显示助手回复
    st.chat_message("assistant").markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

# ==== 清空对话按钮 ====
if st.button("🧹 清空对话", use_container_width=True):
    st.session_state.messages = []
    st.session_state.memory = ConversationBufferMemory(return_messages=True)
    st.experimental_rerun()
