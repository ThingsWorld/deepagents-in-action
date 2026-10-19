> 本次执行模式：**offline**。源码指纹：`b50cb0d3fd25`。

# 第 4 章 Notebook：任务规划与分解

本 Notebook 配套课程[第 4 章：任务规划与分解](../../content/ch04-task-planning.md)，通过实验理解 `TodoListMiddleware`、`write_todos` 和 `todos` 状态之间的关系。

第 2 章研究助手帮助我们观察 Todo 列表和文件状态，本章进一步关注计划如何更新，以及如何根据实际产物判断任务是否完成。

你只需基础 Python。所有变量都从第一格建立，可以单独运行，无需先执行其他章节。

## 学习目标

跑完本 Notebook 后，你应该能够：

1. 显式启用 `TodoListMiddleware()`，对比未启用与启用时的工具和状态结构；
2. 用多步骤研究任务观察计划制定、搜索、进度更新和结果检查；
3. 查看 `write_todos` 的调用参数、工具结果和 `todos` 状态，说明新列表如何替换旧计划；
4. 解释 `pending`（待办）、`in_progress`（进行中）、`completed`（已完成）的含义，以及何时需要调整计划；
5. 根据实际搜索结果或报告核查产物，区分模型声明完成与任务确实完成；
6. 理解模型可能不调用 `write_todos`，对稳定的结构和行为做检查，不强制固定计划内容或完整状态流转。

**实验范围**：六项学习目标分别由配置对照、研究任务、状态与调整实验，以及独立产物核查和可选规划对照覆盖。

**预期现象**（offline）：未启用时，`write_todos` 未注册、`todos` 字段未声明；显式启用后，两项均存在，检查格打印“检查通过”。研究实验中，脚本按预设顺序写入计划、搜索两次、更新进度，最后给出带来源的比较报告。

## 运行环境与运行模式

使用课程锁定的 Python 3.12 环境，安装与内核选择见 [Notebook 索引](../README.md)。默认 offline 模式在仓库根目录执行：

```bash
uv sync --project notebooks --locked
uv run --project notebooks --locked python -m course_notebooks.run ch04-task-planning
```

| 模式 | 模型 | 工具执行 | 需要的 Key 与依赖 |
|---|---|---|---|
| offline（默认，随附输出） | 脚本模型按预设顺序请求工具 | 真实执行 Todo 与搜索函数，搜索返回本地样例 | 无 Key；使用课程基础依赖 |
| live | 研究实验使用真实模型，自主选择工具 | 真实执行 Todo 工具与 Tavily 搜索 | 模型 Key、`TAVILY_API_KEY` 和 `search` 依赖组 |

offline 不联网，框架与工具仍真实执行；固定计划和报告不证明模型具有自主规划能力。第 1、2 节只检查配置，第 3 节起实际执行研究任务。下一格打印运行模式、Python 和核心依赖版本。

### 硅流真实模型（live）

**本地 live 验证**：2026-10-19，`Qwen/Qwen3-Coder-30B-A3B-Instruct` 整本运行通过。验证对象为当前尚未提交的工作区；源码指纹、基线提交、依赖锁指纹及模型配置保存在 Notebook 的 `metadata.course_live_validation` 和本地 `artifacts/notebooks-live-ch04-complete/report.json`。本次仅补充成本与验证说明，沿用上述执行代码的 live 通过记录；代码指纹保存在该元数据中。完整 Notebook 源码指纹会因说明更新而改变，不冒充原记录对应的旧源码。运行结果不保证每次都成功，旧基线提交也不包含本章改动。

配置：真实模型统一在未提交的根目录 `.env` 中填写 `SILICONFLOW_API_KEY` 和完整 `MODEL_NAME`；公共入口不提供隐含模型默认值。API 地址、固定参数与报告字段见 [README 模型记录说明](../README.md#live-records)。随附输出仍为 offline。

范围与服务：第 1、2 节仍是配置对照，不执行模型；第 3～6 节研究实验通过 `create_model()` 切换模式；第 7 节只读取该实验结果，第 8、10～12 节始终使用脚本模型和本地教学数据做机制对照，不调用真实模型或搜索服务。live 使用真实模型和 Tavily 搜索，另需 `TAVILY_API_KEY` 与 `search` 依赖组：

```bash
uv sync --project notebooks --locked --extra search
uv run --project notebooks --locked --extra search python -m course_notebooks.run ch04-task-planning --mode live
```

live 需要网络，模型和搜索可能收费；配置错误或请求失败不会自动回退 offline。模型可能不调用 `write_todos`，不因此判定失败；实际搜索与报告仍须满足研究任务约定。

### 网络、额度与成本

- **模型调用**：live 中每轮模型请求可能消耗输入、输出 Token；工具返回资料越多，上下文通常越长。`temperature=0` 不代表零费用，也不保证工具调用轨迹完全固定。
- **搜索调用**：live 的每次 `internet_search` 都会真实请求 Tavily，消耗相应搜索额度。调用次数由实际执行决定；独立机制对照使用本地资料，不消耗搜索额度。计费方式见 [Tavily Credits & Pricing](https://docs.tavily.com/documentation/api-credits)。
- **以运行时平台为准**：模型是否可用、价格、免费额度和限流规则都可能变化。运行前查看[硅流模型广场](https://www.siliconflow.cn/models)、[硅流价格页](https://www.siliconflow.cn/pricing)及 Tavily 控制台，不把本次实测型号或历史免费额度当作长期承诺。
- **失败与上限**：认证失败、超时、限流或额度不足应记为运行未完成，排查后重试，不自动切换到 offline。`recursion_limit` 限制图执行步数，不能作为模型和搜索费用上限；单次请求与代码格超时也不等于费用预算。


```python
from course_notebooks.model_config import selected_mode
from course_notebooks.nbtools import show_runtime

show_runtime()
MODE = selected_mode()
```

    运行模式： offline （脚本模型）
    Python： 3.12.15 平台： Linux x86_64
    deepagents==0.7.22
    langchain==1.4.3
    langchain-core==1.6.6
    langgraph==1.2.13
    langchain-openai==1.6.7


## 1. 显式启用 TodoListMiddleware

**中间件**是插入 Agent 运行过程的扩展。课程当前 v0.7 默认不安装任务规划中间件，需要时显式传入
`middleware=[TodoListMiddleware()]`。

两个 Agent 分别使用独立的离线模型，只比较是否添加中间件。`create_deep_agent()` 组装运行图，
此时不会执行任务；`AIMessage` 表示模型回复，这里的文字只是未使用的占位响应。


```python
from deepagents import create_deep_agent
from langchain.agents.middleware import TodoListMiddleware
from langchain_core.messages import AIMessage
from course_notebooks.testing import ScriptedChatModel
```


```python
plain_agent = create_deep_agent(
    model=ScriptedChatModel(responses=[AIMessage(content="未执行")]),
)

planning_agent = create_deep_agent(
    model=ScriptedChatModel(responses=[AIMessage(content="未执行")]),
    middleware=[TodoListMiddleware()],
)
```

## 2. 检查工具和状态结构

`write_todos` 是模型可以请求调用的工具，`todos` 是保存任务列表的状态字段。
下一格分别检查它们是否出现在工具注册表和输出状态的 Schema 中。
**Schema** 描述状态允许包含哪些字段，不是本次任务已经产生的状态值。

`agent.nodes["tools"].bound.tools_by_name` 是课程锁定版本中的内部工具注册表，仅用于本实验观察；
`get_output_jsonschema()` 返回输出状态的结构说明。`in` 判断名称是否存在，`assert` 在条件不成立时停止执行。


```python
def has_todo_support(agent):
    tools = agent.nodes["tools"].bound.tools_by_name
    fields = agent.get_output_jsonschema().get("properties", {})
    return "write_todos" in tools, "todos" in fields


plain_support = has_todo_support(plain_agent)
planning_support = has_todo_support(planning_agent)

print("未启用：write_todos 已注册 =", plain_support[0], "；todos 字段已声明 =", plain_support[1])
print("已启用：write_todos 已注册 =", planning_support[0], "；todos 字段已声明 =", planning_support[1])

assert plain_support == (False, False), "未启用时不应包含 Todo 工具和状态字段"
assert planning_support == (True, True), "请检查是否显式传入 TodoListMiddleware()"
print("检查通过：规划中间件提供了 Todo 工具和状态结构。")
```

    未启用：write_todos 已注册 = False ；todos 字段已声明 = False
    已启用：write_todos 已注册 = True ；todos 字段已声明 = True
    检查通过：规划中间件提供了 Todo 工具和状态结构。


### 如何理解结果？

| 配置 | 规划能力的区别 |
|---|---|
| 未启用 | 模型仍可用文字拆解任务、连续调用其他工具，但没有这套内置的 Todo 工具与状态记录机制 |
| 显式启用 | 增加规划提示词、`write_todos` 工具和 `todos` 状态字段，模型可选择用它们记录和更新计划 |

应看到未启用一行为 `False / False`，已启用一行为 `True / True`。
这证明能力已配置，不证明模型已经规划。模型可能不调用 `write_todos`；中间件也不会自动执行待办或核验任务产物。
本节没有调用 `invoke()`，因此没有实际计划、工具执行记录或任务结果。

下面用独立的研究 Agent 执行一次多步骤任务，观察计划与实际搜索。

## 3. 准备多步骤研究任务

任务：分别搜索 LangGraph 和 Deep Agents，比较它们的定位，最后给出带来源的简短报告。
先观察“制定计划 → 搜索 → 更新进度 → 继续搜索 → 汇总”的联系，不重复第 2 章的工具入门和文件写入。

下面沿用[第 2 章研究助手](../ch02/02-research-assistant.ipynb)的 `internet_search` 接口和本地教学资料。
`search_log` 记录函数实际执行的搜索次数与结果数量；不是从模型回复推断。
offline 的不同查询返回同一组教学资料，只用于演示运行机制，不代表搜索相关性或实时网页内容。


```python
import os
from typing import Literal

OFFLINE_RESULTS = [
    {"title": "LangGraph overview", "url": "https://docs.langchain.com/oss/python/langgraph/overview",
     "content": "LangGraph 是用于构建、管理和部署长时间运行、有状态 Agent 的底层编排框架与运行时。", "score": 0.92},
    {"title": "langchain-ai/langgraph", "url": "https://github.com/langchain-ai/langgraph",
     "content": "LangGraph 用图描述工作流：节点执行步骤，边决定下一步，状态在步骤之间传递；支持持久化执行和人工介入。", "score": 0.87},
    {"title": "Deep Agents overview", "url": "https://docs.langchain.com/oss/python/deepagents/overview",
     "content": "Deep Agents 构建在 LangGraph 之上，预置了文件系统、子 Agent 等适合多步骤任务的能力。", "score": 0.74},
]

if MODE == "live":
    from dotenv import load_dotenv
    from tavily import TavilyClient
    from course_notebooks.model_config import repository_root

    load_dotenv(repository_root() / ".env", override=False)
    if not os.getenv("TAVILY_API_KEY"):
        raise ValueError("live 模式需要 TAVILY_API_KEY；offline 模式不需要。")
    tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """Run a web search for the given query.

    Args:
        query: The search query string.
        max_results: Maximum number of results to return.
        topic: The topic category for the search.
        include_raw_content: Whether to include raw page content.
    """
    if MODE == "offline":
        response = {"query": query, "results": OFFLINE_RESULTS[:max_results]}
    else:
        response = tavily_client.search(
            query,
            max_results=max_results,
            include_raw_content=include_raw_content,
            topic=topic,
        )
    search_log.append({"query": query, "results": len(response.get("results") or [])})
    return response


# 每次真正执行搜索都记一笔；本章研究任务约定由主 Agent 直接搜索。
search_log = []


print("搜索来源：", "本地样例（offline）" if MODE == "offline" else "Tavily API（live）")
```

    搜索来源： 本地样例（offline）


## 4. 安排计划与进度更新

`write_todos` 每项包含 `content`（任务内容）和 `status`（任务状态）。这里先用 `in_progress`（进行中）、
`pending`（待办）和 `completed`（已完成）展示进度，后续再讨论状态规则与计划调整。

脚本模型依次发出工具调用请求，框架才真正执行工具并更新状态。每次 `write_todos` 传入完整清单。
下面的计划、查询和报告都提前写好；脚本不会阅读搜索结果、推理或自动修正报告。live 模式则由真实模型决定计划内容和调用顺序。


```python
import json
from langchain_core.messages import ToolMessage
from course_notebooks.model_config import create_model
from course_notebooks.nbtools import show_text

TASK = """分别搜索 LangGraph 与 Deep Agents 的定位，比较它们的分工。
至少直接调用 internet_search 两次，不委派子 Agent。
可以使用 write_todos 制定计划和更新进度。最后给出简短比较报告，
附上至少两个不同的、本次搜索实际返回的来源 URL。"""
PLAN = ["搜索 LangGraph 定位", "搜索 Deep Agents 定位", "比较两者并整理带来源的报告"]


def todos(statuses):
    return [{"content": content, "status": status}
            for content, status in zip(PLAN, statuses)]


def tool_request(name, args, call_id):
    return AIMessage(content="", tool_calls=[{"name": name, "args": args, "id": call_id}])


REPORT = (
    "（脚本预设报告）LangGraph 是有状态 Agent 的底层编排框架与运行时；"
    "Deep Agents 构建在 LangGraph 之上，预置文件系统和子 Agent 等能力。\n"
    "来源：\n" + OFFLINE_RESULTS[0]["url"] + "\n" + OFFLINE_RESULTS[2]["url"]
)
responses = [
    tool_request("write_todos", {"todos": todos(["in_progress", "pending", "pending"])}, "plan-start"),
    tool_request("internet_search", {"query": "LangGraph overview", "max_results": 3}, "search-lg"),
    tool_request("write_todos", {"todos": todos(["completed", "in_progress", "pending"])}, "plan-next"),
    tool_request("internet_search", {"query": "Deep Agents overview", "max_results": 3}, "search-da"),
    tool_request("write_todos", {"todos": todos(["completed", "completed", "in_progress"])}, "plan-report"),
    tool_request("write_todos", {"todos": todos(["completed", "completed", "completed"])}, "plan-done"),
    AIMessage(content=REPORT),
]
research_agent = create_deep_agent(
    model=create_model(ScriptedChatModel(responses=responses)),
    tools=[internet_search],
    system_prompt=TASK,
    middleware=[TodoListMiddleware()],
)
```

## 5. 运行并观察计划和搜索

`stream(..., stream_mode="values")` 在执行过程中返回状态快照，最后一份就是运行结果。
这里只在 `todos` 改变时打印清单，再查看消息中的工具请求和工具返回。
`AIMessage.tool_calls` 保存模型请求；`ToolMessage` 保存实际返回，`tool_call_id` 对应请求的 `id`。

先清空 `search_log`，确保只核查本次运行。没有调用 Todo 时，如实显示“本次没有计划更新”，不强行补上计划。


```python
from copy import deepcopy

search_log.clear()
plan_history = []
result = None
for state in research_agent.stream(
    {"messages": [("user", TASK)]},
    config={"recursion_limit": 40}, stream_mode="values",
):
    result = state
    current = state.get("todos", [])
    if current and (not plan_history or current != plan_history[-1]):
        plan_history.append(deepcopy(current))
        print("\n计划更新", len(plan_history))
        for item in current:
            print(f"  [{item['status']}] {item['content']}")

if not plan_history:
    print("本次没有计划更新。")
for message in result["messages"]:
    if isinstance(message, AIMessage):
        for call in message.tool_calls:
            print("\n请求", call["name"], "ID:", call["id"])
            if call["name"] != "write_todos":
                show_text("参数：", json.dumps(call["args"], ensure_ascii=False))
    elif isinstance(message, ToolMessage):
        print("返回", message.name, message.status, "对应 ID:", message.tool_call_id)
print("\n实际搜索记录：", search_log)
show_text("最终报告：", result["messages"][-1].text)
```

    
    计划更新 1
      [in_progress] 搜索 LangGraph 定位
      [pending] 搜索 Deep Agents 定位
      [pending] 比较两者并整理带来源的报告
    
    计划更新 2
      [completed] 搜索 LangGraph 定位
      [in_progress] 搜索 Deep Agents 定位
      [pending] 比较两者并整理带来源的报告
    
    计划更新 3
      [completed] 搜索 LangGraph 定位
      [completed] 搜索 Deep Agents 定位
      [in_progress] 比较两者并整理带来源的报告
    
    计划更新 4
      [completed] 搜索 LangGraph 定位
      [completed] 搜索 Deep Agents 定位
      [completed] 比较两者并整理带来源的报告
    
    请求 write_todos ID: plan-start
    返回 write_todos success 对应 ID: plan-start
    
    请求 internet_search ID: search-lg
    
    参数：
    {"query": "LangGraph overview", "max_results": 3}
    返回 internet_search success 对应 ID: search-lg
    
    请求 write_todos ID: plan-next
    返回 write_todos success 对应 ID: plan-next
    
    请求 internet_search ID: search-da
    
    参数：
    {"query": "Deep Agents overview", "max_results": 3}
    返回 internet_search success 对应 ID: search-da
    
    请求 write_todos ID: plan-report
    返回 write_todos success 对应 ID: plan-report
    
    请求 write_todos ID: plan-done
    返回 write_todos success 对应 ID: plan-done
    
    实际搜索记录： [{'query': 'LangGraph overview', 'results': 3}, {'query': 'Deep Agents overview', 'results': 3}]
    
    最终报告：
    （脚本预设报告）LangGraph 是有状态 Agent 的底层编排框架与运行时；Deep Agents 构建在 LangGraph
      之上，预置文件系统和子 Agent 等能力。
    来源：
    https://docs.langchain.com/oss/python/langgraph/overview
    https://docs.langchain.com/oss/python/deepagents/overview


offline 应看到计划先指向 LangGraph 搜索，再指向 Deep Agents 搜索，最后进入报告阶段。
这些清单是本次脚本的示范，不是所有模型必须遵循的状态流转；最终 `todos` 只保留最后一版清单。

## 6. 检查实际结果

本任务约定至少直接搜索两次，并在报告中引用至少两个实际返回的来源。
下面核对成功工具结果与请求 ID、搜索返回内容及报告中的来源；Todo 若成功写入，则只比较最终状态与最后一次提交是否一致。
不要求固定计划措辞、条数、更新次数或全部 `completed`。

这些检查可以排除“只有完成声明，却没有搜索证据或来源”的情况；不证明报告结论正确或论据充分，内容仍需阅读来源核查。


```python
import re


def check_research(state, actual_searches):
    messages = state["messages"]
    calls = {call["id"]: call for message in messages if isinstance(message, AIMessage)
             for call in message.tool_calls}
    done = [message for message in messages if isinstance(message, ToolMessage)
            and message.status == "success" and message.tool_call_id in calls
            and calls[message.tool_call_id]["name"] == message.name]
    searches = [message for message in done if message.name == "internet_search"]
    assert len(searches) >= 2, "没有至少两次成功且可关联的直接搜索结果"
    assert sum(bool(entry.get("results")) for entry in actual_searches) >= 2, "搜索函数未实际取得至少两次非空结果"
    source_urls = set()
    for message in searches:
        data = json.loads(message.text)
        assert data.get("query") == calls[message.tool_call_id]["args"]["query"], "搜索返回的查询与请求不一致"
        rows = data.get("results")
        assert isinstance(rows, list) and rows, "搜索结果为空"
        assert any(entry.get("query") == data["query"] and entry.get("results") == len(rows)
                   for entry in actual_searches), "工具结果与实际搜索记录不一致"
        for row in rows:
            assert isinstance(row, dict), "搜索资料应是字典"
            assert all(isinstance(row.get(key), str) and row[key].strip()
                       for key in ("title", "url", "content")), "搜索资料缺少标题、来源或内容"
            source_urls.add(row["url"])
    final = messages[-1]
    assert isinstance(final, AIMessage) and not final.tool_calls and final.text.strip(), "缺少最终报告"
    cited = {url.rstrip(".,;:!?，。；：！？") for url in re.findall(r"https?://[^\s<>\[\]()]+", final.text)}
    assert len(cited & source_urls) >= 2, "报告没有引用至少两个实际搜索到的来源"
    assert cited <= source_urls, "报告引用了本次搜索结果之外的来源"
    plans = [calls[message.tool_call_id]["args"]["todos"]
             for message in done if message.name == "write_todos"]
    for plan in plans + [state.get("todos", [])]:
        assert isinstance(plan, list), "todos 应是列表"
        for item in plan:
            assert isinstance(item, dict) and isinstance(item.get("content"), str) and item["content"].strip()
            assert item.get("status") in {"pending", "in_progress", "completed"}, "未知 Todo 状态"
    if plans:
        assert state.get("todos") == plans[-1], "todos 与最后一次成功写入不一致"
    print("检查通过：实际搜索、工具结果关联和报告来源符合任务约定。")
    print("成功计划写入次数：", len(plans), "；未写计划不作为失败条件。")

```


```python
check_research(result, search_log)
```

    检查通过：实际搜索、工具结果关联和报告来源符合任务约定。
    成功计划写入次数： 4 ；未写计划不作为失败条件。


### 本步小结

计划记录的是模型对工作进度的声明，搜索结果和报告才是本任务要另行检查的证据。
即使清单全部标为 `completed`，搜索为空或报告缺少实际来源时，检查仍会失败。

本步不写入磁盘文件，不启动后台服务；重启内核即可清理状态。
下面先展开工具参数、返回与状态的对应关系，以及完整列表替换；计划调整与更深入的产物核查留到后续。

## 7. 对照 write_todos 请求、返回与状态

上面的进度输出展示了清单变化，现在回到同一次研究运行，查看清单从哪里来。
三处信息要分开读：

| 位置 | 内容 | 说明 |
|---|---|---|
| `AIMessage.tool_calls` 的 `args["todos"]` | 模型提交的完整列表 | 提出请求时尚未证明写入成功 |
| `ToolMessage` | 工具返回的确认文本和 `status` | 用 `tool_call_id` 与请求的 `id` 关联，同名成功结果才计入 |
| `result.get("todos", [])` | 运行结束后的当前清单 | 保存最后一版列表，不保存所有历史版本 |

下一格只收集实际成功的 `write_todos` 更新，并显示参数和确认文本；不会重新调用模型。
若模型没有调用 Todo，就打印“没有成功的 Todo 更新”，不要求它为了通过检查补写计划。


```python
def successful_todo_updates(state):
    calls = {call["id"]: call for message in state["messages"] if isinstance(message, AIMessage)
             for call in message.tool_calls}
    updates = []
    for message in state["messages"]:
        if not isinstance(message, ToolMessage) or message.name != "write_todos":
            continue
        call = calls.get(message.tool_call_id)
        if message.status == "success":
            assert call is not None and call["name"] == "write_todos", "成功结果缺少对应的 Todo 请求"
            updates.append({"id": message.tool_call_id,
                            "todos": deepcopy(call["args"]["todos"]),
                            "reply": message.text})
    return updates


todo_updates = successful_todo_updates(result)
for update in todo_updates:
    print("\n成功更新 ID：", update["id"])
    show_text("请求参数：", json.dumps({"todos": update["todos"]}, ensure_ascii=False))
    show_text("对应工具返回：", update["reply"])

show_text("最终 todos 状态：", json.dumps(result.get("todos", []), ensure_ascii=False))
if todo_updates:
    assert result.get("todos") == todo_updates[-1]["todos"], "最终状态与最后一次成功提交不一致"
    print("检查通过：最后一次成功提交的列表与最终状态一致。")
else:
    print("没有成功的 Todo 更新；不据此判定研究失败。")
```

    
    成功更新 ID： plan-start
    
    请求参数：
    {"todos": [{"content": "搜索 LangGraph 定位", "status": "in_progress"},
      {"content": "搜索 Deep Agents 定位", "status": "pending"}, {"content":
      "比较两者并整理带来源的报告", "status": "pending"}]}
    
    对应工具返回：
    Updated todo list to [{'content': '搜索 LangGraph 定位', 'status':
      'in_progress'}, {'content': '搜索 Deep Agents 定位', 'status': 'pending'},
      {'content': '比较两者并整理带来源的报告', 'status': 'pending'}]
    
    成功更新 ID： plan-next
    
    请求参数：
    {"todos": [{"content": "搜索 LangGraph 定位", "status": "completed"},
      {"content": "搜索 Deep Agents 定位", "status": "in_progress"}, {"content":
      "比较两者并整理带来源的报告", "status": "pending"}]}
    
    对应工具返回：
    Updated todo list to [{'content': '搜索 LangGraph 定位', 'status': 'completed'},
      {'content': '搜索 Deep Agents 定位', 'status': 'in_progress'}, {'content':
      '比较两者并整理带来源的报告', 'status': 'pending'}]
    
    成功更新 ID： plan-report
    
    请求参数：
    {"todos": [{"content": "搜索 LangGraph 定位", "status": "completed"},
      {"content": "搜索 Deep Agents 定位", "status": "completed"}, {"content":
      "比较两者并整理带来源的报告", "status": "in_progress"}]}
    
    对应工具返回：
    Updated todo list to [{'content': '搜索 LangGraph 定位', 'status': 'completed'},
      {'content': '搜索 Deep Agents 定位', 'status': 'completed'}, {'content':
      '比较两者并整理带来源的报告', 'status': 'in_progress'}]
    
    成功更新 ID： plan-done
    
    请求参数：
    {"todos": [{"content": "搜索 LangGraph 定位", "status": "completed"},
      {"content": "搜索 Deep Agents 定位", "status": "completed"}, {"content":
      "比较两者并整理带来源的报告", "status": "completed"}]}
    
    对应工具返回：
    Updated todo list to [{'content': '搜索 LangGraph 定位', 'status': 'completed'},
      {'content': '搜索 Deep Agents 定位', 'status': 'completed'}, {'content':
      '比较两者并整理带来源的报告', 'status': 'completed'}]
    
    最终 todos 状态：
    [{"content": "搜索 LangGraph 定位", "status": "completed"}, {"content": "搜索 Deep
      Agents 定位", "status": "completed"}, {"content": "比较两者并整理带来源的报告", "status":
      "completed"}]
    检查通过：最后一次成功提交的列表与最终状态一致。


### 如何理解对应关系？

offline 的请求 ID 如 `plan-start`、`plan-next`，可与第 5 节的返回逐一对应；live 的 ID 和清单内容可能不同。
确认文本说明工具返回了，但最新清单要读取 `todos`。前面的版本保存在消息和 `plan_history` 中，不会自动累积进最终状态。

这里检查的是**工具写入与状态是否一致**，不是任务产物是否完成。即使最后一版仍有待办，只要写入成功且状态一致，这项机制检查也可以通过。

## 8. 新列表会替换旧列表，不是追加或按项合并

如果原清单有三项，只传入其中一项，最终 `todos` 就只剩这一项。
要保留其他任务，应提交包含它们的完整列表。任务没有独立的自动合并 ID，不能把 `content` 当作会自动匹配的更新键。

下面是独立的机制实验，**在 offline/live 下都只使用脚本模型**，无搜索或真实模型请求。
先真实写入三项，再提交第二版；从每次成功返回后的状态快照读取清单，核对“完整请求列表 → 实际工具返回 → 状态替换”。
响应列表依次给出两次写入和结束消息，不直接构造最终 Agent 状态；每个对照创建新模型和新 Agent，避免响应游标或旧状态相互影响。


```python
def observe_replacement(second_plan):
    agent = create_deep_agent(
        model=ScriptedChatModel(responses=[
            tool_request("write_todos", {"todos": todos(["in_progress", "pending", "pending"])}, "replace-first"),
            tool_request("write_todos", {"todos": second_plan}, "replace-second"),
            AIMessage(content="清单写入结束；尚未执行搜索或完成研究。"),
        ]),
        middleware=[TodoListMiddleware()],
    )
    snapshots = {}
    final_state = None
    for state in agent.stream({"messages": [("user", "依次写入两版清单，不执行研究任务。")]},
                              stream_mode="values", config={"recursion_limit": 12}):
        final_state = state
        latest = state["messages"][-1]
        if isinstance(latest, ToolMessage) and latest.name == "write_todos" and latest.status == "success":
            snapshots[latest.tool_call_id] = deepcopy(state.get("todos", []))
    updates = successful_todo_updates(final_state)
    assert len(updates) == 2, "固定机制实验应真实完成两次写入"
    assert set(snapshots) == {update["id"] for update in updates}, "缺少成功写入后的快照"
    for update in updates:
        assert snapshots[update["id"]] == update["todos"], "成功返回后的状态与提交列表不一致"
    return final_state, snapshots


# 只提交一项：其他两项不会自动保留。
partial_plan = [{"content": PLAN[1], "status": "in_progress"}]
partial_state, partial_snapshots = observe_replacement(partial_plan)
show_text("首次实际写入：", json.dumps(partial_snapshots["replace-first"], ensure_ascii=False))
show_text("只提交一项后的状态：", json.dumps(partial_state["todos"], ensure_ascii=False))
assert partial_state["todos"] == partial_plan

# 提交完整清单：保留三项，并更新其中的进度。
full_plan = todos(["completed", "in_progress", "pending"])
full_state, full_snapshots = observe_replacement(full_plan)
show_text("提交完整列表后的状态：", json.dumps(full_state["todos"], ensure_ascii=False))
assert full_state["todos"] == full_plan
print("检查通过：新列表整体替换旧列表；保留其他任务需要提交完整清单。")
```

    
    首次实际写入：
    [{"content": "搜索 LangGraph 定位", "status": "in_progress"}, {"content": "搜索
      Deep Agents 定位", "status": "pending"}, {"content": "比较两者并整理带来源的报告",
      "status": "pending"}]
    
    只提交一项后的状态：
    [{"content": "搜索 Deep Agents 定位", "status": "in_progress"}]


    
    提交完整列表后的状态：
    [{"content": "搜索 LangGraph 定位", "status": "completed"}, {"content": "搜索 Deep
      Agents 定位", "status": "in_progress"}, {"content": "比较两者并整理带来源的报告",
      "status": "pending"}]
    检查通过：新列表整体替换旧列表；保留其他任务需要提交完整清单。


### 本步小结

第 7 节读取研究实验的真实调用；第 8 节独立验证列表替换，没有进行研究或产物验收。
“必须两次写入”的断言仅用于这个固定的机制对照，不要求真实模型一定写计划或按固定次数更新。

清单中被省略的任务只是从当前状态消失，不等于任务已完成；历史仍可在本次消息记录中找到。
本步所有数据只在内核内存中，重启即可清理。下面再解释三种状态的使用和何时需要调整计划。

## 9. 三种状态表示什么？

`status` 是模型通过 `write_todos` 写下的进度声明。与第 2 章保持一致：

| 状态 | 含义 | 使用时机 | 核查时注意 |
|---|---|---|---|
| `pending` | 待办 | 已列入计划，尚未开始；也可因依赖未满足而暂缓 | 不是工具已经排队，框架不会自动执行 |
| `in_progress` | 进行中 | 正在处理，或处理过程中遇到需要解决的阻碍 | 不代表一定有后台任务运行，需查看实际调用 |
| `completed` | 已完成 | 模型认为该项已完成 | 仍应核对搜索资料、报告或其他产物 |

正常使用时，应在开始工作时标为进行中，取得足够证据后再标为完成。彼此独立的任务可以同时进行，不必为了清单整齐而机械地串行执行。
内置提示会建议这些用法，但 `TodoListMiddleware` 不会核验业务产物，也不把任务状态强制限制成“待办 → 进行中 → 已完成”的完整流转。

### 什么时候调整计划？

| 实际情况 | 可采用的调整 |
|---|---|
| 已有摘要只讲定位，没有回答两者关系 | 增加核查项，暂缓依赖该证据的报告任务 |
| 搜索无结果或来源互相矛盾 | 保留未完成状态，补充搜索或交叉核查步骤 |
| 用户缩小研究范围 | 删除不再相关的待办，并说明范围变化；不要将被删项当作完成 |
| 已完成事项之后出现新问题 | 保留原完成记录，新增后续核查项，说明新证据带来的问题 |

调整应有理由，并提交完整清单来保留仍相关的任务。下面只演示第一种情况，不把某套计划措辞或完整流转当成真实模型必须遵循的答案。

## 10. 发现资料缺口后补充核查任务

延续前面的比较研究，但本小实验只检查两份固定教学笔记，不重新搜索、不验证整份研究是否完成。
笔记包含两者的定位摘要，却没有单独记录“依赖关系”的核查结果；检查工具按这个明确的数据约定返回缺项。
它不是用关键词判断事实，也不声称网页没有说明关系。

脚本先写入初始计划，再请求工具读取笔记。取得缺项结果后，提交包含新核查项的完整计划，将报告继续保留为待办。
末尾停在“需要补查”，不假装已经完成新增工作。这里脚本顺序和修订计划都提前安排好，框架、检查工具和状态更新仍真实执行；不证明模型能自主发现缺口或重新规划。

本节在 offline/live 下都使用脚本模型，不读取供应商配置，不产生额外模型或 Tavily 请求。


```python
# 固定笔记有定位摘要，但没有 relationship 字段，表示尚未记录关系核查结果。
research_notes = {
    "summaries": [
        {"title": "LangGraph", "content": OFFLINE_RESULTS[0]["content"]},
        {"title": "Deep Agents", "content": "预置文件系统与子 Agent 等能力的 Agent Harness。"},
    ],
}
note_checks = []


def inspect_research_notes() -> dict:
    """读取教学笔记，检查是否已记录两者依赖关系的核查结果。"""
    evidence = {
        "summaries": deepcopy(research_notes["summaries"]),
        "missing": [] if research_notes.get("relationship") else ["尚未记录两者依赖关系的核查结果"],
    }
    note_checks.append(deepcopy(evidence))
    return evidence


initial_plan = [
    {"content": "整理两者定位摘要", "status": "in_progress"},
    {"content": "比较两者分工", "status": "pending"},
    {"content": "撰写带来源的报告", "status": "pending"},
]
revised_plan = [
    {"content": "整理两者定位摘要", "status": "completed"},
    {"content": "补充核查两者依赖关系", "status": "in_progress"},
    {"content": "比较两者分工", "status": "pending"},
    {"content": "撰写带来源的报告", "status": "pending"},
]
adjustment_agent = create_deep_agent(
    model=ScriptedChatModel(responses=[
        tool_request("write_todos", {"todos": initial_plan}, "adjust-initial"),
        tool_request("inspect_research_notes", {}, "adjust-inspect"),
        tool_request("write_todos", {"todos": revised_plan}, "adjust-revised"),
        AIMessage(content="定位摘要已取得，但关系核查结果缺失。已增加核查项，报告尚待完成。"),
    ]),
    tools=[inspect_research_notes],
    middleware=[TodoListMiddleware()],
)
```


```python
note_checks.clear()
adjustment_snapshots = {}
adjustment_result = None
for state in adjustment_agent.stream(
    {"messages": [("user", "读取已有笔记，遇到缺项时补充核查计划，暂不撰写报告。注重如实记录未完成项。") ]},
    config={"recursion_limit": 16}, stream_mode="values",
):
    adjustment_result = state
    latest = state["messages"][-1]
    if isinstance(latest, ToolMessage) and latest.status == "success":
        print("\n成功工具：", latest.name, "；对应请求 ID：", latest.tool_call_id)
        if latest.name == "write_todos":
            adjustment_snapshots[latest.tool_call_id] = deepcopy(state.get("todos", []))
            for item in state.get("todos", []):
                print(f"  [{item['status']}] {item['content']}")
        elif latest.name == "inspect_research_notes":
            show_text("实际检查结果：", latest.text)

updates = successful_todo_updates(adjustment_result)
for update in updates:
    assert adjustment_snapshots[update["id"]] == update["todos"], "计划写入与实际状态不一致"

# 以下断言针对固定教学数据和脚本，不要求真实模型产生同一份修订计划。
inspection_calls = {call["id"]: call for message in adjustment_result["messages"]
                    if isinstance(message, AIMessage) for call in message.tool_calls
                    if call["name"] == "inspect_research_notes"}
inspection_replies = [message for message in adjustment_result["messages"]
                      if isinstance(message, ToolMessage) and message.name == "inspect_research_notes"
                      and message.status == "success" and message.tool_call_id in inspection_calls]
assert len(note_checks) == len(inspection_replies) == 1, "未取得实际笔记检查结果"
assert json.loads(inspection_replies[0].text) == note_checks[0]
assert note_checks[0]["missing"], "固定笔记应缺少关系核查记录"
assert adjustment_snapshots["adjust-initial"] == initial_plan
assert adjustment_result["todos"] == revised_plan
assert {item["content"] for item in initial_plan} < {item["content"] for item in revised_plan}
assert any(item["status"] != "completed" for item in adjustment_result["todos"])
show_text("当前说明：", adjustment_result["messages"][-1].text)
print("检查通过：工具返回了缺项证据，新计划保留原任务并补充核查项；研究仍未完成。")
```

    
    成功工具： write_todos ；对应请求 ID： adjust-initial
      [in_progress] 整理两者定位摘要
      [pending] 比较两者分工
      [pending] 撰写带来源的报告
    
    成功工具： inspect_research_notes ；对应请求 ID： adjust-inspect
    
    实际检查结果：
    {"summaries": [{"title": "LangGraph", "content": "LangGraph
      是用于构建、管理和部署长时间运行、有状态 Agent 的底层编排框架与运行时。"}, {"title": "Deep Agents",
      "content": "预置文件系统与子 Agent 等能力的 Agent Harness。"}], "missing":
      ["尚未记录两者依赖关系的核查结果"]}
    
    成功工具： write_todos ；对应请求 ID： adjust-revised
      [completed] 整理两者定位摘要
      [in_progress] 补充核查两者依赖关系
      [pending] 比较两者分工
      [pending] 撰写带来源的报告
    
    当前说明：
    定位摘要已取得，但关系核查结果缺失。已增加核查项，报告尚待完成。
    检查通过：工具返回了缺项证据，新计划保留原任务并补充核查项；研究仍未完成。


### 如何理解这次调整？

首次清单只有整理、比较和报告三项。检查工具实际返回了两份定位摘要及缺项说明；修订清单保留这三项，同时增加关系核查。
整理摘要被标为已完成，新核查项正在进行，比较和报告仍是待办。这里只完成了计划修订，没有执行补充核查或生成研究报告。

这不是用新增条目数衡量规划质量。真实任务也可能拆分、合并或删除待办；应根据证据和用户需求解释原因，并另行核查产物。
所有笔记、执行记录和计划都在内存中，重启内核即可清理。下面单独对照“标为 completed”与“产物核查通过”。

## 11. 全部 completed，产物就完成了吗？

不一定。用相同的研究任务和第 6 节核查器，分别控制“是否搜索”“搜索是否有资料”“报告是否引用实际来源”。
这里重新建立 Agent，真实执行工具和更新状态；没有把手写的最终状态当作执行证据。

下面的 `run_controlled_research()` 在所有模式下都使用脚本模型和本地搜索资料，不调用 Tavily。
传入 `plan` 决定是否写计划，`empty_results` 控制搜索为空，`report` 控制最终文本。
故意先将清单写成 `completed`，然后再执行或跳过搜索，用来说明中间件不会检查这个完成声明是否真实。


```python
def run_controlled_research(*, plan=None, run_searches=True, empty_results=False, report=REPORT):
    executions = []

    def internet_search(query: str, max_results: int = 5,
                        topic: Literal["general", "news", "finance"] = "general",
                        include_raw_content: bool = False):
        """读取本地教学搜索资料，用于独立对照，不联网。"""
        response = {"query": query, "results": [] if empty_results else deepcopy(OFFLINE_RESULTS[:max_results])}
        executions.append({"query": query, "results": len(response["results"])})
        return response

    steps = []
    if plan is not None:
        steps.append(tool_request("write_todos", {"todos": plan}, "control-plan"))
    if run_searches:
        steps.extend([
            tool_request("internet_search", {"query": "LangGraph overview", "max_results": 3}, "control-lg"),
            tool_request("internet_search", {"query": "Deep Agents overview", "max_results": 3}, "control-da"),
        ])
    steps.append(AIMessage(content=report))
    agent = create_deep_agent(
        model=ScriptedChatModel(responses=steps), tools=[internet_search],
        middleware=[TodoListMiddleware()],
    )
    state = agent.invoke({"messages": [("user", TASK)]}, config={"recursion_limit": 20})
    return state, executions


def show_delivery_check(label, state, executions):
    print("\n场景：", label)
    all_completed = bool(state.get("todos")) and all(item["status"] == "completed" for item in state["todos"])
    print("Todo 全部 completed：", all_completed)
    try:
        check_research(state, executions)
    except AssertionError as error:
        print("产物未通过：", error)
        return False
    return True
```


```python
completed_plan = todos(["completed", "completed", "completed"])
delivery_cases = [
    ("只声明完成，没有搜索", {"run_searches": False}, False),
    ("声明完成，但搜索结果为空", {"empty_results": True}, False),
    ("声明完成，但报告没有来源", {"report": "研究已完成，结果见我的总结。"}, False),
    ("声明完成，且搜索与报告来源均有证据", {}, True),
]
for label, options, expected in delivery_cases:
    case_state, case_searches = run_controlled_research(plan=completed_plan, **options)
    assert case_state["todos"] == completed_plan, "机制对照应实际写入相同完成声明"
    passed = show_delivery_check(label, case_state, case_searches)
    assert passed == expected, "核查器未按实际产物区分成功与失败"
```

    
    场景： 只声明完成，没有搜索
    Todo 全部 completed： True
    产物未通过： 没有至少两次成功且可关联的直接搜索结果


    
    场景： 声明完成，但搜索结果为空
    Todo 全部 completed： True
    产物未通过： 搜索函数未实际取得至少两次非空结果


    
    场景： 声明完成，但报告没有来源
    Todo 全部 completed： True
    产物未通过： 报告没有引用至少两个实际搜索到的来源


    
    场景： 声明完成，且搜索与报告来源均有证据
    Todo 全部 completed： True
    检查通过：实际搜索、工具结果关联和报告来源符合任务约定。
    成功计划写入次数： 1 ；未写计划不作为失败条件。


前三个场景的预期失败被捕获并打印，不会中断整本实验；第四个场景必须通过。
四份清单的完成状态相同，核查结论却不同，说明 `completed` 不能作为验收证据。
核查范围仍是工具结果关联、资料结构与报告来源，不包括结论准确性、来源独立性或论据充分性。

## 12. 没有 Todo，或 Todo 没有全完成，核查应怎样处理？

第一个对照启用了 `TodoListMiddleware()`，但脚本不请求 `write_todos`，仍搜索两次并提交同样的报告。
第二个对照保留一份不同措辞、不同条数且尚未完成的计划，搜索与报告则满足同样约定。

两者都应通过产物检查。Todo 状态可能落后于实际工作，此时可以提醒模型更新；不能仅凭清单状态否定已经验证的产物。
真实模型是否写 Todo、写多少项和如何更新都不固定，验证应关注已经承诺的结构与行为。


```python
no_todo_state, no_todo_searches = run_controlled_research()
assert not successful_todo_updates(no_todo_state)
assert not no_todo_state.get("todos")
assert show_delivery_check("没有调用 write_todos，但产物符合约定", no_todo_state, no_todo_searches)

alternative_plan = [{"content": "继续人工核查比较报告", "status": "in_progress"}]
unfinished_state, unfinished_searches = run_controlled_research(plan=alternative_plan)
assert unfinished_state["todos"] == alternative_plan
assert show_delivery_check("计划未全部 completed，但产物符合约定", unfinished_state, unfinished_searches)
```

    
    场景： 没有调用 write_todos，但产物符合约定
    Todo 全部 completed： False
    检查通过：实际搜索、工具结果关联和报告来源符合任务约定。
    成功计划写入次数： 0 ；未写计划不作为失败条件。


    
    场景： 计划未全部 completed，但产物符合约定
    Todo 全部 completed： False
    检查通过：实际搜索、工具结果关联和报告来源符合任务约定。
    成功计划写入次数： 1 ；未写计划不作为失败条件。


## 小结与排错

- `TodoListMiddleware()` 提供规划提示、`write_todos` 和 `todos` 状态；模型仍可以不使用规划工具。
- 每次写入完整列表，新列表替换旧列表；通过请求 ID、工具成功状态和实际状态核对写入。
- 三种任务状态是进度声明；新增核查、保留未完成项或删除无关待办，都应说明理由。
- 验收依据实际资料与报告，不依据计划措辞、条数、完整流转或是否全部 `completed`。

| 现象 | 检查位置 |
|---|---|
| 找不到 course_notebooks | 安装项目依赖，并选择正确的 Python 3.12 内核 |
| live 缺少 MODEL_NAME 或 TAVILY_API_KEY | 检查根目录未提交的 .env；模型名必须使用 MODEL_NAME |
| 没有 Todo 调用 | 先看工具是否注册；模型本次可能没有选择使用，不单独算失败 |
| 搜索或来源断言失败 | 查看实际 ToolMessage、search_log 和最终报告；不能用 completed 绕过 |
| 网络超时、限流或额度不足 | 记录运行未完成，排查服务后重试；不改称验证通过 |

本 Notebook 不启动后台服务、不写磁盘研究文件，变量与状态均在内存中；重启内核即可清理。
live 研究请求可能产生费用；独立机制对照始终使用本地数据。
继续阅读[第 5 章：子 Agent 委派](../ch05/01-subagent-delegation.ipynb)，理解任务如何委派以及消息上下文与共享状态的区别。
