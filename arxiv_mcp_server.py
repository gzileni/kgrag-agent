import uuid
from mcp.server.fastmcp import FastMCP
from arxiv_export_documents import export_papers
from krag import (
    kgrag,
    settings
)
from starlette.applications import Starlette
from starlette.routing import Mount
from typing import Any

# Initialize FastMCP server
mcp = FastMCP("Arxiv KGraph")


@mcp.tool(
    name="arxiv_query",
    description="Ingest a document from Arxiv based on a search query."
)
async def arxiv_query(
    search_query: str,
    max_results: int = 1,
    thread_id: str = str(uuid.uuid4())
):
    """
    Ingest a document from Arxiv based on a search query.
    Args:
        query (str): Search query for Arxiv.
    """
    #papers: list[Any] = []
    #async for paper in _export_arxiv_papers(search_query, max_results):
    #    papers.append(paper)

    response = await kgrag.query(search_query)
    return {
        "jsonrpc": "2.0",
        "result": {
            "message": str(response),
            #"papers": (
            #    papers[-1] if len(papers) > 0 else ["No papers found."]
            #)
        },
        "id": thread_id
    }


async def _export_arxiv_papers(search_query, max_results):
    """
    Export documents from Arxiv based on a search query.
    Args:
        search_query (str): Search query for Arxiv.
        max_results (int): Maximum number of results to return.
    Returns:
        list: List of ArxivPaper objects.
    """
    papers = []
    async for paper in export_papers(
        search=search_query,
        path_download=settings.PATH_DOWNLOAD,
        max_results=max_results
    ):
        if not paper.is_exist:
            async for d in kgrag.process_documents(
                documents=paper.documents,
            ):
                if d == "ERROR":
                    yield "Error ingesting document."
                else:
                    yield d
        papers.append(paper)

    papers_list: list[str] = []
    if len(papers) > 0:
        for paper in papers:
            msg: str = (
                f"Title: {paper.title},\n "
                f"Authors: {', '.join(paper.authors)}\n"
                f"Link: {paper.link}\n"
            )
            papers_list.append(msg)

    yield papers_list


# Mount the SSE server to the existing ASGI server
app = Starlette(
    routes=[
        Mount('/', app=mcp.sse_app()),
    ]
)
