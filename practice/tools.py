import random
import logging

from langchain_core.tools import tool


@tool(parse_docstring=True)
def query_weather() -> str:
    """查询天气

    Returns: 今天的天气信息
    """
    randint = random.Random().randint(0, 100)
    if randint % 2 == 0:
        return "今天天气晴朗，气温28摄氏度"
    return "今天天气阴，气温12摄氏度"


@tool(parse_docstring=True)
def send_email(recipient: str, subject: str, body: str):
    """发送邮件

    Args:
        recipient: 收件人
        subject: 主题
        body: 邮件内容
    """
    logging.info(f"send email successfully, recipient: {recipient}, subject: {subject}, body: {body}")
