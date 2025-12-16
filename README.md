# OpenWebUI Configurations

This repository contains all the documentation and functions necessary to set up OpenWebUI properly.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Directory Structure](#directory-structure)
- [Available Functions](#available-functions)
- [Testing Functions](#testing-functions)
- [Configuration](#configuration)
- [Docker Deployment](#docker-deployment)
- [Contributing](#contributing)

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

This repository includes a custom Docker image that comes with all dependencies pre-installed.

```bash
# Quick start with Docker Compose
docker compose up -d

# Or use the update script (handles everything)
./update.sh
```

Access OpenWebUI at: **http://localhost:3001**

**Note**: The first startup may take 5-10 minutes as OpenWebUI initializes its database and downloads models.

#### Option 2: Standard Docker Installation

```bash
docker run -d -p 3000:8080 --name open-webui ghcr.io/open-webui/open-webui:main
```

#### Option 3: Local Python Installation

```bash
pip install open-webui
open-webui serve
```

#### Installing Custom Functions

After setting up OpenWebUI:

1. Access the interface at `http://localhost:3001` (Docker) or `http://localhost:3000` (standard)
2. Complete initial setup
3. Go to Settings → Functions
4. Click "+" to add a new function
5. Copy/paste the content from any `.py` file in the `functions/` directory
6. Configure the valve settings (API keys, options, etc.)

**Important**: Functions must be added manually through the OpenWebUI interface. The custom Docker image provides the dependencies but does not auto-load functions.

## Directory Structure

```
openweb-ui-configs/
├── CLAUDE.md          # Claude Code specific instructions
├── README.md          # This file
├── DOCKER.md          # Docker deployment documentation
├── pyproject.toml     # Python project configuration with dependencies
├── Dockerfile         # Custom OpenWebUI image with dependencies
├── docker-compose.yml # Docker Compose configuration
├── build.sh           # Script to build custom image
├── update.sh          # Script to update OpenWebUI with dependencies
└── functions/         # OpenWebUI pipes/valves
    ├── open_webui/    # Mock OpenWebUI utilities for testing
    ├── test_valve.py  # Generic testing script for all functions
    └── *.py           # Individual pipe/valve functions
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

**Example Session**:

```
Available functions:
1. perplexity_sonar_api_with_citations.py

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

## Configuration

### Installing Dependencies

Before testing functions locally, install the required dependencies:

```bash
uv sync
```

This will install:
- `pydantic` - For valve configuration models
- `httpx` - For HTTP/API calls with HTTP/2 support

### Valve Configuration

Each function has its own valve configuration. See the function's docstring for available options.

### Mock OpenWebUI Utilities

The `functions/open_webui/` directory contains mock utilities that allow functions to run standalone for testing. These utilities replicate the behavior of OpenWebUI's internal modules:

- `open_webui.utils.misc.pop_system_message` - Extracts system messages from message lists

When deploying to OpenWebUI, the real OpenWebUI modules are used instead.

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
- `crewai>=0.95.0` - AI agent framework
- `exa-py>=1.0.0` - Exa search API
- `langchain-openai>=0.1.0` - LangChain OpenAI integration
- `litellm>=1.56.4` - LLM proxy and gateway

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

- Include docstrings for all classes and methods
- Add usage examples
- Document all configuration options
- Update README.md when adding functions

## Resources

- [OpenWebUI Documentation](https://docs.openwebui.com/)
- [OpenWebUI GitHub](https://github.com/open-webui/open-webui)
- [Perplexity AI API](https://docs.perplexity.ai/)

## License

See individual function files for licensing information.

