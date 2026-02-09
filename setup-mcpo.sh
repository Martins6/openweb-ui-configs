#!/bin/bash

# Setup script for mcpo configuration
# This script reads .env file and generates mcpo-config.json with actual API keys

set -e

# Load environment variables from .env file if it exists
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found!"
    echo "Please copy .env.example to .env and fill in your API keys."
    exit 1
fi

# Check if EXA_API_KEY is set
if [ -z "${EXA_API_KEY}" ]; then
    echo "Error: EXA_API_KEY is not set in .env file!"
    exit 1
fi

# Generate mcpo-config.json with actual API key
cat > mcpo-config.json <<EOF
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
EOF

echo "✓ mcpo-config.json has been generated with your API key from .env"
echo "✓ Ready to start mcpo service!"
