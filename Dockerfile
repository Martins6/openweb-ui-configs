FROM ghcr.io/open-webui/open-webui:main

# Install only the specific dependencies we need that don't conflict with OpenWebUI
RUN pip install --no-cache-dir \
  "pydantic>=2.0.0" \
  "httpx[http2]>=0.24.0" \
  "openai>=1.7.1,<2.0.0"

# Expose port
EXPOSE 8080

# Use same entry point as base image
CMD ["bash", "start.sh"]
