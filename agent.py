import json
import uuid
from langgraph.prebuilt import create_react_agent
from langchain_core.runnables import RunnableConfig
from langmem.short_term import SummarizationNode
from langchain_core.messages.utils import count_tokens_approximately
from memory_agent import MemoryCheckpointer, MemoryPersistence
from langgraph.config import get_store
from log import logger, get_metadata
from kgrag_store import State
from kgrag import kgrag
from config import settings

summarize_node = SummarizationNode(
    token_counter=count_tokens_approximately,
    model=kgrag._get_model(),
    max_tokens=384,
    max_summary_tokens=128,
    output_messages_key="llm_input_messages",
)


def prompt(state):
    """Prepare the messages for the LLM."""
    # Get store from configured contextvar;
    # Same as that provided to `create_react_agent`
    store = get_store()
    memories = store.search(
        # Search within the same namespace as the one
        # we've configured for the agent
        ("memories",),
        query=state["messages"][-1].content,
    )
    system_msg = f"""You are a helpful assistant.

    ## Memories
    <memories>
    {memories}
    </memories>
    """
    return [{"role": "system", "content": system_msg}, *state["messages"]]


def _get_memory():
    """
    Retrieves the memory persistence configuration and initializes
    the MemoryStoreQdrant.
    Args:
        kwargs (dict): A dictionary containing optional parameters
        for memory persistence configuration.
        The expected structure for `memory_persistence_config` is:
            {
                "host": "localhost",
                "port": 6379,
                "db": 0
            }
    If `memory_persistence_config` is not provided, it defaults
        to the Redis settings from the environment.
    If `model_embeggind_type` is "vllm", it requires `model_embedding_url`
        to be provided.
    If `model_embedding` and `model_embedding_url` are not provided,
        it raises a ValueError.
    If `qdrant_url` is not provided, it raises a ValueError.
    If `model_embedding_vs_name` and `model_embedding_vs_type`
        are not provided, it raises a ValueError.
    If `model_embedding_vs_type` is "local", it requires
        `model_embedding_vs_path` to be provided.
    Args:
        kwargs (dict): A dictionary containing optional parameters
            for memory persistence configuration.
        The expected structure for `memory_persistence_config` is:
            {
                "host": "localhost",
                "port": 6379,
                "db": 0
            }
        - `model_embedding_type`: The type of model embedding to use
            (default is settings.LLM_MODEL_TYPE).
        - `model_embedding`: The name of the model embedding to use
            (default is settings.MODEL_EMBEDDING).
        - `model_embedding_url`: The URL of the model embedding
            (default is settings.LLM_EMBEDDING_URL).
        - `qdrant_url`: The URL of the Qdrant instance
            (default is the environment variable QDRANT_URL).
        - `model_embedding_vs_name`: The name of the vector store for
            the model embedding (default is settings.VECTORDB_SENTENCE_MODEL).
        - `model_embedding_vs_type`: The type of vector store
            for the model embedding
            (default is settings.VECTORDB_SENTENCE_TYPE).
        - `model_embedding_vs_path`: The path to the vector store
            for the model embedding
            (default is settings.VECTORDB_SENTENCE_PATH).

        Returns:
        tuple: A tuple containing the host persistence configuration
            and the initialized MemoryStoreQdrant.

        Raises:
        ValueError: If the memory persistence configuration is
            not provided or is invalid.
    """
    host_persistence_config = {
                                "host": settings.REDIS_HOST,
                                "port": settings.REDIS_PORT,
                                "db": settings.REDIS_DB
                            }
    if settings.LLM_MODEL_TYPE == "vllm" and not settings.LLM_EMBEDDING_URL:
        raise ValueError(
            "model_embedding must be provided when "
            "model_embeggind_type is 'vllm'"
        )

    if not settings.QDRANT_URL:
        raise ValueError("Qdrant URL must be provided")

    if not all([
        settings.VECTORDB_SENTENCE_MODEL,
        settings.VECTORDB_SENTENCE_TYPE
    ]):
        raise ValueError(
            (
                "Both model_embedding_vs_name and "
                "model_embedding_vs_type must be provided"
            )
        )

    if (
        settings.VECTORDB_SENTENCE_TYPE == "local"
        and not settings.VECTORDB_SENTENCE_PATH
    ):
        raise ValueError(
            (
                "model_embedding_vs_path must be provided when "
                "model_embedding_vs_type is 'local'"
            )
        )
    memory_store = MemoryPersistence(
        model_embeggind_type=settings.LLM_MODEL_TYPE,
        model_embedding_name=settings.MODEL_EMBEDDING,
        model_embedding_url=settings.LLM_EMBEDDING_URL,
        qdrant_url=settings.QDRANT_URL,
        model_embedding_vs_name=settings.VECTORDB_SENTENCE_MODEL,
        model_embedding_vs_type=settings.VECTORDB_SENTENCE_TYPE,
        model_embedding_vs_path=settings.VECTORDB_SENTENCE_PATH
    )

    return host_persistence_config, memory_store


async def invoke(
    prompt: str,
    tools: list,
    thread_id: str = str(uuid.uuid4())
):
    """
    Asynchronously runs the agent with the given prompt.

    Args:
        prompt (str): The user input prompt to be processed by the agent.
        tools (list): A list of tools available for the agent to use.
        thread_id (str): A unique identifier for the thread,
            used for tracking and logging.
    """

    host_persistence_config, memory_store = _get_memory()

    config, input_data = _get_agent_params(prompt, thread_id)

    async with MemoryCheckpointer.from_conn_info(
        host=host_persistence_config["host"],
        port=host_persistence_config["port"],
        db=host_persistence_config["db"]
    ) as checkpointer:

        await checkpointer.adelete_by_thread_id(thread_id)

        agent = create_react_agent(
            kgrag._get_model(),
            prompt=prompt,
            tools=tools,
            store=memory_store.get_in_memory_store(),
            state_schema=State,
            pre_model_hook=summarize_node,
            checkpointer=checkpointer
        )

        response_agent = await agent.ainvoke(
            input=input_data, config=config,
            stream_mode="updates"
        )

        if (
            "messages" in response_agent
            and len(response_agent["messages"]) > 0
        ):
            event_messages = response_agent["messages"]
            event_response = event_messages[-1].content
            # If there are messages from the agent, return the last message
            logger.info(
                f">>> Response event from agent: {event_response}",
                extra=get_metadata(thread_id=thread_id)
            )
            return event_response


async def stream(
    prompt: str,
    tools: list,
    thread_id: str = str(uuid.uuid4())
):
    """
    Asynchronously streams response chunks from the agent based
    on the provided prompt.

    Args:
        prompt (str): The user input prompt to be processed by the agent.
        tools (list): A list of tools available for the agent to use.
        thread_id (str): A unique identifier for the thread,
            used for tracking and logging.
    """
    try:

        host_persistence_config, memory_store = _get_memory()

        config, input_data = _get_agent_params(prompt, thread_id)

        async with MemoryCheckpointer.from_conn_info(
                host=host_persistence_config["host"],
                port=host_persistence_config["port"],
                db=host_persistence_config["db"]
        ) as checkpointer:

            # Delete checkpoints older than 15 minutes for the current thread
            await checkpointer.adelete_by_thread_id(
                thread_id=str(thread_id),
                filter_minutes=15
            )

            agent = create_react_agent(
                kgrag._get_model(),
                tools=tools,
                store=memory_store.get_in_memory_store(),
                checkpointer=checkpointer,
                state_schema=State,
                pre_model_hook=summarize_node,
            )

            index: int = 1
            async for event in agent.astream(
                input=input_data,
                config=config,
                stream_mode="updates"
            ):

                logger.debug(
                    f">>> Event {index} received: {event}",
                    extra=get_metadata(thread_id=thread_id)
                )
                event_item = None

                if "agent" in event:
                    event_item = event["agent"]
                    logger.debug(
                        f">>> Agent event detected {event_item}",
                        extra=get_metadata(thread_id=thread_id)
                    )

                elif "tools" in event:
                    event_item = event["tools"]
                    logger.debug(
                        f">>> Tools event detected {event_item}",
                        extra=get_metadata(thread_id=thread_id)
                    )

                if event_item is not None:
                    if (
                        "messages" in event_item
                        and len(event_item["messages"]) > 0
                    ):
                        event_messages = event_item["messages"]
                        event_response = event_messages[-1].content
                        # If there are messages from the agent, return
                        # the last message
                        logger.info(
                            f">>> Response event from agent: {event_response}",
                            extra=get_metadata(thread_id=thread_id)
                        )
                        if (
                            event_response
                            or (len(event_response) > 0)
                        ):
                            yield event_response

                index += 1

    except Exception as e:
        # In caso di errore, restituisce un messaggio di errore
        error_message = json.dumps({"error": str(e)})
        yield f"response: {error_message}\n\n"
        raise e


def _get_agent_params(prompt, thread_id):
    """
    Prepares the configuration and input data for the agent
    based on the provided prompt and thread ID.
    Args:
        prompt (str): The user input prompt to be processed by the agent.
        thread_id (str): A unique identifier for the thread,
        used for tracking and logging.
    Returns:
        tuple: A tuple containing the configuration for the agent
        and the input data structured for processing.
    """
    config: RunnableConfig = {
            "configurable": {
                "thread_id": thread_id,
                "recursion_limit": settings.MAX_RECURSION_LIMIT,
            }
        }

    input_data = {"messages": [{"role": "user", "content": prompt}]}
    return config, input_data
