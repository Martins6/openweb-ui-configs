# Exa CrewAI Answer Pipe

## Overview

This OpenWebUI pipe integrates Exa's Answer API with CrewAI to provide intelligent web search-powered responses with conversation context management.

## Features

- **CrewAI Agent**: Single intelligent agent that decides when to search
- **Exa Answer API**: Uses Exa's /answer endpoint for high-quality web search results
- **Conversation Context**: Maintains full message history, not one-shot
- **Multiple Tool Calls**: Agent can search multiple times if needed
- **OpenRouter Integration**: Configurable LLM model via OpenRouter
- **Citation Support**: Automatically emits sources in OpenWebUI format

## Architecture

```
User Query → CrewAI Agent → [Decides if search needed]
                ↓
          Exa Answer Tool → Web Search
                ↓
          Agent Response → OpenWebUI
                ↓
          Citations Emitted
```

## Configuration (Valves)

### Required API Keys

Set these in your `.env` file or configure in OpenWebUI:

```bash
EXA_API_KEY=your_exa_api_key_here
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### Valve Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `EXA_API_KEY` | env var | Exa API authentication key |
| `EXA_API_BASE_URL` | `https://api.exa.ai` | Exa API endpoint |
| `EXA_TEXT_PARAMETER` | `false` | Include full text content (uses more tokens) |
| `OPENROUTER_API_KEY` | env var | OpenRouter API authentication key |
| `OPENROUTER_API_BASE_URL` | `https://openrouter.ai/api/v1` | OpenRouter endpoint |
| `OPENROUTER_MODEL` | `anthropic/claude-3.5-sonnet` | Model to use via OpenRouter |
| `EMIT_SOURCES` | `true` | Show citation sources in UI |
| `TIMEOUT` | `60` | Request timeout in seconds |

### Popular OpenRouter Models

- `anthropic/claude-3.5-sonnet` (default)
- `openai/gpt-4-turbo`
- `openai/gpt-4o`
- `google/gemini-pro`
- `meta-llama/llama-3.1-70b-instruct`

## How It Works

### 1. Conversation Context Management

The agent receives the full conversation history:

```python
# Previous messages are formatted for context
conversation_context = """
Previous conversation:

User: What is quantum computing?
Assistant: Quantum computing uses quantum mechanics...

User: How does it compare to classical computing?
"""
```

The agent can reference previous exchanges when answering follow-up questions.

### 2. Agent Decision Making

The CrewAI agent autonomously decides:
- Does this query need web search?
- Do I need to search multiple times?
- Can I answer from conversation context alone?

### 3. Tool Calling

When search is needed:

```python
ExaAnswerTool(
    query="latest developments in quantum computing 2024"
)
→ Returns answer + citations
```

### 4. Response Generation

The agent:
1. Analyzes the query in context
2. Searches if needed (multiple times if necessary)
3. Synthesizes information from search + context
4. Returns comprehensive answer

### 5. Citation Emission

Citations are automatically formatted and emitted to OpenWebUI:

```python
{
  "source": {
    "name": "[1] Article Title",
    "type": "web_search_results",
    "urls": ["https://example.com"]
  },
  "document": ["Preview text..."],
  "metadata": [{"source": "url", "author": "...", "publishedDate": "..."}]
}
```

## Example Conversations

### Single Query
```
User: What are the latest AI developments in 2024?

Agent: [Searches Exa] → [Returns comprehensive answer with sources]
```

### Multi-Turn Conversation
```
User: What is quantum computing?
Agent: [Searches] Quantum computing is...

User: How is it being used in practice?
Agent: [Searches again] Based on recent developments...

User: What about the challenges?
Agent: [May search or use previous context] The main challenges include...
```

### Multiple Searches
```
User: Compare the performance of quantum vs classical computers across different tasks

Agent: [Searches "quantum computer performance"]
       [Searches "classical computer benchmarks"]
       [Synthesizes both results]
       Returns comprehensive comparison...
```

## Installation

1. Ensure Python >=3.10
2. Dependencies are in `pyproject.toml`:
   - `crewai>=0.95.0`
   - `exa-py>=1.0.0`
   - `langchain-openai>=0.1.0`
   - `openai>=1.7.1,<2.0.0`

3. Set environment variables:
   ```bash
   export EXA_API_KEY="your_key"
   export OPENROUTER_API_KEY="your_key"
   ```

4. Add to OpenWebUI functions directory

## Usage in OpenWebUI

1. Navigate to **Settings** → **Functions**
2. Upload `exa_crewai_answer.py`
3. Configure valves (API keys, model selection)
4. The pipe appears as: **Exa CrewAI Answer**
5. Select it from the model dropdown

## Differences from Perplexity Pipe

| Feature | Perplexity Pipe | Exa CrewAI Pipe |
|---------|----------------|-----------------|
| Architecture | Direct API call | CrewAI agent orchestration |
| Context | One-shot per message | Full conversation history |
| Search Control | Always searches | Agent decides when to search |
| Multiple Searches | No | Yes, if agent determines needed |
| LLM Backend | Perplexity models | Configurable via OpenRouter |
| Tool Calling | N/A | CrewAI tool framework |

## Troubleshooting

### "EXA_API_KEY not provided"
Set the API key in valves or environment variable.

### "OPENROUTER_API_KEY not provided"
Set the OpenRouter API key in valves or environment variable.

### Agent not searching when expected
- Check the system prompt (agent decides autonomously)
- Verify EXA_API_KEY is valid
- Check logs for Exa API errors

### No citations appearing
- Set `EMIT_SOURCES` to `true` in valves
- Verify Exa API returned citations (check logs)
- Ensure the agent used the search tool

## Advanced Configuration

### Custom System Prompt

Override the default system prompt in OpenWebUI to change agent behavior:

```
You are an expert research assistant. Always search for current information
before answering questions about recent events or data.
```

### Adjusting Search Behavior

Modify the agent's `goal` and `backstory` in the code:

```python
agent = Agent(
    role="Research Assistant",
    goal="Your custom goal",
    backstory="Your custom backstory",
    tools=[exa_tool],
    llm=llm,
)
```

## API Costs

- **Exa API**: Pay per search query
- **OpenRouter**: Pay per token (varies by model)

Monitor usage in respective dashboards.

## Credits

Based on the Perplexity Sonar Manifold Pipe by yazon.
Adapted for Exa + CrewAI integration.
