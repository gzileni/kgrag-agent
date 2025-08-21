from a2a.types import (
    AgentCard,
    AgentSkill,
    AgentCapabilities
)
from agent import KGragAgent


capabilities = AgentCapabilities(
    streaming=True,
    push_notifications=True
)


skills = [
    AgentSkill(
        id='query_kgraph',
        name='Structured Data Query',
        description=(
            'Query the KGraph system with a specific query string.'
        ),
        tags=['query', 'kgraph'],
        examples=['What are the key points in the risk report for 2023?']
    ),
    AgentSkill(
        id='ingestion_data',
        name='Ingestion Data',
        description=(
            'Ingest a path of file into the KGraph system.'
        ),
        tags=['ingestion', 'kgraph'],
        examples=['/home/user/documents/report.pdf']
    )
]


def create_agent_card(
    host: str,
    port: int,
    version: str = '1.0.0'
) -> AgentCard:
    """
    Create an agent card for the KnowledgeGraph AI Agent.
    """
    return AgentCard(
        name='KnowledgeGraph AI Agent',
        description=(
            'Agent for ingesting and querying structured and unstructured '
            'content. Accepts PDF, CSV, JSON, and TXT files, extracts text '
            'and metadata, normalizes the content, and imports it into a '
            'semantic graph to enable complex queries over informational '
            'links.'
        ),
        url=f'http://{host}:{port}/',
        version=version,
        default_input_modes=KGragAgent.SUPPORTED_CONTENT_TYPES,
        default_output_modes=KGragAgent.SUPPORTED_CONTENT_TYPES,
        capabilities=capabilities,
        skills=skills,
    )
