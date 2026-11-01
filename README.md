# langgraph-start

LangGraph 学习项目：从零到多智能体。跟着下面的阶段一步步走，每个阶段都对应一个能跑起来的案例。

> ⚠️ 版本提示：本项目基于 **LangGraph 1.x**（当前 1.2.x）。网上很多 2024 年的旧教程还在用 `create_react_agent`，1.0 之后已迁移为 `langchain.agents` 里的 `create_agent`，看旧教程时留意别照抄报错。

## 环境（已搭好）

- Python 3.12（由 `uv` 自动管理，不依赖系统自带的 3.7）
- 依赖：`langgraph` / `langchain` / `langchain-openai` / `python-dotenv`

```bash
uv sync          # 安装/同步依赖（首次会自动下载 Python 3.12）
cp .env.example .env   # 然后编辑 .env，填入你的 DEEPSEEK_API_KEY
```

## 当前案例

| 文件 | 阶段 | 学什么 | 需要 key |
|---|---|---|---|
| `01_hello_graph.py` | 1 | State / Node / Edge / StateGraph 四个核心概念 | 否 |
| `02_llm_node.py` | 1.5 | 在节点里调用 DeepSeek，验证接入 | 是 |
| `03_agent_tools.py` | 2 | Agent 循环 + 工具调用（`create_agent` + `@tool`） | 是 |
| `04_agent_manual.py` | 2 进阶 | 手写 Agent 循环（拆解 `create_agent`，条件边 + ToolNode） | 是 |

```bash
uv run python 01_hello_graph.py   # 无需 key
uv run python 02_llm_node.py      # 需先填 .env
uv run python 03_agent_tools.py   # Agent 循环 + 工具调用
uv run python 04_agent_manual.py  # 手写 Agent 循环
```

## 学习路线（8 个阶段）

| 阶段 | 核心概念 | 案例 |
|---|---|---|
| 0 | 环境准备 | Hello World（✅ 已完成） |
| 1 | State / Node / Edge / StateGraph | 最小图骨架（✅ `01`） |
| 2 | 工具调用 + Agent 循环（`create_agent`） | ReAct Agent（✅ `03`） |
| 3 | 状态 + 记忆持久化（`checkpointer`、`thread_id`） | 多轮对话机器人 |
| 4 | 条件路由（`conditional_edges`、`Command`） | RAG 检索 Agent |
| 5 | 人机协同 HITL（`interrupt`、`resume`） | 审批流 |
| 6 | 流式 / 子图 / 并行（`stream`、`subgraph`、map-reduce） | 研究报告生成器 |
| 7 | 多 Agent 编排（supervisor-worker） | 多角色团队 |
| 8 | 部署与可观测（LangGraph Platform / LangSmith） | 把案例变成服务 |

## 推荐学习资源

- [LangChain Academy — Introduction to LangGraph](https://academy.langchain.com/)（官方免费课，跟 v1.x）
- [官方文档](https://langchain-ai.github.io/langgraph/)
- [尚硅谷 LangGraph 教程（B站 132 集）+ GitHub 课件](https://github.com/xbsheng/atguigu-note)
- [kevinten-ai/ai-agent-langgraph](https://github.com/kevinten-ai/ai-agent-langgraph)（从零到生产的 9 阶段路线）
