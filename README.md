# OpenWebUI Configurations

This repository contains all the documentation and functions necessary to set up OpenWebUI properly.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Directory Structure](#directory-structure)
- [Available Functions](#available-functions)
- [Quick Reference](#quick-reference)
- [Testing Functions](#testing-functions)
- [Configuration](#configuration)
- [Docker Deployment](#docker-deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Resources](#resources)

## Overview

OpenWebUI is a self-hosted web interface for AI models. This repository provides:

- Custom pipes/valves (functions) for extending OpenWebUI functionality
- Comprehensive setup documentation
- Testing utilities for function development

## Installation

### Prerequisites

- Python 3.8+ (for local development)
- `uv` package manager (recommended)
- Docker & Docker Compose (for containerized deployment)

### Setting Up OpenWebUI

#### Option 1: Docker with Custom Dependencies (Recommended)

This repository includes a custom Docker image with all dependencies pre-installed for both Perplexity and Exa functions.

```bash
# Quick start with Docker Compose
docker compose up -d

# Or use the update script (handles everything)
./update.sh
```

Access OpenWebUI at: **<http://localhost:3001>**

**Important Notes**:
- First startup may take 5-10 minutes for database initialization and model downloads
- All required dependencies are pre-installed
- Functions must still be added manually through the interface

#### Option 2: Standard Docker Installation

```bash
docker run -d -p 3000:8080 --name open-webui ghcr.io/open-webui/open-webui:main
```

**Limitation**: You'll need to manually install dependencies for custom functions.

#### Option 3: Local Python Installation

```bash
# Install OpenWebUI
pip install open-webui

# Install project dependencies for custom functions
cd /path/to/openweb-ui-configs
uv sync

# Start OpenWebUI
open-webui serve
```

#### Installing Custom Functions

After setting up OpenWebUI:

1. Access the interface at `http://localhost:3001` (custom Docker) or `http://localhost:3000` (standard)
2. Complete the initial setup wizard
3. Navigate to **Settings → Functions**
4. Click **"+"** to add a new function
5. Copy/paste the entire content from any `.py` file in the `functions/` directory
6. Configure the valve settings with your API keys and preferences
7. Save and test the function

**Critical**: Functions must be added manually through the OpenWebUI interface. The custom Docker image only provides the runtime dependencies.

## Directory Structure

```
openweb-ui-configs/
├── README.md          # This file
├── CLAUDE.md          # Claude-specific development instructions
├── pyproject.toml     # Python project configuration with dependencies
├── Dockerfile         # Custom OpenWebUI image with dependencies
├── update.sh          # Script to update OpenWebUI with dependencies
├── .python-version    # Python version specification
├── .gitignore         # Git ignore rules
├── uv.lock           # Dependency lock file
└── functions/         # OpenWebUI pipes/valves
    ├── test_valve.py  # Generic testing script for all functions
    ├── perplexity_sonar_api_with_citations.py  # Perplexity Sonar integration
    └── exa_openrouter_direct.py  # Exa + OpenRouter direct integration
```

## Available Functions

### Perplexity Sonar Manifold Pipe

**File**: `functions/perplexity_sonar_api_with_citations.py`

**Description**: Integrates Perplexity AI's Sonar models with OpenWebUI, providing web search capabilities with citations.

**Models Available**:

- Sonar
- Sonar Pro
- Sonar Reasoning
- Sonar Reasoning Pro
- Sonar Deep Research
- R1-1776 Offline

**Required Configuration**:

- `PERPLEXITY_API_KEY`: Your Perplexity API key (required)
- `PERPLEXITY_API_BASE_URL`: API base URL (default: <https://api.perplexity.ai>)
- `RETURN_IMAGES`: Whether to return images in responses (default: false)
- `EMIT_SOURCES`: Whether to emit citation sources (default: true)
- `SEARCH_RECENCY_FILTER`: Time filter for results (month/week/day/hour/none)
- `SEARCH_CONTEXT_SIZE`: Amount of context to retrieve (low/medium/high/none)

**Usage**:

1. Get an API key from [Perplexity AI](https://www.perplexity.ai/)
2. Add the function to OpenWebUI
3. Configure the valve settings with your API key
4. Select a Sonar model from the model dropdown
5. Start chatting - citations will appear automatically


### Exa OpenRouter Direct Answer Pipe

**File**: `functions/exa_openrouter_direct.py`

**Description**: Direct integration of Exa search APIs with OpenRouter's native tool calling for fast, lean web search and code documentation retrieval.

**Version**: 0.1.0
**Author**: adrielmartins

**Available Tools**:

- **Exa Answer Search**: General web search for current events and information
- **Exa Context Search**: Specialized search for code documentation, GitHub repos, and Stack Overflow

**Required Configuration**:

- `EXA_API_KEY`: Your Exa API key (required)
- `OPENROUTER_API_KEY`: Your OpenRouter API key for LLM access (required)
- `EXA_API_BASE_URL`: Exa API base URL (default: https://api.exa.ai)
- `OPENROUTER_API_BASE_URL`: OpenRouter API base URL (default: https://openrouter.ai/api/v1)
- `OPENROUTER_MODEL`: Model to use via OpenRouter (default: moonshotai/kimi-k2-thinking)
- `EXA_TEXT_PARAMETER`: Whether to include full text content (default: false)
- `EXA_CONTEXT_TOKENS_NUM`: Number of tokens for context search (default: 5000)
- `EMIT_SOURCES`: Whether to emit citation sources (default: true)
- `TIMEOUT`: Request timeout in seconds (default: 60)

**Usage**:

1. Get API keys from [Exa AI](https://exa.ai/) and [OpenRouter](https://openrouter.ai/)
2. Add the function to OpenWebUI
3. Configure the valve settings with both API keys
4. Select the "Exa OpenRouter Direct" model from the dropdown
5. Start chatting - the system will automatically choose the best search tool based on your query

**Recommended Models via OpenRouter**:

- `moonshotai/kimi-k2-thinking` - Excellent for research and analysis (default)
- `anthropic/claude-3.5-sonnet` - Great for technical questions
- `openai/gpt-4-turbo` - Good all-around performance

**Benefits over CrewAI version**:

- **60% smaller codebase** (~220 lines vs 550 lines)
- **Faster execution** with direct API calls
- **No CrewAI dependency** - leaner and more direct
- **Native tool calling** through OpenRouter
- **Same functionality** with context handling and citations

## Quick Reference

| Function | File | Required API Keys | Special Features |
|----------|------|-------------------|------------------|
| Perplexity Sonar | `perplexity_sonar_api_with_citations.py` | PERPLEXITY_API_KEY | Web search with citations, multiple Sonar models |
| Exa OpenRouter Direct | `exa_openrouter_direct.py` | EXA_API_KEY, OPENROUTER_API_KEY | Fast direct tool calling, code documentation focus, 60% smaller |
## Testing Functions

Use the generic test script to test any function locally before deploying to OpenWebUI:

```bash
# Run the interactive test script
uv run functions/test_valve.py
```

The test script will:

1. Discover all functions in the `functions/` directory
2. Let you select which function to test
3. Prompt you to configure all valve settings
4. If the function supports multiple models/pipes, let you choose one
5. Accept a test message
6. Display the streaming response with citations/sources

**Example Sessions**:

### Testing Perplexity Sonar
```
Available functions:
1. perplexity_sonar_api_with_citations.py
2. exa_crewai_answer.py

Select function [1]: 1

Configure Valves:
PERPLEXITY_API_KEY: pplx-xxxxx
RETURN_IMAGES [False]:
EMIT_SOURCES [True]:
SEARCH_RECENCY_FILTER [none]: day
SEARCH_CONTEXT_SIZE [none]: medium

Available pipes:
1. Sonar
2. Sonar Pro
3. Sonar Reasoning
...

Select pipe [1]: 2

Enter your test message: What are the latest developments in AI?

[Streaming response appears here with citations]
```

### Testing Exa OpenRouter Direct
```
Select function [1]: 2

Configure Valves:
EXA_API_KEY: your_exa_key_here
OPENROUTER_API_KEY: your_openrouter_key_here
OPENROUTER_MODEL [moonshotai/kimi-k2-thinking]:
EMIT_SOURCES [True]:
TIMEOUT [60]:

Available pipes:
1. Exa OpenRouter Direct

Select pipe [1]: 1

Enter your test message: How do I implement async/await in Python?

[Streaming response appears here with code examples and sources]
```

## Configuration

### Installing Dependencies

Before testing functions locally, install the required dependencies:

```bash
uv sync
```

This will install:

- `pydantic>=2.0.0` - For valve configuration models
- `httpx[http2]>=0.24.0` - For HTTP/API calls with HTTP/2 support
- `openai>=1.7.1,<2.0.0` - OpenAI API client
- `crewai>=0.95.0` - AI agent framework
- `exa-py>=1.0.0` - Exa search API
- `langchain-openai>=0.1.0` - LangChain OpenAI integration
- `litellm>=1.56.4` - LLM proxy and gateway

### Valve Configuration

Each function has its own valve configuration. See the function's docstring for available options.

### Valve Configuration

Each function has its own valve configuration. See the function's docstring for available options.

### Testing Utilities

The `functions/test_valve.py` script provides a comprehensive testing environment that:
- Discovers all available functions automatically
- Provides interactive configuration for valve settings
- Supports both streaming and non-streaming modes
- Handles citation/source display
- Works with multiple pipes/models per function

When deploying to OpenWebUI, the real OpenWebUI modules are used instead of the testing utilities.

## Docker Deployment

This repository includes a custom Docker setup that extends OpenWebUI with all project dependencies pre-installed.

### Quick Start

```bash
# Using Docker Compose (easiest)
docker-compose up -d

# Or use the update script (recommended for ongoing use)
./update.sh
```

### Available Scripts

#### `update.sh` - Complete Update Process (Recommended)

**What it does:**

- Stops and removes existing container
- Pulls latest OpenWebUI base image
- Rebuilds custom image with your dependencies
- Starts new container with updated image

**When to use:**

- First-time setup
- Updating OpenWebUI to new versions
- Complete redeployment

```bash
./update.sh
```

#### `build.sh` - Image Building Only

**What it does:**

- Pulls latest OpenWebUI base image
- Builds custom image with dependencies
- **Does NOT** touch running containers

**When to use:**

- Just rebuilding dependencies
- Development when you don't want downtime
- Creating image without deployment

```bash
./build.sh
```

### Which Script to Use?

- **For production/regular use**: Always use `./update.sh` - it handles everything and includes the build step
- **For development**: Use `./build.sh` when frequently changing dependencies to avoid container restarts

### Container Details

- **Image**: `open-webui-custom:latest`
- **Port**: `3001` (host) → `8080` (container)
- **Data Volume**: `open-webui` mounted to `/app/backend/data`
- **Python Version**: 3.12
- **Ollama Integration**: Pre-configured for local Ollama at `http://host.docker.internal:11434`

### Pre-installed Dependencies

The custom image includes all dependencies from `pyproject.toml`:

- `pydantic>=2.0.0` - Valve configuration models
- `httpx[http2]>=0.24.0` - HTTP/API calls with HTTP/2
- `openai>=1.7.1,<2.0.0` - OpenAI API client

**Note**: These dependencies are available for use in custom functions, but functions must be added manually through the OpenWebUI interface.

### Manual Docker Commands

If you prefer manual control:

```bash
# Build image
docker build -t open-webui-custom:latest .

# Run container
docker run -d \
  -p 3001:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  --name open-webui \
  --restart always \
  open-webui-custom:latest
```

## Contributing

### Adding New Functions

1. Create a new Python file in `functions/` directory
2. Follow the OpenWebUI pipe/valve structure:

   ```python
   class Pipe:
       class Valves(BaseModel):
           # Your configuration options
           pass

       def pipes(self):
           # Return available models/pipes
           pass

       async def pipe(self, body, __event_emitter__=None):
           # Your implementation
           pass
   ```

3. Test using `uv run functions/test_valve.py`
4. Document in this README under [Available Functions](#available-functions)
5. Commit your changes

### Documentation Standards

All functions must follow the code style and standards defined in `CLAUDE.md`:

- Include proper module-level docstring with title, author, author_url, funding_url, and version
- Add comprehensive docstrings for the `Valves` class explaining each configuration option
- Use type hints throughout the code
- Follow async/await patterns for API calls
- Handle errors gracefully with try/except blocks
- Test both streaming and non-streaming modes when applicable
- Verify citation/source handling if applicable

### Adding New Functions Workflow

1. Create new function in `functions/` directory following OpenWebUI pipe/valve structure
2. Test using `uv run functions/test_valve.py`
3. Update README.md with function documentation under [Available Functions](#available-functions)
4. Update the [Quick Reference](#quick-reference) table
5. Add any new dependencies to `pyproject.toml` if needed
6. Commit with clear description of what the function does

## Troubleshooting

### Common Issues and Solutions

**Function Not Appearing in OpenWebUI**
- Ensure the function code is properly copied into the OpenWebUI interface
- Check that all required dependencies are installed in the Docker image
- Verify the function follows the correct OpenWebUI pipe/valve structure

**API Key Errors**
- Double-check API keys are correctly entered in valve settings
- Ensure API keys have the required permissions
- Verify API endpoints are accessible from your network

**Timeout Issues**
- Increase the TIMEOUT valve setting for slower APIs
- Check network connectivity to external services
- Consider using faster models for testing

**Citation/Source Issues**
- Ensure EMIT_SOURCES is set to true in valve settings
- Check that the API returns citation data
- Verify the function properly processes citation metadata

**Docker Build Failures**
- Run `./update.sh` to rebuild with latest dependencies
- Check that `pyproject.toml` has correct dependency versions
- Ensure Docker has sufficient disk space

### Getting Help

- Check the function logs in OpenWebUI interface
- Test functions locally using `uv run functions/test_valve.py`
- Review the documentation for specific API requirements

## Resources

### OpenWebUI
- [OpenWebUI Documentation](https://docs.openwebui.com/)
- [OpenWebUI GitHub](https://github.com/open-webui/open-webui)

### API Documentation
- [Perplexity AI API](https://docs.perplexity.ai/)
- [Exa AI API](https://docs.exa.ai/)
- [OpenRouter API](https://openrouter.ai/docs)


### Development Tools
- [UV Package Manager](https://github.com/astral-sh/uv)
- [Docker Documentation](https://docs.docker.com/)
- [Python Async/Await](https://docs.python.org/3/library/asyncio.html)

## License

See individual function files for licensing information.
