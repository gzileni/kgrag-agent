from agent import stream
from fastapi import FastAPI, Request, HTTPException
from sse_starlette.sse import EventSourceResponse
from arxiv import arxiv_mcp_client
from langmem import create_manage_memory_tool, create_search_memory_tool
from krag import kgrag_mcp_client

app = FastAPI(title="KGraph Arxiv Agent",
              description="An agent for querying Arxiv using KGraph",
              version="0.1.0")


@app.post("/kgrag")
async def query_kgrag(request: Request):
    try:
        data = await request.json()
        user_input = data.get("query")
        tools = await kgrag_mcp_client.get_tools()
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


@app.post("/papers")
async def query_arxiv(request: Request):
    try:
        data = await request.json()
        user_input = data.get("query")
        tools = await arxiv_mcp_client.get_tools()
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
