"""
阶段 2 进阶：手写 Agent 循环（拆解 create_agent 到底做了什么）
================================================================

上一节 03 用 create_agent 一行搞定，这一节我们**不用它**，自己用
StateGraph + 条件边把「模型 ⇄ 工具」的循环亲手搭出来。

搭完你会明白：create_agent 本质上就是下面这几行。

运行： uv run python 04_agent_manual.py
"""
import os
from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.prebuilt import ToolNode

load_dotenv()


@tool
def add(a: int, b: int) -> int:
    """两个数相加，返回它们的和。"""
    return a + b


@tool
def multiply(a: int, b: int) -> int:
    """两个数相乘，返回它们的积。"""
    return a * b


tools = [add, multiply]

model = ChatOpenAI(
    model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
)

# 关键①：把工具「绑定」到模型上，模型才会在需要时输出 tool_calls
model_with_tools = model.bind_tools(tools)


# 关键②：State 里用 add_messages 作 reducer —— 新消息是「追加」进列表，而不是覆盖。
#        这样多轮对话、工具调用记录才能一路累积下来。
class State(TypedDict):
    messages: Annotated[list, add_messages]


# 关键③：model 节点 —— 把当前对话发给模型，返回模型的回复（可能含 tool_calls）
def call_model(state: State):
    return {"messages": [model_with_tools.invoke(state["messages"])]}


# 关键④：tools 节点 —— ToolNode 会自动执行上一条 AIMessage 里的 tool_calls，
#        并把每个结果作为一条 ToolMessage 返回。执行逻辑不用自己写。

# 关键⑤：路由函数 —— 看最后一条消息：有 tool_calls → 去 tools 节点；否则 → 结束
def route_after_model(state: State):
    last = state["messages"][-1]
    if last.tool_calls:
        return "tools"
    return END


# 手工搭图
builder = StateGraph(State)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode(tools))

builder.add_edge(START, "model")
builder.add_conditional_edges("model", route_after_model, {"tools": "tools", END: END})
builder.add_edge("tools", "model")   # ← 这一条就是「循环」：工具跑完回到模型

graph = builder.compile()

print("手写 agent 的节点:", list(graph.get_graph().nodes.keys()))
print("手写 agent 的边:", list(graph.get_graph().edges))
print()


def run(question: str):
    result = graph.invoke({"messages": [("user", question)]})
    print(f"问题：{question}\n")
    for msg in result["messages"]:
        if msg.type == "ai" and getattr(msg, "tool_calls", None):
            print(f"  [模型] 调工具: {[(c['name'], c['args']) for c in msg.tool_calls]}")
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
        run("先算 3 加 4，再把结果乘以 5，等于多少？")
