import logging
import os
from typing import TypedDict, Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END, add_messages
from langgraph.prebuilt import ToolNode

from tools import query_weather, send_email

logging.basicConfig(level=logging.INFO)
load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]


def route_after_model(state: State) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return "end"


class WeatherAgent:
    def __init__(self):
        self.model = ChatOpenAI(model=os.environ.get("DEEPSEEK_MODEL"), api_key=os.environ.get("DEEPSEEK_API_KEY"),
                                base_url=os.environ.get("DEEPSEEK_BASE_URL"))
        self.tools = [query_weather, send_email]
        self.model = self.model.bind_tools(self.tools)

        builder = StateGraph(State)
        builder.add_node("model", self.call_model)
        builder.add_node("tools", ToolNode(self.tools))

        builder.add_edge(START, "model")
        builder.add_conditional_edges("model", route_after_model, {"tools": "tools", "end": END})
        builder.add_edge("tools", "model")  # ← 这一条就是「循环」：工具跑完回到模型

        self.graph = builder.compile()

    def call_model(self, state: State):
        response = self.model.invoke(state["messages"])  # 只传 messages 列表
        return {"messages": [response]}

    def chat(self, message: str):
        """chat with user
        Args:
            message (str): weather message from user
        """
        response = self.graph.invoke({"messages": [HumanMessage(message)]})
        logging.info(f"用户问题：{message}\n")
        for msg in response["messages"]:
            if msg.type == "ai" and getattr(msg, "tool_calls", None):
                logging.info(f"  [模型] 调工具: {[(c['name'], c['args']) for c in msg.tool_calls]}")
            elif msg.type == "tool":
                logging.info(f"  [工具] 返回: {msg.content}")
            elif msg.type == "ai":
                logging.info(f"  [模型] 最终回答: {msg.content}")
            else:
                logging.info(f"  [{msg.type}] {msg.content}")
        logging.info(f"\n最终答案：{response['messages'][-1].content}")


if __name__ == "__main__":
    agent = WeatherAgent()
    agent.chat("今天天气怎么样？发送给yangkuan@gmail.com")
