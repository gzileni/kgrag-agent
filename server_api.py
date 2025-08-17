from agent import KGragAgent
from fastapi import FastAPI, Request, HTTPException
from sse_starlette.sse import EventSourceResponse
from config import settings

app = FastAPI(title="KGraph Agent",
              description="An agent for querying using KGraph",
              version=settings.APP_VERSION)


@app.post("/agent")
async def query_kgrag(request: Request):
    try:
        agent = KGragAgent()
        data = await request.json()
        user_input = data.get("user_input")

        if not user_input:
            raise HTTPException(
                status_code=400,
                detail="Query parameter 'query' is required."
            )
        return EventSourceResponse(agent.stream(prompt=user_input))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
