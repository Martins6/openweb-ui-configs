# OpenWebUI Configurations

This repository contains all the documentation and functions necessary to set up OpenWebUI properly.

## Table of Contents

- [Overview](#overview)
- [Quick Start - MCP Integration](#quick-start-mcp) ⭐ NEW
- [Installation](#installation)
- [Directory Structure](#directory-structure)
- [Available Functions](#available-functions)
- [Quick Reference](#quick-reference)
- [Testing Functions](#testing-functions)
- [Configuration](#configuration)
- [Docker Deployment](#docker-deployment)
- [MCP Integration](#mcp-integration)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Resources](#resources)

## Overview

OpenWebUI is a self-hosted web interface for AI models. This repository provides:

- Custom pipes/valves (functions) for extending OpenWebUI functionality
- Comprehensive setup documentation
- Testing utilities for function development

## Quick Start - MCP Integration ⭐ NEW

**This is the fastest way to get Exa MCP tools running with OpenWebUI.**

### Step-by-Step (3 commands total):

```bash
# Step 1: Copy environment template and add your API keys
cp .env.example .env

# Step 2: Edit .env and add your actual API keys
# - EXA_API_KEY: Get from https://exa.ai/
# - WEBUI_SECRET_KEY: Generate with: openssl rand -hex 32
# - MCPO_API_KEY: Generate with: openssl rand -hex 16

# Step 3: Generate mcpo configuration file
./setup-mcpo.sh

# Step 4: Start both OpenWebUI and mcpo services
./start.sh
```

**That's it! Now access:**
- 🌐 **OpenWebUI**: http://localhost:3000
- 🔧 **mcpo API Docs**: http://localhost:8010/docs

### Step 5: Connect OpenWebUI to mcpo (one-time setup)

After services start, configure the connection in OpenWebUI's web interface:

**Important:** Each MCP server configured in mcpo-config.json requires its own external tool configuration in OpenWebUI. The URL pattern is: `http://mcpo:8000/<mcp-name>`

1. Open http://localhost:3000 in your browser
2. Click ⚙️ (Settings) → Admin Panel → **External Tools**
3. Click **+ (Add Server)**
4. Fill in for the **Exa** MCP server:
   - **Name**: `Exa MCP Tools` (or any name you like)
   - **Type**: **OpenAPI** (⚠️ NOT "MCP")
   - **URL**: `http://mcpo:8000/exa` (base URL + MCP server name)
   - **Auth**: **Bearer Token**
   - **API Token**: Copy `MCPO_API_KEY` value from your `.env` file
5. Click **Save**

**If you have multiple MCP servers** (e.g., exa and context7), repeat steps 3-4 for each server with their respective URLs:
- Exa: `http://mcpo:8000/exa`
- Context7: `http://mcpo:8000/context7`

**✅ Done!** Your Exa MCP tools are now available in OpenWebUI chats.

### Step 6: Configure Model Settings (Important)

For optimal tool calling with external MCP tools, configure your model settings:

1. Open a new chat
2. Click on the model settings (gear icon) or model selector
3. Configure the following:
   - **Enable "Built-in Tools"**: Toggle this ON. Even though you are using an external tool, this toggle often acts as the master switch for the injection logic.
   - **Set Tool Calling Mode to "Native"**: Most models (including GLM-4.7) are fully OpenAI-compatible for tool calling. If set to "Compatibility" or "Default," OpenWebUI might try to use a ReAct prompt which the model might ignore in favor of its own internal "Thinking" blocks.

### Why This Works:

1. **mcpo container starts** - Runs the Exa MCP server (npx exa-mcp-server)
2. **OpenWebUI container starts** - Connects to mcpo via Docker network
3. **Docker network** - Both containers can communicate as `http://mcpo:8000/<mcp-name>`
4. **OpenWebUI discovers tools** - Shows `crawling_exa`, `get_code_context_exa`, `web_search_exa`

### Important Notes:

⚠️ **mcpo MUST be running before connecting** - OpenWebUI will fail to connect if mcpo isn't started first

🔐 **Use container URL** - When adding the connection in OpenWebUI, use `http://mcpo:8000/<mcp-name>` (the internal Docker network URL with the MCP server name), NOT `http://localhost:8010`

🔑 **Secure your keys** - Never commit `.env` or `mcpo-config.json` to git (both are in .gitignore)

---

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

**Note:** Port numbers:
- **MCP Integration** (docker compose): Uses port 3000
- **Single Container** (update.sh): Uses port 3001 (old approach)

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

| Function              | File                                     | Required API Keys               | Special Features                                                |
| --------------------- | ---------------------------------------- | ------------------------------- | --------------------------------------------------------------- |
| Perplexity Sonar      | `perplexity_sonar_api_with_citations.py` | PERPLEXITY_API_KEY              | Web search with citations, multiple Sonar models                |
| Exa OpenRouter Direct | `exa_openrouter_direct.py`               | EXA_API_KEY, OPENROUTER_API_KEY | Fast direct tool calling, code documentation focus, 60% smaller |

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

**Option 1: Docker Compose with MCP Integration (Recommended for MCP)**

This approach uses docker compose to orchestrate both OpenWebUI and mcpo, enabling MCP tools like Exa search.

```bash
# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Generate mcpo configuration
./setup-mcpo.sh

# Start services
./start.sh
```

Access OpenWebUI at: **<http://localhost:3000>**

For detailed MCP setup instructions, see [MCP Integration](#mcp-integration).

**Option 2: Single Container (No MCP)**

This uses direct Docker commands for a simple, single-container setup.

```bash
# Using Docker Compose
docker compose up -d

# Or use the update script
./update.sh
```

Access OpenWebUI at: **<http://localhost:3001>** (or :3000 if using docker compose)

**Note:** This approach doesn't include MCP tools. For MCP integration, use Option 1.

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

- **For MCP integration**: Use the new docker compose approach (see [MCP Integration](#mcp-integration)) with `./start.sh`, `./stop.sh`, `./restart.sh`, and `./logs.sh`
- **For production/regular use (single container)**: Use `./update.sh` - it handles everything and includes the build step
- **For development**: Use `./build.sh` when frequently changing dependencies to avoid container restarts

### Container Details

**Docker Compose (MCP Integration):**
- **Image**: `open-webui-custom:latest` (OpenWebUI), `ghcr.io/open-webui/mcpo:main` (mcpo)
- **Ports**:
  - `3000` (host) → `8080` (container, OpenWebUI)
  - `8010` (host) → `8000` (container, mcpo)
- **Data Volume**: `open-webui` mounted to `/app/backend/data`
- **Network**: `openwebui-network` (shared between containers)
- **Restart Policy**: `always` (automatic restart on system reboot)
- **Configuration File**: `docker-compose.yml` (defines both services)

**Single Container (update.sh) - Legacy:**
- **Image**: `open-webui-custom:latest`
- **Port**: `3001` (host) → `8080` (container) - ⚠️ Different port!
- **Data Volume**: `open-webui` mounted to `/app/backend/data`
- **Restart Policy**: `always`
- **Configuration**: Direct Docker commands (no docker-compose.yml)

**Common for both:**
- **Python Version**: 3.12
- **Ollama Integration**: Pre-configured for local Ollama at `http://host.docker.internal:11434`

**Common for both:**

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

**Docker Compose (MCP Integration):**

```bash
# Build OpenWebUI image
docker build -t open-webui-custom:latest .

# Start all services
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f

# Restart services
docker compose restart
```

**Single Container:**

```bash
# Build image
docker build -t open-webui-custom:latest .

# Run container
docker run -d \
  -p 3000:8080 \
  --add-host=host.docker.internal:host-gateway \
  -v open-webui:/app/backend/data \
  -v ./functions:/app/custom-functions/functions \
  --name open-webui \
  --restart always \
  open-webui-custom:latest
```

## MCP Integration

This section covers setting up Model Context Protocol (MCP) tools using the mcpo proxy, allowing you to use Exa's powerful search capabilities directly within OpenWebUI.

### Overview

**What is MCP?**

Model Context Protocol (MCP) is an open standard from Anthropic that allows AI assistants to connect to external data sources and tools through a unified interface. MCP servers communicate via stdio, SSE (Server-Sent Events), or Streamable HTTP.

**What is mcpo?**

[mcpo](https://github.com/open-webui/mcpo) is an MCP-to-OpenAPI proxy server that converts MCP servers into standard HTTP/OpenAPI endpoints. This is essential because:

- Most MCP servers use stdio (local command-line communication)
- Docker containers can't easily access host machine stdio processes
- mcpo bridges this gap by translating stdio to HTTP
- OpenWebUI can then connect via standard OpenAPI (or native MCP Streamable HTTP)

**Architecture:**

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────┐
│   OpenWebUI    │◄──────►│    mcpo      │◄──────►│  Exa MCP    │
│  (Docker)      │         │  (Docker)     │         │  (npx)       │
│  Port: 3000     │         │  Port: 8010   │         │  Tools:       │
│                 │         │               │         │  - Search     │
│  + Functions     │         │  Proxies:     │         │  - Code Docs  │
└─────────────────┘         │  - stdio      │         │  - Web       │
                           │  - HTTP       │         └─────────────┘
                           └──────────────┘
```

### Prerequisites

**Required:**
- Docker & Docker Compose V2
- EXA_API_KEY from [Exa AI](https://exa.ai/)

**Software Versions:**
- OpenWebUI `:main` tag includes MCP support (v0.6.31+, confirmed January 2026)
- mcpo runs automatically with docker compose

### Quick Start

**👆 See the complete step-by-step guide at the top of this document: [Quick Start - MCP Integration](#quick-start-mcp)**

This section provides detailed information about each component. If you've already completed the Quick Start, proceed to [Manual Setup](#manual-setup) to connect OpenWebUI to mcpo.

### Configuration

#### Environment Variables

Create `.env` file with the following variables:

```bash
# OpenWebUI Configuration
WEBUI_PORT=3000                          # Port to access OpenWebUI
WEBUI_SECRET_KEY=<your-secret-key>         # Required for MCP auth persistence

# MCPo Configuration
MCPO_PORT=8010                            # Port to access mcpo
MCPO_API_KEY=<your-mcpo-api-key>          # API key to secure mcpo endpoint

# API Keys
EXA_API_KEY=your_exa_api_key_here           # Exa API key for search tools
PERPLEXITY_API_KEY=your_perplexity_api_key   # Perplexity API key (optional)
```

**Generating Secure Keys:**

```bash
# Generate WEBUI_SECRET_KEY (32 hex characters)
openssl rand -hex 32

# Generate MCPO_API_KEY (16 hex characters)
openssl rand -hex 16
```

**Important:** The `.env` file is in `.gitignore` and should never be committed to version control. Use `.env.example` as a template.

#### mcpo Configuration

The `mcpo-config.json` file defines which MCP servers to expose. For this setup, we configure the Exa MCP server:

```json
{
  "mcpServers": {
    "exa": {
      "command": "npx",
      "args": [
        "-y",
        "exa-mcp-server",
        "tools=crawling_exa,get_code_context_exa,web_search_exa"
      ],
      "env": {
        "API_TOKEN": "${EXA_API_KEY}"
      }
    }
  }
}
```

**Available Exa Tools:**

- `crawling_exa` - Fetch full content from specific URLs
- `get_code_context_exa` - Search code documentation, GitHub repos, Stack Overflow
- `web_search_exa` - General web search for current events and information

**Auto-Generation:**

Run `./setup-mcpo.sh` to automatically generate `mcpo-config.json` with your actual API key from `.env`. This is recommended because:

- Keeps API key out of version control
- Easy to regenerate with updated keys
- Supports hot-reload for development

### Management Scripts

The following scripts help you manage the OpenWebUI and mcpo services:

- **`start.sh`** - Start all services via docker compose
- **`stop.sh`** - Stop all services
- **`restart.sh`** - Restart services (no downtime)
- **`logs.sh`** - View service logs (all or specific service)
- **`setup-mcpo.sh`** - Regenerate mcpo-config.json from .env

**Examples:**

```bash
# Start services
./start.sh

# View all logs
./logs.sh

# View only mcpo logs
./logs.sh mcpo

# Restart services after configuration changes
./restart.sh

# Stop services
./stop.sh
```

### Manual Setup <a id="manual-setup"></a>

After starting the services, you need to configure the MCP connection in OpenWebUI:

**Important:** Each MCP server configured in mcpo-config.json requires its own external tool configuration in OpenWebUI. The URL pattern is: `http://mcpo:8000/<mcp-name>` where `<mcp-name>` is the server name from your mcpo-config.json.

1. **Access OpenWebUI:**
    Navigate to http://localhost:3000

2. **Navigate to Admin Settings:**
    Click on the settings/gear icon → Admin Panel → External Tools

3. **Add MCP Server:**
    - Click **"+ (Add Server)**
    - Set **Name**: "Exa MCP Tools" (or any name you prefer)
    - Set **Type**: **OpenAPI** (NOT "MCP" - mcpo translates MCP to OpenAPI)
    - Set **URL**: `http://mcpo:8000/exa` (base URL + MCP server name from mcpo-config.json)
     - Set **Auth**: **Bearer Token**
     - Set **API Token**: Copy `MCPO_API_KEY` value from your `.env` file
     - Click **Save**
     - **If prompted to restart OpenWebUI**, run: `docker compose restart openwebui`

4. **Add Additional MCP Servers (if configured):**
    If you have multiple MCP servers in mcpo-config.json (e.g., exa, context7), repeat step 3 for each:
    - Exa: `http://mcpo:8000/exa`
    - Context7: `http://mcpo:8000/context7`
    - Each server gets its own external tool configuration with its specific URL

5. **Verify Connection:**
    - The connection should show as active/green
    - Click on the connection to see available tools
    - You should see: `crawling_exa`, `get_code_context_exa`, `web_search_exa`

6. **Enable Tools in Conversation:**
    - Start a new chat
    - Click on the "Tools" or "Plugins" icon in the chat interface
    - Enable the Exa tools you want to use
    - Some models automatically select appropriate tools

7. **Configure Model Settings:**
    For optimal tool calling with external MCP tools, configure your model settings:
    - **Enable "Built-in Tools"**: Toggle this ON. Even though you are using an external tool, this toggle often acts as the master switch for the injection logic.
    - **Set Tool Calling Mode to "Native"**: Most models (including GLM-4.7) are fully OpenAI-compatible for tool calling. If set to "Compatibility" or "Default," OpenWebUI might try to use a ReAct prompt which the model might ignore in favor of its own internal "Thinking" blocks.

8. **Test the Tools:**
    Try asking questions that would require web search:
    - "What are the latest developments in AI?"
    - "How do I implement async/await in Python?"
    - "Search for tutorials on Docker Compose"

### Using Exa MCP Tools

**Web Search (`web_search_exa`):**
Best for general questions, current events, and broad information retrieval.

Example prompts:

- "What's the weather like today?"
- "Latest news about technology"
- "Compare Python and JavaScript for web development"

**Code Documentation (`get_code_context_exa`):**
Specialized for technical documentation, GitHub repositories, and Stack Overflow.

Example prompts:

- "How does React useEffect work?"
- "Examples of Docker Compose configurations"
- "PostgreSQL connection pooling best practices"

**URL Crawling (`crawling_exa`):**
Fetches full content from specific URLs when you provide a URL.

Example prompts:

- "Summarize the content at https://example.com/docs/api"
- "Extract the key points from this article"

### Troubleshooting

#### Connection Issues Between Containers

**Problem:** OpenWebUI can't connect to mcpo
**Solution:**

- Check both containers are running: `docker ps`
- Verify network: `docker network inspect openwebui-configs_openwebui-network`
- Test connectivity: `docker exec open-webui ping mcpo`

#### API Key Problems

**Problem:** Tools fail with authentication errors
**Solutions:**

- Verify `.env` has correct `EXA_API_KEY` and `MCPO_API_KEY`
- Regenerate mcpo config: `./setup-mcpo.sh`
- Restart services: `./restart.sh`
- Check mcpo logs: `./logs.sh mcpo`

#### MCP Tools Not Appearing

**Problem:** Tools don't show up in OpenWebUI External Tools
**Solutions:**

- Verify mcpo is running: `curl http://localhost:8010/docs`
- Check mcpo logs for errors: `./logs.sh mcpo`
- Ensure URL is correct in OpenWebUI: `http://mcpo:8000/<mcp-name>` (not localhost, use internal port 8000)
- Verify Auth Token matches `MCPO_API_KEY` from `.env`

#### WEBUI_SECRET_KEY Issues

**Problem:** MCP connection breaks on container restart
**Solution:**

- Ensure `WEBUI_SECRET_KEY` is set in `.env` and passed to container
- This key is required for OpenWebUI to encrypt/decrypt MCP auth tokens
- If you change this key, you'll need to re-add the MCP connection in OpenWebUI

#### Hot-Reload Not Working

**Problem:** Changes to mcpo-config.json don't take effect
**Solutions:**

- Ensure `--hot-reload` flag is in docker-compose.yml file (it should be)
- Check mcpo logs: `./logs.sh mcpo` for reload messages
- Manually restart: `docker compose restart mcpo`

#### Port Conflicts

**Problem:** Port 3000 or 8010 already in use
**Solution:**

- Modify `WEBUI_PORT` or `MCPO_PORT` in `.env`
- Restart services: `./stop.sh && ./start.sh`

### Comparison: Old vs New Approach

**Old Approach (`update.sh`):**

- Single container with direct Docker commands
- Good for: Simple deployments, single-service setups
- Limited to: Basic OpenWebUI with custom functions

**New Approach (docker compose + mcpo):**

- Two services orchestrated by Docker Compose
- Better for: MCP tool integration, service orchestration, development
- Enables: Exa MCP tools, easy scaling, hot-reload, centralized config

**Recommendation:** Use the new docker compose approach for MCP integration. Keep `update.sh` for backwards compatibility and single-container deployments.

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
