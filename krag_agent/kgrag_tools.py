from langchain_core.tools import tool
from .kgrag_ingestion import grag_ingestion


@tool(
    "graph_rag_tool",
    description="Graph RAG tool that queries the graph memory store."
)
async def graph_rag_tool(prompt: str) -> str:
    """
    Graph RAG tool that queries the graph memory store.
    Args:
        prompt (str): The input prompt to query the graph memory store.
        Returns:
            str: The response from the graph memory store based
            on the input prompt.

    Raises:
        Exception: Propagates any exceptions raised during the query.

    Note:
        This function sends the prompt to the graph memory store
        and awaits the response.
    """
    return await grag_ingestion.query(query=prompt)
