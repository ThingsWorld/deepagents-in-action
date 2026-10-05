"""A deliberately slow graph so background execution is observable."""

import asyncio

from langgraph.graph import END, START, MessagesState, StateGraph


async def research(state: MessagesState):
    request = next(
        (message.content for message in reversed(state["messages"]) if message.type == "human"),
        "",
    )
    await asyncio.sleep(8)
    return {"messages": [{"role": "ai", "content": f"Research completed: {request}"}]}


builder = StateGraph(MessagesState)
builder.add_node("research", research)
builder.add_edge(START, "research")
builder.add_edge("research", END)
graph = builder.compile()
