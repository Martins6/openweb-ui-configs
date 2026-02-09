#!/bin/bash

echo "Starting OpenWebUI and mcpo services..."
docker compose up -d
echo ""
echo "✓ Services started!"
echo ""
echo "🌐 OpenWebUI: http://localhost:3000"
echo "🔧 mcpo API: http://localhost:8010"
echo "📚 mcpo Docs: http://localhost:8010/docs"
echo ""
echo "To view logs, run: ./logs.sh"
echo "To stop services, run: ./stop.sh"
