#!/bin/bash
# ==============================================================================
# Spotify Trends: Unified Local Startup Script
# Starts both the Streamlit Analytics Studio and the Next.js Music Platform
# ==============================================================================

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_ROOT"

echo "======================================================="
echo "🎵  STARTING SPOTIFY TRENDS (LOCAL ACADEMIC SUBMISSION) "
echo "======================================================="

# Function to check if a port is in use
is_port_in_use() {
  lsof -i :"$1" >/dev/null 2>&1
}

# 1. Dependency checks
if [ ! -d ".venv" ] && [ ! -d "venv" ]; then
  echo "⚠️  Python virtual environment not found. Creating .venv..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install --quiet -r analytics/requirements.txt -r pipeline/requirements.txt
fi

VENV_STREAMLIT=""
if [ -f ".venv/bin/streamlit" ]; then
  VENV_STREAMLIT=".venv/bin/streamlit"
elif [ -f "venv/bin/streamlit" ]; then
  VENV_STREAMLIT="venv/bin/streamlit"
elif command -v streamlit >/dev/null 2>&1; then
  VENV_STREAMLIT="$(command -v streamlit)"
else
  echo "❌ Error: streamlit executable not found in .venv or PATH."
  exit 1
fi

if [ ! -d "web/node_modules" ]; then
  echo "📦 Installing web dependencies..."
  (cd web && npm install --silent)
fi

# Ensure web build exists for fast production start
if [ ! -d "web/.next" ]; then
  echo "⚡ Building Next.js application..."
  (cd web && npm run build)
fi

# 2. Cleanup handler for graceful shutdown
STREAMLIT_PID=""
NEXTJS_PID=""

cleanup() {
  echo ""
  echo "🛑 Stopping Spotify Trends services..."
  if [ -n "$STREAMLIT_PID" ]; then
    kill "$STREAMLIT_PID" 2>/dev/null || true
  fi
  if [ -n "$NEXTJS_PID" ]; then
    kill "$NEXTJS_PID" 2>/dev/null || true
  fi
  # Also kill by port to be 100% clean
  kill $(lsof -ti :8501) 2>/dev/null || true
  kill $(lsof -ti :3000) 2>/dev/null || true
  echo "✅ All services stopped."
  exit 0
}

trap cleanup INT TERM

# 3. Start Streamlit (port 8501)
if is_port_in_use 8501; then
  echo "ℹ️  Port 8501 is already occupied. Reusing existing Streamlit process."
else
  echo "🚀 Starting Streamlit Analytics Studio on port 8501..."
  "$VENV_STREAMLIT" run analytics/app.py \
    --server.port 8501 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false \
    --browser.gatherUsageStats false \
    > /tmp/spotify_trends_streamlit.log 2>&1 &
  STREAMLIT_PID=$!
fi

# 4. Start Next.js (port 3000)
if is_port_in_use 3000; then
  echo "ℹ️  Port 3000 is already occupied. Reusing existing Next.js process."
else
  echo "🚀 Starting Next.js Music Platform on port 3000..."
  (cd web && exec npx next start -p 3000) > /tmp/spotify_trends_nextjs.log 2>&1 &
  NEXTJS_PID=$!
fi

# 5. Wait for both servers to be responsive
echo "⏳ Waiting for services to become ready..."
for i in {1..30}; do
  STREAMLIT_READY=0
  NEXTJS_READY=0

  if curl -s -f http://localhost:8501/_stcore/health >/dev/null 2>&1; then
    STREAMLIT_READY=1
  fi

  if curl -s -f http://localhost:3000 >/dev/null 2>&1; then
    NEXTJS_READY=1
  fi

  if [ $STREAMLIT_READY -eq 1 ] && [ $NEXTJS_READY -eq 1 ]; then
    break
  fi
  sleep 0.5
done

echo ""
echo "======================================================="
echo "✨ SPOTIFY TRENDS IS LIVE AND READY!"
echo "======================================================="
echo ""
echo "  🎧 Music Streaming App : http://localhost:3000"
echo "  📊 Analytics Studio    : http://localhost:8501"
echo "  🔗 Integrated Viewer   : http://localhost:3000/analytics"
echo ""
echo "Press Ctrl+C to stop both applications."
echo "======================================================="

# Keep script running and wait for background jobs
if [ -n "$STREAMLIT_PID" ] && [ -n "$NEXTJS_PID" ]; then
  wait "$STREAMLIT_PID" "$NEXTJS_PID"
elif [ -n "$STREAMLIT_PID" ]; then
  wait "$STREAMLIT_PID"
elif [ -n "$NEXTJS_PID" ]; then
  wait "$NEXTJS_PID"
else
  # If both were already running, wait on a sleep loop
  while true; do
    sleep 1
  done
fi
