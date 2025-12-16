FROM ghcr.io/open-webui/open-webui:main

# Install only the specific dependencies we need that don't conflict with OpenWebUI
# Skip langchain-openai to avoid conflicts - CrewAI will use OpenAI directly
RUN pip install --no-cache-dir \
  "pydantic>=2.0.0" \
  "httpx[http2]>=0.24.0" \
  "openai>=1.7.1,<2.0.0" \
  "crewai>=0.95.0" \
  "exa-py>=1.0.0" \
  "litellm>=1.56.4" \
  "langchain-openai>=0.1.0"

# Expose port
EXPOSE 8080

# Use same entry point as base image
CMD ["bash", "start.sh"]
