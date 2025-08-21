from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    InvalidParamsError,
    Part,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    new_agent_text_message,
    new_task,
)
from a2a.utils.errors import ServerError
from agent import KGragAgent
from log import logger


class KGragAgentExecutor(AgentExecutor):
    """
    KGrag AgentExecutor Example.
    """

    def __init__(self):
        """
        Initializes the KGragAgentExecutor.
        """
        self.agent = KGragAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        error = self._validate_request(context)
        if error:
            raise ServerError(error=InvalidParamsError())

        query = context.get_user_input()
        task = context.current_task
        if not task:
            task = new_task(context.message)  # type: ignore
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        try:
            async for item in self.agent.stream(query):
                result = item['result']
                is_task_complete = result['is_task_complete']
                require_user_input = result['require_user_input']
                error = item['error']
                try:

                    if not is_task_complete and not require_user_input:
                        await updater.update_status(
                            TaskState.working,
                            new_agent_text_message(
                                result['content'],
                                task.context_id,
                                task.id,
                            ),
                        )
                    elif require_user_input:
                        await updater.update_status(
                            TaskState.input_required,
                            new_agent_text_message(
                                result['content'],
                                task.context_id,
                                task.id,
                            ),
                            final=True,
                        )
                        break
                    else:
                        await updater.add_artifact(
                            [Part(root=TextPart(text=result['content']))],
                            name='conversion_result',
                        )
                        await updater.complete()
                        break

                except Exception as e:
                    logger.error(
                        f'An error occurred while streaming the response: '
                        f'{e}\n'
                        f'{error}'
                    )
                    await updater.update_status(
                        TaskState.failed,
                        new_agent_text_message(
                            error,
                            task.context_id,
                            task.id,
                        )
                    )
                    raise e
        except Exception as e:
            logger.error(
                f'An error occurred while executing the agent: {e}'
            )
            await updater.update_status(
                TaskState.failed,
                new_agent_text_message(
                    'An error occurred while processing your request.',
                    task.context_id,
                    task.id,
                ),
                final=True
            )
            await updater.complete()

    def _validate_request(
        self,
        context: RequestContext
    ) -> bool:
        """
        Validates the request context.
        """
        return False

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue
    ) -> None:
        """
        Cancels the current task.
        """
        raise ServerError(error=UnsupportedOperationError())
