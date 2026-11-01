"""
阶段 2：Agent 循环 + 工具调用
==============================

目标：搞懂「Agent 循环」到底是怎么一回事，以及如何让模型调用工具。

核心理解 —— Agent 循环就是模型反复做两件事，直到它认为不用再调工具为止：
    1. 模型输出「我要调用哪个工具、参数是什么」（tool call）
    2. 工具真正执行，把结果交回给模型
    模型再判断：还要不要继续调工具？还是信息够了、直接给最终答案？

在 LangGraph 1.x 里，这个循环由 create_agent 一行搭好。
运行： uv run python 03_agent_tools.py
"""
import os

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI

load_dotenv()


# 1) 定义工具：用 @tool 装饰一个普通函数即可。
#    docstring 很重要 —— 模型就是靠它来理解「这个工具是干嘛的、什么时候该用」。
@tool
def add(a: int, b: int) -> int:
    """两个数相加，返回它们的和。"""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """两个数相乘，返回它们的积。"""
    return a * b


# 2) 构造模型（DeepSeek）
model = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)

# 3) 一行搭出 Agent 循环
agent = create_agent(
    model,
    tools=[add, multiply],
    system_prompt="你是一个数学助手，先算清楚再回答，用中文回复。",
)

# 这个 agent 本质上就是一个 StateGraph，内部已经自动内置了
# 「模型节点 + 工具节点 + 一条回到模型的循环边」
print("agent 内部的节点:", list(agent.get_graph().nodes.keys()))
print()


def run(question: str):
    result = agent.invoke({"messages": [("user", question)]})

    # result["messages"] 存着完整对话过程，能清楚看到循环是怎么转的
    print(f"问题：{question}\n")
    for msg in result["messages"]:
        if msg.type == "ai" and getattr(msg, "tool_calls", None):
            print(f"  [模型] 决定调工具: {[(c['name'], c['args']) for c in msg.tool_calls]}")
        elif msg.type == "tool":
            print(f"  [工具] 返回: {msg.content}")
        elif msg.type == "ai":
            print(f"  [模型] 最终回答: {msg.content}")
        else:
            print(f"  [{msg.type}] {msg.content}")

    print(f"\n最终答案：{result['messages'][-1].content}")


if __name__ == "__main__":
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("⚠️  请先 cp .env.example .env 并填入 DEEPSEEK_API_KEY")
    else:
        # 这个问题需要先 add(3,4)，再 multiply(结果,5)，能体现「循环走了两轮」
        run("先算 3 加 4，再把结果乘以 5，等于多少？")
