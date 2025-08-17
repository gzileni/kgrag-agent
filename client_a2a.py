from python_a2a import (
    A2AClient, Message, TextContent, MessageRole, Conversation
)


def research_workflow(query):
    # Connect to the specialized [Python A2A](python-a2a.html) agents
    llm_client = A2AClient("http://localhost:5002/a2a")     # LLM agent
    search_client = A2AClient("http://localhost:5003/a2a")  # Search agent
    summarize_client = A2AClient("http://localhost:5004/a2a")  # Summarize agent

    # Track the entire workflow in a [Python A2A](python-a2a.html) conversation
    conversation = Conversation()
    conversation.create_text_message(
        text=f"Research question: {query}",
        role=MessageRole.USER
    )

    # Step 1: Generate search queries using [Python A2A](python-a2a.html)
    print("Generating search queries...")
    search_request = Message(
        content=TextContent(
            text=f"Based on this research question: '{query}', "
                 f"generate 3 specific search queries that would help find relevant information."
        ),
        role=MessageRole.USER
    )
    search_queries_response = llm_client.send_message(search_request)
    conversation.add_message(search_queries_response)

    # Step 2: Retrieve information using [Python A2A](python-a2a.html)
    print("Retrieving information...")
    search_message = Message(
        content=TextContent(
            text=f"Search for information to answer: {query}\n\n"
                 f"Using these queries:\n{search_queries_response.content.text}"
        ),
        role=MessageRole.USER
    )
    search_results = search_client.send_message(search_message)
    conversation.add_message(search_results)

    # Step 3: Synthesize information using [Python A2A](python-a2a.html)
    print("Synthesizing information...")
    summarize_message = Message(
        content=TextContent(
            text=f"Synthesize this information to answer the question: '{query}'\n\n"
                 f"Information:\n{search_results.content.text}"
        ),
        role=MessageRole.USER
    )
    summary_response = summarize_client.send_message(summarize_message)
    conversation.add_message(summary_response)

    # Add final answer to the [Python A2A](python-a2a.html) conversation
    conversation.create_text_message(
        text=f"Answer to your research question:\n\n{summary_response.content.text}",
        role=MessageRole.AGENT
    )

    return conversation


# Example usage of [Python A2A](python-a2a.html)
if __name__ == "__main__":
    query = input("What's your research question? ")
    result = research_workflow(query)
    print("\nResearch Complete!")
    print("=" * 50)
    print(result.messages[-1].content.text)
