#!/usr/bin/env bash
# ==============================================================================
# Script para Detener los Servicios - Stack Local de IA
# ==============================================================================

echo "=========================================================="
echo "🛑 Deteniendo servicios del Stack Local de IA..."
echo "=========================================================="

# 1. Detener n8n
if pgrep -f "n8n start" > /dev/null; then
    echo "Parando n8n..."
    pkill -f "n8n start" || true
    echo "✅ n8n detenido."
else
    echo "ℹ️ n8n no estaba corriendo."
fi

# 2. Detener Open WebUI
if pgrep -f "open-webui serve" > /dev/null; then
    echo "Parando Open WebUI..."
    pkill -f "open-webui serve" || true
    echo "✅ Open WebUI detenido."
else
    echo "ℹ️ Open WebUI no estaba corriendo."
fi

# 3. Detener Ollama
if pgrep -f "ollama serve" > /dev/null; then
    echo "Parando Ollama..."
    pkill -f "ollama serve" || true
    echo "✅ Ollama detenido."
else
    echo "ℹ️ Ollama no estaba corriendo."
fi

echo "=========================================================="
echo "✨ Todos los procesos han sido detenidos."
echo "=========================================================="
