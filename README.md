# OpenWebUI Configurations

This repository contains all the documentation and functions necessary to set up OpenWebUI properly.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Directory Structure](#directory-structure)
- [Available Functions](#available-functions)
- [Testing Functions](#testing-functions)
- [Configuration](#configuration)
- [Contributing](#contributing)

## Overview

OpenWebUI is a self-hosted web interface for AI models. This repository provides:

- Custom pipes/valves (functions) for extending OpenWebUI functionality
- Comprehensive setup documentation
- Testing utilities for function development

## Installation

### Prerequisites

- Python 3.8+
- `uv` package manager (recommended)

### Setting Up OpenWebUI

1. **Install OpenWebUI** (choose one method):

   ```bash
   # Using Docker (recommended)
   docker run -d -p 3000:8080 --name open-webui ghcr.io/open-webui/open-webui:main

   # Or using pip
   pip install open-webui
   open-webui serve
   ```

2. **Access the interface**:
   - Navigate to `http://localhost:3000`
   - Complete initial setup

3. **Install custom functions**:
   - In OpenWebUI, go to Settings → Functions
   - Click "+" to add a new function
   - Copy/paste the content from any `.py` file in the `functions/` directory
   - Configure the valve settings (API keys, options, etc.)

## Directory Structure

```
openweb-ui-configs/
├── CLAUDE.md          # Claude Code specific instructions
├── README.md          # This file
├── pyproject.toml     # Python project configuration with dependencies
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

