"""
阶段 1.5：第一个带 LLM 的节点
==============================

目标：验证 DeepSeek 接入是否正常，并学会「在节点里调用大模型」。

运行前：
    1. 复制 .env.example 为 .env
    2. 在 .env 里填入你的 DEEPSEEK_API_KEY
然后运行：
    uv run python 02_llm_node.py

关键点：DeepSeek 提供 OpenAI 兼容接口，所以直接用 langchain_openai 的
ChatOpenAI，把 base_url 指向 DeepSeek 即可，不用装专门的 deepseek 包。
"""
import os
from typing import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END

load_dotenv()  # 把 .env 里的 key 读进环境变量


def build_llm() -> ChatOpenAI:
    """构造 DeepSeek 模型。deepseek-chat 是对话模型，deepseek-reasoner 是推理模型。"""
    return ChatOpenAI(
        model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        api_key=os.getenv("DEEPSEEK_API_KEY"),
        base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
    )


class State(TypedDict):
    question: str
    answer: str


def answer_node(state: State) -> dict:
    llm = build_llm()
    reply = llm.invoke(state["question"])  # invoke 返回 AIMessage，.content 是文本
    return {"answer": reply.content}


builder = StateGraph(State)
builder.add_node("answer", answer_node)
builder.add_edge(START, "answer")
builder.add_edge("answer", END)
graph = builder.compile()


if __name__ == "__main__":
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("⚠️  还没配置 key：请复制 .env.example 为 .env，并填入 DEEPSEEK_API_KEY")
    else:
        result = graph.invoke({"question": "用一句话介绍你自己"})
        print("DeepSeek 回答:", result["answer"])
