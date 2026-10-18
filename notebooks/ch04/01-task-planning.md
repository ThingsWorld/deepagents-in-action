> 本次执行模式：**offline**。源码指纹：`e0dff3975113`。

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

**当前范围**：已实现第 1 项，其余实验后续逐步添加。

**预期现象**（offline）：未启用时，`write_todos` 未注册、`todos` 字段未声明；显式启用后，两项均存在，检查格打印“检查通过”。本阶段不执行任务，不产生实际计划或报告。

## 运行环境与运行模式

使用课程锁定的 Python 3.12 环境，安装与内核选择见 [Notebook 索引](../README.md)。默认 offline 模式在仓库根目录执行：

```bash
uv sync --project notebooks --locked
uv run --project notebooks --locked python -m course_notebooks.run ch04-task-planning
```

| 模式 | 模型 | 工具执行 | 需要的 Key 与依赖 |
|---|---|---|---|
| offline（默认，随附输出） | 脚本模型，仅用于组装 Agent，不执行预设回复 | 只检查工具注册与状态结构，不执行工具 | 无 Key；使用课程基础依赖 |
| live（尚未接入） | 当前对照实验仍使用脚本模型 | 尚无真实模型驱动的工具调用 | 当前实验无需配置；后续按实际实验补充 |

当前实验无需联网。它验证规划能力是否已配置，不证明模型会使用规划工具，也不验证任务完成情况。下一格打印运行模式、Python 和核心依赖版本，便于核对环境。

### 硅流真实模型（live）

**待验证**：当前版本尚无整本 live 通过记录，暂不列出已验证型号。

配置：真实模型统一在未提交的根目录 `.env` 中填写 `SILICONFLOW_API_KEY` 和完整 `MODEL_NAME`；公共入口不提供隐含模型默认值。API 地址、固定参数与报告字段见 [README 模型记录说明](../README.md#live-records)。随附输出仍为 offline。

范围与服务：当前仅完成配置对照，直接使用 `ScriptedChatModel`，尚未通过 `create_model()` 接入真实模型；添加 `--mode live` 不会使本节调用真实模型。暂用默认 offline，后续加入实际执行流程时再补充 live 命令、服务要求和验证记录。


```python
from course_notebooks.nbtools import show_runtime

show_runtime()
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

本节没有创建文件或后台服务，重启内核即可清理变量。
后续再添加 `write_todos` 的实际调用、状态含义和产物核查。
