#!/usr/bin/env bash
# ==============================================================================
# Script de Inicio - Stack Local de IA (Ollama + Open WebUI + n8n)
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOGS_DIR="$PROJECT_DIR/logs"
mkdir -p "$LOGS_DIR"

echo "=========================================================="
echo "🚀 Iniciando Stack Local de IA en $PROJECT_DIR"
echo "=========================================================="

# 1. Iniciar Ollama
if pgrep -f "ollama serve" > /dev/null; then
    echo "✅ [1/3] Ollama ya está en ejecución en el puerto 11434."
else
    echo "⏳ [1/3] Iniciando servidor Ollama (con aceleración GPU NVIDIA)..."
    export HOME="$PROJECT_DIR/home"
    export OLLAMA_HOST="0.0.0.0:11434"
    export OLLAMA_ORIGINS="*"
    export OLLAMA_MODELS="$PROJECT_DIR/models"
    export PATH="$PROJECT_DIR/bin:$PATH"

    nohup "$PROJECT_DIR/bin/ollama" serve > "$LOGS_DIR/ollama.log" 2>&1 &
    sleep 3
    echo "✅ [1/3] Ollama iniciado. Logs en: $LOGS_DIR/ollama.log"
fi

# 2. Iniciar Open WebUI
if pgrep -f "open-webui serve" > /dev/null; then
    echo "✅ [2/3] Open WebUI ya está en ejecución en el puerto 3000."
else
    echo "⏳ [2/3] Iniciando Open WebUI..."
    export DATA_DIR="$PROJECT_DIR/data/openwebui"
    export OLLAMA_BASE_URL="http://127.0.0.1:11434"
    export WEBUI_AUTH="False"
    export PORT=3000
    export HOST="0.0.0.0"

    nohup "$PROJECT_DIR/openwebui_env/bin/open-webui" serve --port 3000 --host 0.0.0.0 > "$LOGS_DIR/openwebui.log" 2>&1 &
    echo "✅ [2/3] Open WebUI iniciado en http://localhost:3000 (Logs en $LOGS_DIR/openwebui.log)"
fi

# 3. Iniciar n8n
if pgrep -f "n8n start" > /dev/null; then
    echo "✅ [3/3] n8n ya está en ejecución en el puerto 5678."
else
    echo "⏳ [3/3] Iniciando n8n..."
    export N8N_USER_FOLDER="$PROJECT_DIR/data/n8n"
    export N8N_PORT=5678
    export N8N_HOST="0.0.0.0"
    export N8N_LISTEN_ADDRESS="0.0.0.0"
    export PATH="$PROJECT_DIR/node_dist/bin:$PATH"

    nohup "$PROJECT_DIR/node_dist/bin/n8n" start > "$LOGS_DIR/n8n.log" 2>&1 &
    echo "✅ [3/3] n8n iniciado en http://localhost:5678 (Logs en $LOGS_DIR/n8n.log)"
fi

echo ""
echo "=========================================================="
echo "🎉 ¡Todos los servicios han sido lanzados con éxito!"
echo "=========================================================="
echo "🔹 Open WebUI:      http://localhost:3000"
echo "🔹 n8n Automations: http://localhost:5678"
echo "🔹 Ollama API:       http://localhost:11434"
echo "🔹 Modelo activo:    qwen2.5:7b"
echo "=========================================================="
