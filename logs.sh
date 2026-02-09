#!/bin/bash

if [ -z "$1" ]; then
  echo "Viewing logs for all services (Ctrl+C to exit)..."
  echo ""
  docker compose logs -f
else
  echo "Viewing logs for $1 (Ctrl+C to exit)..."
  echo ""
  docker compose logs -f "$1"
fi
