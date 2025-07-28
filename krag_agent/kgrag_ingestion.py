from .kgrag_retrievers import MemoryStoreRetriever
from .kgrag_config import settings

grag_ingestion = MemoryStoreRetriever(
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    s3_bucket=settings.AWS_BUCKET_NAME,
    aws_region=settings.AWS_REGION,
    path_type="s3",
    path_download=settings.PATH_DOWNLOAD,
    format_file="pdf",
    collection_name=settings.COLLECTION_NAME,
    llm_model=settings.LLM_MODEL_NAME,
    llm_type=settings.LLM_MODEL_TYPE,
    neo4j_url=settings.NEO4J_URL,
    neo4j_username=settings.NEO4J_USERNAME,
    neo4j_password=settings.NEO4J_PASSWORD,
    neo4j_db_name=settings.NEO4J_DB_NAME,
    qdrant_url=settings.QDRANT_URL,
    redis_host=settings.REDIS_HOST,
    redis_port=settings.REDIS_PORT,
    redis_db=settings.REDIS_DB
)
