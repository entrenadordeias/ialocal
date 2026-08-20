#!/usr/bin/env bash
# ==============================================================================
# Script de Estado - Stack Local de IA
# ==============================================================================

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "=========================================================="
echo "📊 ESTADO DEL STACK LOCAL DE IA"
echo "=========================================================="

echo ""
echo "--- 1. Servicios y Puertos ---"
# Ollama
if pgrep -f "ollama serve" > /dev/null; then
    echo "🟢 Ollama:       ACTIVO  (PID: $(pgrep -f 'ollama serve' | tr '\n' ' ')) -> http://localhost:11434"
else
    echo "🔴 Ollama:       DETENIDO"
fi

# Open WebUI
if pgrep -f "open-webui serve" > /dev/null; then
    echo "🟢 Open WebUI:   ACTIVO  (PID: $(pgrep -f 'open-webui serve' | tr '\n' ' ')) -> http://localhost:3000"
else
    echo "🔴 Open WebUI:   DETENIDO"
fi

# n8n
if pgrep -f "n8n start" > /dev/null; then
    echo "🟢 n8n:          ACTIVO  (PID: $(pgrep -f 'n8n start' | tr '\n' ' ')) -> http://localhost:5678"
else
    echo "🔴 n8n:          DETENIDO"
fi

echo ""
echo "--- 2. Modelos Instalados en Ollama ---"
export HOME="$PROJECT_DIR/home"
export OLLAMA_HOST="127.0.0.1:11434"
export PATH="$PROJECT_DIR/bin:$PATH"
if command -v ollama >/dev/null 2>&1; then
    "$PROJECT_DIR/bin/ollama" list 2>/dev/null || echo "Ollama no responde o no está disponible."
fi

echo ""
echo "--- 3. Recursos de GPU (VRAM) ---"
if command -v nvidia-smi >/dev/null 2>&1; then
    nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader
fi

echo ""
echo "--- 4. Memoria RAM del Sistema ---"
free -h | awk 'NR==1{print $0} NR==2{print $0}'

echo "=========================================================="
