"""
title: Exa CrewAI Answer Manifold Pipe.

author: adrielmartins
version: 0.1.0
"""

import asyncio
import logging
import os
from collections.abc import AsyncGenerator, Awaitable, Callable

import httpx
from crewai import LLM, Agent, Crew, Task
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from open_webui.utils.misc import pop_system_message
except ImportError:
    # Fallback for testing outside OpenWebUI environment
    def pop_system_message(messages: list[dict]) -> tuple[dict | None, list[dict]]:
        """Extract system message from messages list."""
        if messages and messages[0].get("role") == "system":
            return messages[0], messages[1:]
        return None, messages


class PipeExceptionError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class ExaAnswerTool(BaseTool):
    """Tool that uses Exa's Answer API to search and generate answers."""

    name: str = "exa_answer_search"
    description: str = (
        "Search the web using Exa's Answer API to find information and generate "
        "comprehensive answers. Use this when you need current information from the web. "
        "The query should be a clear question or search term."
    )

    exa_api_key: str = Field(description="Exa API key")
    exa_api_base_url: str = Field(default="https://api.exa.ai")
    text_parameter: bool = Field(default=False, description="Whether to include full text")
    num_results: int = Field(default=10, description="Number of results to return")
    timeout: int = Field(default=30, description="Request timeout in seconds")

    def _run(self, query: str) -> str:
        """Execute the search synchronously by calling the async version."""
        try:
            # Run the async version in the current event loop or create a new one
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If there's already a running loop, we need to run in a thread
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._arun(query))
                        return future.result()
                else:
                    # If no loop is running, just run the async function
                    return asyncio.run(self._arun(query))
            except RuntimeError:
                # Fallback for edge cases
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._arun(query))
                    return future.result()
        except Exception as e:
            logger.error(f"Error in sync ExaAnswerTool._run: {e}")
            return f"Error searching: {str(e)}"

    async def _arun(self, query: str) -> str:
        """Execute the search and return formatted results with citations."""
        headers = {
            "x-api-key": self.exa_api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "query": query,
            "text": self.text_parameter,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.exa_api_base_url}/answer",
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()

                answer = data.get("answer", "No answer provided.")
                citations = data.get("citations", [])

                # Store citations for later emission
                self._last_citations = citations

                # Format the response with inline citations
                result = f"{answer}\n\n"
                if citations:
                    result += "Sources:\n"
                    for i, citation in enumerate(citations, 1):
                        title = citation.get("title", "Unknown")
                        url = citation.get("url", "")
                        result += f"[{i}] {title}: {url}\n"

                return result

        except httpx.HTTPStatusError as e:
            error_msg = f"Exa API error: {e.response.status_code} - {e.response.text}"
            logging.error(error_msg)
            return f"Error searching: {error_msg}"
        except Exception as e:
            logging.exception("Error calling Exa API")
            return f"Error searching: {str(e)}"


class ExaContextTool(BaseTool):
    """Tool that uses Exa's Context API to search for coding-related information."""

    name: str = "exa_context_search"
    description: str = (
        "Search GitHub repos, documentation, and Stack Overflow using Exa's Context API "
        "to find code snippets, examples, and technical documentation. Use this when you need "
        "code examples, implementation details, or technical information. "
        "The query should be a clear technical question or search term."
    )

    exa_api_key: str = Field(description="Exa API key")
    exa_api_base_url: str = Field(default="https://api.exa.ai")
    tokens_num: int = Field(default=5000, description="Number of tokens for context")
    timeout: int = Field(default=30, description="Request timeout in seconds")

    def _run(self, query: str) -> str:
        """Execute the search synchronously by calling the async version."""
        try:
            # Run the async version in the current event loop or create a new one
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If there's already a running loop, we need to run in a thread
                    import concurrent.futures

                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self._arun(query))
                        return future.result()
                else:
                    # If no loop is running, just run the async function
                    return asyncio.run(self._arun(query))
            except RuntimeError:
                # Fallback for edge cases
                import concurrent.futures

                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, self._arun(query))
                    return future.result()
        except Exception as e:
            logger.error(f"Error in sync ExaContextTool._run: {e}")
            return f"Error searching: {str(e)}"

    async def _arun(self, query: str) -> str:
        """Execute the context search and return formatted results."""
        headers = {
            "x-api-key": self.exa_api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "query": query,
            "tokensNum": self.tokens_num,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.exa_api_base_url}/context",
                    json=payload,
                    headers=headers,
                    timeout=self.timeout,
                )
                response.raise_for_status()
                data = response.json()

                context_response = data.get("response", "No context provided.")
                results_count = data.get("resultsCount", 0)

                # Format the response
                result = f"{context_response}\n\n"
                result += f"Found {results_count} relevant results.\n"

                # Store empty citations since Context API doesn't return traditional citations
                self._last_citations = []

                return result

        except httpx.HTTPStatusError as e:
            error_msg = f"Exa API error: {e.response.status_code} - {e.response.text}"
            logging.error(error_msg)
            return f"Error searching: {error_msg}"
        except Exception as e:
            logging.exception("Error calling Exa Context API")
            return f"Error searching: {str(e)}"


class Pipe:
    class Valves(BaseModel):
        """
        Configuration settings for Exa CrewAI Answer pipe.

        Attributes:
            EXA_API_KEY: Authentication key for Exa API. Required.
            EXA_API_BASE_URL: Exa API base URL. Defaults to official API URL.
            EXA_TEXT_PARAMETER: Whether to include full text content. Default False.
            EXA_CONTEXT_TOKENS_NUM: Number of tokens for context search. Default 5000.
            OPENROUTER_API_KEY: Authentication key for OpenRouter API. Required.
            OPENROUTER_API_BASE_URL: OpenRouter API base URL. Defaults to official API URL.
            OPENROUTER_MODEL: Model to use via OpenRouter. Default anthropic/claude-3.5-sonnet.
            EMIT_SOURCES: Whether to include citation sources in responses. Default True.
            TIMEOUT: Request timeout in seconds. Default 60.
        """

        EXA_API_KEY: str | None = Field(
            default=os.getenv("EXA_API_KEY"),
            description="Exa API key.",
        )
        EXA_API_BASE_URL: str = Field(
            default="https://api.exa.ai",
            description="Exa API base URL.",
        )
        EXA_TEXT_PARAMETER: bool = Field(
            default=False,
            description="Whether to include full text content in search results. "
            "Enabling this provides more context but uses more tokens.",
        )
        EXA_CONTEXT_TOKENS_NUM: int = Field(
            default=5000,
            description="Number of tokens for Exa Context API responses. "
            "Default is 5000, use 10000 for expanded context.",
        )
        OPENROUTER_API_KEY: str | None = Field(
            default=os.getenv("OPENROUTER_API_KEY"),
            description="OpenRouter API key for LLM access.",
        )
        OPENROUTER_API_BASE_URL: str = Field(
            default="https://openrouter.ai/api/v1",
            description="OpenRouter API base URL.",
        )
        OPENROUTER_MODEL: str = Field(
            default="moonshotai/kimi-k2-thinking",
            description="Model to use via OpenRouter (e.g., moonshotai/kimi-k2-thinking, "
            "anthropic/claude-3.5-sonnet, openai/gpt-4-turbo, etc.).",
        )
        EMIT_SOURCES: bool = Field(
            default=True,
            description="Emit sources as citations in the UI.",
        )
        TIMEOUT: int = Field(
            default=60,
            description="Request timeout in seconds.",
        )

    def __init__(self) -> None:
        self.type = "manifold"
        self.valves = self.Valves()
        self._last_citations = []

    def pipes(self) -> list[dict[str, str]]:
        """Return a list of available pipes with their IDs and names."""
        return [
            {"id": "exa-crewai-answer", "name": "Exa CrewAI Answer"},
        ]

    def _format_citations_as_sources(self, citations: list[dict]) -> list[dict]:
        """
        Format citations to match the expected structure for sources.

        Expected format comes from Chat.svelte in OpenWebUI.
        """
        formatted_sources = []

        for i, citation in enumerate(citations):
            url = citation.get("url", "")
            title = citation.get("title", f"Source {i + 1}")
            author = citation.get("author", "")
            published_date = citation.get("publishedDate", "")

            # Build metadata
            metadata = {"source": url}
            if author:
                metadata["author"] = author
            if published_date:
                metadata["publishedDate"] = published_date

            # Build document preview
            text_content = citation.get("text", "")
            document = [
                text_content[:500] if text_content else "Click the link to view the content."
            ]

            formatted_sources.append(
                {
                    "source": {
                        "name": f"[{i + 1}] {title}",
                        "type": "web_search_results",
                        "urls": [url],
                    },
                    "document": document,
                    "metadata": [metadata],
                }
            )

        return formatted_sources

    async def _emit_sources(
        self, citations: list[dict], event_emitter: Callable[[dict], Awaitable[None]] | None
    ) -> None:
        """
        Emit sources if the valve is enabled.

        Args:
            citations: A list of citation dictionaries.
            event_emitter: A callable to emit events.
        """
        if citations and self.valves.EMIT_SOURCES and event_emitter:
            sources = self._format_citations_as_sources(citations)
            if sources:
                await event_emitter({"type": "chat:completion", "data": {"sources": sources}})

    def _build_conversation_context(self, messages: list[dict]) -> str:
        """
        Build a formatted conversation context from message history.

        Args:
            messages: List of message dictionaries with 'role' and 'content'.

        Returns:
            Formatted string representing the conversation history.
        """
        context = "Previous conversation:\n\n"
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                context += f"User: {content}\n\n"
            elif role == "assistant":
                context += f"Assistant: {content}\n\n"
        return context

    async def pipe(
        self,
        body: dict,
        __event_emitter__: Callable[[dict], Awaitable[None]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Main pipe method that processes requests using CrewAI."""
        logger.info("Starting Exa CrewAI pipe execution")

        # Validate API keys
        if not self.valves.EXA_API_KEY:
            msg = "EXA_API_KEY not provided in the valves."
            logger.error(msg)
            raise PipeExceptionError(msg)

        if not self.valves.OPENROUTER_API_KEY:
            msg = "OPENROUTER_API_KEY not provided in the valves."
            logger.error(msg)
            raise PipeExceptionError(msg)

        logger.info("API keys validated successfully")

        try:
            # Extract system message and conversation history
            system_message, messages = pop_system_message(body.get("messages", []))
            logger.info(f"Extracted {len(messages)} messages from request")

            # Build conversation context
            conversation_context = ""
            if len(messages) > 1:
                # Include previous messages for context (excluding the last user message)
                conversation_context = self._build_conversation_context(messages[:-1])
                logger.info("Built conversation context from previous messages")

            # Get the current user query
            current_query = messages[-1].get("content", "") if messages else ""
            logger.info(f"Current query: {current_query[:100]}...")

            # Create the Exa Answer tool instance
            logger.info("Creating Exa Answer tool")
            exa_answer_tool = ExaAnswerTool(
                exa_api_key=self.valves.EXA_API_KEY,
                exa_api_base_url=self.valves.EXA_API_BASE_URL,
                text_parameter=self.valves.EXA_TEXT_PARAMETER,
                timeout=self.valves.TIMEOUT,
            )

            # Create the Exa Context tool instance for coding questions
            logger.info("Creating Exa Context tool")
            exa_context_tool = ExaContextTool(
                exa_api_key=self.valves.EXA_API_KEY,
                exa_api_base_url=self.valves.EXA_API_BASE_URL,
                tokens_num=self.valves.EXA_CONTEXT_TOKENS_NUM,
                timeout=self.valves.TIMEOUT,
            )

            # Configure OpenRouter LLM using CrewAI's native LLM class
            logger.info(f"Configuring OpenRouter LLM with model: {self.valves.OPENROUTER_MODEL}")
            logger.info(f"OpenRouter base URL: {self.valves.OPENROUTER_API_BASE_URL}")

            try:
                llm = LLM(
                    model=f"openrouter/{self.valves.OPENROUTER_MODEL}",
                    api_key=self.valves.OPENROUTER_API_KEY,
                    base_url=self.valves.OPENROUTER_API_BASE_URL,
                    temperature=0.7,
                )
                logger.info("LLM configuration successful")
            except Exception as e:
                logger.error(f"LLM configuration failed: {e}")
                raise

            # Create the agent
            logger.info("Creating CrewAI agent")
            try:
                agent = Agent(
                    role="Research Assistant",
                    goal=(
                        "Provide accurate and comprehensive answers using web search when needed"
                    ),
                    backstory=(
                        "You are an expert research assistant with access "
                        "to real-time web search. You have two specialized "
                        "search tools: exa_answer_search for general web "
                        "queries and current events, and exa_context_search "
                        "for coding questions, technical documentation, and "
                        "code examples. You strategically choose the right "
                        "tool based on the question type. You maintain "
                        "conversation context and can handle follow-up "
                        "questions naturally."
                    ),
                    tools=[exa_answer_tool, exa_context_tool],
                    llm=llm,
                    verbose=True,  # Enable verbose for debugging
                    allow_delegation=False,
                )
                logger.info("Agent creation successful")
            except Exception as e:
                logger.error(f"Agent creation failed: {e}")
                raise

            # Build the task description with context
            task_description = ""
            if conversation_context:
                task_description += f"{conversation_context}\n"

            task_description += f"Current query: {current_query}\n\n"
            task_description += (
                "Respond to the current query. Choose the appropriate "
                "search tool based on the question:\n"
                "- Use exa_context_search for coding questions, "
                "technical documentation, or code examples\n"
                "- Use exa_answer_search for general web queries, "
                "current events, or non-technical information\n"
                "You can call tools multiple times if needed to gather "
                "sufficient information. Provide a comprehensive answer "
                "based on your findings."
            )

            # Create the task
            task = Task(
                description=task_description,
                expected_output=(
                    "A comprehensive answer to the user's query, incorporating any relevant "
                    "information from web searches if needed."
                ),
                agent=agent,
            )

            # Create and execute the crew
            logger.info("Creating CrewAI crew")
            try:
                crew = Crew(
                    agents=[agent],
                    tasks=[task],
                    verbose=True,  # Enable verbose for debugging
                )
                logger.info("Crew creation successful")
            except Exception as e:
                logger.error(f"Crew creation failed: {e}")
                raise

            # Execute the crew
            logger.info("Executing crew kickoff")
            try:
                result = crew.kickoff()
                logger.info(f"Crew kickoff completed. Result type: {type(result)}")

                # Handle CrewAI result format
                if result is None:
                    logger.error("CrewAI returned None")
                    raise ValueError("CrewAI returned None result")
                elif hasattr(result, "raw"):
                    # CrewAI CrewOutput object - this is the standard format
                    result_text = result.raw
                    logger.info("Extracted result from CrewOutput.raw")
                else:
                    # Fallback for unexpected formats
                    result_text = str(result)
                    logger.info("Converted result to string (fallback)")

                logger.info(f"Result text length: {len(result_text)}")
                logger.info(f"Result text preview: {result_text[:200]}...")

                if not result_text or result_text.strip() == "":
                    logger.error("Result is empty or None")
                    raise ValueError("Empty result from CrewAI execution")

            except Exception as e:
                logger.error(f"Crew execution failed: {e}")
                # Provide a fallback response
                result_text = f"I apologize, but I encountered an error while processing your request: {str(e)}. Please try again or rephrase your question."
                logger.info("Using fallback response due to crew execution error")

            # Try to extract citations from both tools if they exist
            citations = []
            answer_citations = getattr(exa_answer_tool, "_last_citations", [])
            context_citations = getattr(exa_context_tool, "_last_citations", [])

            # Combine citations from both tools
            if answer_citations:
                citations.extend(answer_citations)
            if context_citations:
                citations.extend(context_citations)

            # Yield the result
            yield result_text

            # Emit sources after yielding the main content
            if citations:
                await self._emit_sources(citations, __event_emitter__)

        except Exception as e:
            logger.exception("Error in Exa CrewAI pipe")
            yield f"Error: {str(e)}"
