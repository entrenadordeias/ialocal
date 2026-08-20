#!/usr/bin/env bash
# ==============================================================================
# Lanzador Oficial de Hermes Agent (Nous Research)
# ==============================================================================

set -e

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Verificar que Ollama esté corriendo
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "⏳ Ollama no está activo. Iniciando Ollama primero..."
    export HOME="$PROJECT_DIR/home"
    export OLLAMA_HOST="0.0.0.0:11434"
    export OLLAMA_ORIGINS="*"
    export OLLAMA_MODELS="$PROJECT_DIR/models"
    export PATH="$PROJECT_DIR/bin:$PATH"
    nohup "$PROJECT_DIR/bin/ollama" serve > "$PROJECT_DIR/logs/ollama.log" 2>&1 &
    sleep 3
fi

export HERMES_HOME="$PROJECT_DIR/hermes_home"
export HOME="$PROJECT_DIR/home"
export PATH="$PROJECT_DIR/bin:$PATH"

cd "$PROJECT_DIR/hermes_agent_official"

if [ $# -gt 0 ]; then
    exec .venv/bin/python cli.py -q "$*"
else
    exec .venv/bin/python cli.py
fi
