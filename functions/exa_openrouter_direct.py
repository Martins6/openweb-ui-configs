"""
title: Exa OpenRouter Direct Answer Pipe.

author: adrielmartins
version: 0.1.0
"""

import asyncio
import json
import logging
import os
from collections.abc import AsyncGenerator, Awaitable, Callable

import httpx
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


async def exa_answer_search(
    query: str,
    api_key: str,
    base_url: str = "https://api.exa.ai",
    text: bool = False,
    timeout: int = 30,
) -> tuple[str, list[dict]]:
    """Search using Exa Answer API. Returns (answer_text, citations)."""
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "query": query,
        "text": text,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/answer",
                json=payload,
                headers=headers,
                timeout=timeout,
            )
            response.raise_for_status()
            data = response.json()

            answer = data.get("answer", "No answer provided.")
            citations = data.get("citations", [])

            return answer, citations

    except httpx.HTTPStatusError as e:
        error_msg = f"Exa API error: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return f"Error searching: {error_msg}", []
    except Exception as e:
        logger.exception("Error calling Exa API")
        return f"Error searching: {str(e)}", []


async def exa_context_search(
    query: str,
    api_key: str,
    base_url: str = "https://api.exa.ai",
    tokens_num: int = 5000,
    timeout: int = 30,
) -> tuple[str, list[dict]]:
    """Search using Exa Context API. Returns (context_text, citations)."""
    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    payload = {
        "query": query,
        "tokensNum": tokens_num,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/context",
                json=payload,
                headers=headers,
                timeout=timeout,
            )
            response.raise_for_status()
            data = response.json()

            context_response = data.get("response", "No context provided.")
            results_count = data.get("resultsCount", 0)

            # Context API doesn't return traditional citations
            result = f"{context_response}\n\nFound {results_count} relevant results."
            return result, []

    except httpx.HTTPStatusError as e:
        error_msg = f"Exa API error: {e.response.status_code} - {e.response.text}"
        logger.error(error_msg)
        return f"Error searching: {error_msg}", []
    except Exception as e:
        logger.exception("Error calling Exa Context API")
        return f"Error searching: {str(e)}", []


# OpenRouter tool definitions
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "exa_answer_search",
            "description": (
                "Search the web using Exa's Answer API to find information and generate "
                "comprehensive answers. Use this when you need current information from the web. "
                "The query should be a clear question or search term."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query or question",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "exa_context_search",
            "description": (
                "Search GitHub repos, documentation, and Stack Overflow using Exa's Context API "
                "to find code snippets, examples, and technical documentation. Use this when you need "
                "code examples, implementation details, or technical information. "
                "The query should be a clear technical question or search term."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Technical search query for code or documentation",
                    }
                },
                "required": ["query"],
            },
        },
    },
]


class Pipe:
    class Valves(BaseModel):
        """
        Configuration settings for Exa OpenRouter Direct Answer pipe.

        Attributes:
            EXA_API_KEY: Authentication key for Exa API. Required.
            EXA_API_BASE_URL: Exa API base URL. Defaults to official API URL.
            EXA_TEXT_PARAMETER: Whether to include full text content. Default False.
            EXA_CONTEXT_TOKENS_NUM: Number of tokens for context search. Default 5000.
            OPENROUTER_API_KEY: Authentication key for OpenRouter API. Required.
            OPENROUTER_API_BASE_URL: OpenRouter API base URL. Defaults to official API URL.
            OPENROUTER_MODEL: Model to use via OpenRouter. Default moonshotai/kimi-k2-thinking.
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

    def pipes(self) -> list[dict[str, str]]:
        """Return a list of available pipes with their IDs and names."""
        return [
            {"id": "exa-openrouter-direct", "name": "Exa OpenRouter Direct"},
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

    async def _call_openrouter_with_tools(
        self, messages: list[dict], all_citations: list[dict]
    ) -> tuple[str, list[dict]]:
        """Call OpenRouter API with tool definitions and handle tool calls."""
        headers = {
            "Authorization": f"Bearer {self.valves.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://openwebui.com",
            "X-Title": "Exa OpenRouter Direct",
        }

        # Initial API call with tools
        payload = {
            "model": self.valves.OPENROUTER_MODEL,
            "messages": messages,
            "tools": TOOLS,
            "tool_choice": "auto",
            "temperature": 0.7,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.valves.OPENROUTER_API_BASE_URL}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=self.valves.TIMEOUT,
                )
                response.raise_for_status()
                data = response.json()

                message = data["choices"][0]["message"]
                tool_calls = message.get("tool_calls", [])

                # If no tool calls, return the response
                if not tool_calls:
                    return message.get("content", ""), all_citations

                # Handle tool calls
                messages.append(message)  # Add assistant message with tool calls

                for tool_call in tool_calls:
                    function_name = tool_call["function"]["name"]
                    function_args = json.loads(tool_call["function"]["arguments"])

                    # Execute the appropriate tool
                    if function_name == "exa_answer_search":
                        if not self.valves.EXA_API_KEY:
                            result = "Error: EXA_API_KEY not configured"
                            citations = []
                        else:
                            result, citations = await exa_answer_search(
                                query=function_args["query"],
                                api_key=self.valves.EXA_API_KEY,
                                base_url=self.valves.EXA_API_BASE_URL,
                                text=self.valves.EXA_TEXT_PARAMETER,
                                timeout=self.valves.TIMEOUT,
                            )
                        all_citations.extend(citations)
                    elif function_name == "exa_context_search":
                        if not self.valves.EXA_API_KEY:
                            result = "Error: EXA_API_KEY not configured"
                            citations = []
                        else:
                            result, citations = await exa_context_search(
                                query=function_args["query"],
                                api_key=self.valves.EXA_API_KEY,
                                base_url=self.valves.EXA_API_BASE_URL,
                                tokens_num=self.valves.EXA_CONTEXT_TOKENS_NUM,
                                timeout=self.valves.TIMEOUT,
                            )
                        all_citations.extend(citations)
                    else:
                        result = f"Unknown tool: {function_name}"

                    # Add tool result to messages
                    messages.append(
                        {
                            "tool_call_id": tool_call["id"],
                            "role": "tool",
                            "content": result,
                        }
                    )

                # Make final API call with tool results
                final_payload = {
                    "model": self.valves.OPENROUTER_MODEL,
                    "messages": messages,
                    "temperature": 0.7,
                }

                final_response = await client.post(
                    f"{self.valves.OPENROUTER_API_BASE_URL}/chat/completions",
                    json=final_payload,
                    headers=headers,
                    timeout=self.valves.TIMEOUT,
                )
                final_response.raise_for_status()
                final_data = final_response.json()

                final_message = final_data["choices"][0]["message"]
                logger.debug(f"Final message structure: {final_message}")
                result_text = final_message.get("content", "")

                if not result_text or not result_text.strip():
                    logger.warning("Empty response from OpenRouter, using fallback")
                    if all_citations:
                        # If we have citations but no response, create a summary
                        result_text = f"Based on the search results I found, here's what I can tell you about your query. I found {len(all_citations)} relevant sources that should help answer your question."
                    else:
                        result_text = "I apologize, but I couldn't generate a response. Please try rephrasing your question."

                return result_text, all_citations

        except httpx.HTTPStatusError as e:
            error_msg = f"OpenRouter API error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return f"Error: {error_msg}", all_citations
        except Exception as e:
            logger.exception("Error calling OpenRouter API")
            return f"Error: {str(e)}", all_citations

    async def pipe(
        self,
        body: dict,
        __event_emitter__: Callable[[dict], Awaitable[None]] | None = None,
    ) -> AsyncGenerator[str, None]:
        """Main pipe method that processes requests using direct OpenRouter tool calling."""
        logger.info("Starting Exa OpenRouter Direct pipe execution")

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
            if len(messages) > 1:
                # Include previous messages for context (excluding the last user message)
                conversation_context = self._build_conversation_context(messages[:-1])
                if conversation_context:
                    # Add context as a system message
                    context_message = {
                        "role": "system",
                        "content": (
                            f"{conversation_context}\n\n"
                            "You have access to two search tools:\n"
                            "- exa_answer_search: for general web queries and current events\n"
                            "- exa_context_search: for coding questions, technical documentation, and code examples\n"
                            "Choose the appropriate tool based on the question type. You can call tools multiple times if needed."
                        ),
                    }
                    messages = [context_message] + messages[-1:]  # Keep only the last user message
                    logger.info("Added conversation context to system message")

            # Call OpenRouter with tools
            logger.info("Calling OpenRouter with tool support")
            result_text, citations = await self._call_openrouter_with_tools(messages, [])

            logger.info(f"OpenRouter response received, length: {len(result_text)}")
            logger.info(f"Found {len(citations)} citations")
            logger.info(f"Response preview: {result_text[:200]}...")

            # Validate and log response before yielding
            if not result_text or not result_text.strip():
                logger.warning("Empty response detected, using fallback")
                if citations:
                    result_text = f"Based on my search, I found {len(citations)} relevant sources that should help answer your question."
                else:
                    result_text = "I apologize, but I couldn't generate a response. Please try rephrasing your question."

            logger.info(f"About to yield response of length {len(result_text)}")
            logger.info(f"Response preview: {result_text[:100]}...")

            # Yield the result
            yield str(result_text)

            logger.info("Response yielded successfully")

            # Small delay to ensure response is displayed before sources
            await asyncio.sleep(0.1)

            # Emit sources after yielding the main content
            if citations:
                logger.info(f"Emitting {len(citations)} sources")
                await self._emit_sources(citations, __event_emitter__)
                logger.info("Sources emitted successfully")

        except Exception as e:
            logger.exception("Error in Exa OpenRouter Direct pipe")
            yield f"Error: {str(e)}"
