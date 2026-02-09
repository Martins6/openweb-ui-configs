#!/bin/bash

echo "Restarting OpenWebUI and mcpo services..."
docker compose restart
echo ""
echo "✓ Services restarted!"
echo ""
echo "🌐 OpenWebUI: http://localhost:3000"
echo "🔧 mcpo API: http://localhost:8010"
