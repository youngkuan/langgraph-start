"""
阶段 1：LangGraph 的最小骨架
==============================

目标：搞懂 LangGraph 最核心的四个概念 —— State / Node / Edge / StateGraph。

运行（**不需要任何 API key**）：
    uv run python 01_hello_graph.py

四个概念一句话理解：
- State  ：图里流转的「共享状态」，就是一个普通字典（这里用 TypedDict 声明字段）
- Node   ：一个 Python 函数，接收 state，返回要更新的字段（返回一个 dict）
- Edge   ：节点之间的连线，决定执行顺序
- StateGraph：把上面的东西组装起来，compile() 之后才是一个可运行的图
"""
from typing import TypedDict

from langgraph.graph import StateGraph, START, END


# 1) 定义 State：整个图共享的状态，各节点读它、并返回要更新的部分
class State(TypedDict):
    message: str
    count: int


# 2) 定义节点：每个节点是一个普通函数，返回要「合并」回 state 的字段
def node_add_text(state: State) -> dict:
    return {"message": state["message"] + " -> 步骤A"}


def node_add_count(state: State) -> dict:
    return {"count": state["count"] + 1}


def node_final(state: State) -> dict:
    return {"message": state["message"] + " -> 结束"}


# 3) 搭图：加节点，再用边把它们串起来
builder = StateGraph(State)
builder.add_node("add_text", node_add_text)
builder.add_node("add_count", node_add_count)
builder.add_node("final", node_final)

# START 是虚拟的「入口」，END 是虚拟的「出口」
builder.add_edge(START, "add_text")
builder.add_edge("add_text", "add_count")
builder.add_edge("add_count", "final")
builder.add_edge("final", END)

graph = builder.compile()  # 编译后才是可运行的图


if __name__ == "__main__":
    result = graph.invoke({"message": "开始", "count": 0})
    print("最终状态:", result)
    # 期望输出: {'message': '开始 -> 步骤A -> 结束', 'count': 1}
