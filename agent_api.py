from agent import stream
from fastapi import FastAPI, Request, HTTPException
from sse_starlette.sse import EventSourceResponse
from langmem import create_manage_memory_tool, create_search_memory_tool
from mcp_client import mcp_client
from config import settings

app = FastAPI(title="KGraph Agent",
              description="An agent for querying using KGraph",
              version=settings.APP_VERSION)


@app.post("/agent")
async def query_kgrag(request: Request):
    try:
        data = await request.json()
        user_input = data.get("query")
        tools = await mcp_client.get_tools()
        tools.extend([
            create_manage_memory_tool(namespace=("memories",)),
            create_search_memory_tool(namespace=("memories",))
        ])
        if not user_input:
            raise HTTPException(
                status_code=400,
                detail="Query parameter 'query' is required."
            )
        return EventSourceResponse(stream(prompt=user_input, tools=tools))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
