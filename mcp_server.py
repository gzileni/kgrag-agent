import uuid
from mcp.server.fastmcp import FastMCP
from arxiv_export_documents import export_papers
from config import settings
from krag import (
    MemoryStoreRetriever,
    PARSER_PROMPT,
    AGENT_PROMPT,
    stream
)

model_embedding_url: str | None = None
llm_model_url: str | None = None
if settings.LLM_MODEL_TYPE == "ollama" and settings.LLM_URL is not None:
    model_embedding_url = f"{settings.LLM_URL}/api/embeddings"
    llm_model_url = settings.LLM_URL

grag_ingestion = MemoryStoreRetriever(
    path_type="fs",
    path_download=settings.PATH_DOWNLOAD,
    format_file="pdf",
    collection_name=settings.COLLECTION_NAME,
    llm_model=settings.LLM_MODEL_NAME,
    llm_type=settings.LLM_MODEL_TYPE,
    llm_model_url=llm_model_url,
    model_embedding_type=settings.LLM_MODEL_TYPE,
    model_embedding_name=settings.MODEL_EMBEDDING,
    model_embedding_url=model_embedding_url,
    model_embedding_vs_name=settings.VECTORDB_SENTENCE_MODEL,
    model_embedding_vs_type=settings.VECTORDB_SENTENCE_TYPE,
    model_embedding_vs_path=settings.VECTORDB_SENTENCE_PATH,
    neo4j_url=settings.NEO4J_URL,
    neo4j_username=settings.NEO4J_USERNAME,
    neo4j_password=settings.NEO4J_PASSWORD,
    neo4j_db_name=settings.NEO4J_DB_NAME,
    qdrant_url=settings.QDRANT_URL,
    redis_host=settings.REDIS_HOST,
    redis_port=settings.REDIS_PORT,
    redis_db=settings.REDIS_DB
)

# Initialize FastMCP server
mcp = FastMCP("KGraph")


@mcp.tool(
    name="ingestion_document_tool",
    description="Ingest a document into the KGraph system."
)
async def ingestion_document_tool(path_file: str):
    """
    Ingest a document into the KGraph system.
    Args:
        path_file (str): Path to the document file to be ingested.
    """
    async for d in grag_ingestion.process_documents(path=path_file):
        return f"Document {d} ingested successfully."


@mcp.tool(
    name="arxiv_ingestion_tool",
    description="Ingest a document from Arxiv based on a search query."
)
async def arxiv_ingestion_tool(
    search_query: str,
    max_results: int = 5,
    thread_id: str = str(uuid.uuid4())
):
    """
    Ingest a document from Arxiv based on a search query.
    Args:
        query (str): Search query for Arxiv.
    """
    papers = []
    async for paper in export_papers(
        search=search_query,
        path_download=settings.PATH_DOWNLOAD,
        max_results=max_results
    ):
        async for d in grag_ingestion.process_documents(
            documents=paper.documents,
        ):
            if d == "ERROR":
                return "Error ingesting document."
            papers.append(d)
            return f"Document {d} ingested successfully."

    async for event_response in stream(
        thread_id=thread_id,
        prompt=search_query
    ):
        return event_response

    if len(papers) > 0:
        for paper in papers:
            msg: str = (
                f"Title: {paper.title},\n "
                f"Authors: {', '.join(paper.authors)}\n"
                f"Published: {paper.published},\n "
                f"Link: {paper.link}\n"
            )
            return msg


@mcp.prompt(title="Parser Text Prompt")
def parser_text_prompt(text: str) -> str:
    """
    Generate a prompt for extracting relationships from text.
    Args:
        text (str): The input text to extract relationships from.
    Returns:
        str: The formatted prompt for the relationship extractor.
    """
    return PARSER_PROMPT


@mcp.prompt(title="Agent Query Prompt")
def agent_query_prompt(nodes_str: str, edges_str: str, user_query: str) -> str:
    """
    Generate a prompt for the agent to answer a user query
    using the knowledge graph.
    Args:
        nodes_str (str): String representation of nodes in the graph.
        edges_str (str): String representation of edges in the graph.
        user_query (str): The user's query to be answered.
    Returns:
        str: The formatted prompt for the agent.
    """
    return AGENT_PROMPT.format(
        nodes_str=nodes_str,
        edges_str=edges_str,
        user_query=user_query
    )


def main():
    """Entry point for the direct execution server."""
    mcp.run(transport='sse')


if __name__ == "__main__":
    main()
