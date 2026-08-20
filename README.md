# 🚀 Proyecto de IA Local: Qwen 2.5 7B + Open WebUI + n8n + Hermes Agent (Nous Research)

Este proyecto contiene una suite completa de Inteligencia Artificial local optimizada para tu equipo (Intel i9, 64 GB RAM, NVIDIA Quadro T1000 con soporte CUDA).

---

## 📌 Servicios y Componentes Instalados

| Servicio | Tipo | URL / Acceso | Descripción |
| :--- | :--- | :--- | :--- |
| **Open WebUI** | Web UI | [http://localhost:3000](http://localhost:3000) | Interfaz de chat moderna, RAG, subida de documentos e historial. |
| **n8n** | Web UI | [http://localhost:5678](http://localhost:5678) | Automatizaciones y orquestación con nodos de IA y Function Calling. |
| **Ollama API** | Servidor | [http://localhost:11434](http://localhost:11434) | Motor de inferencia local compatible con API OpenAI (`/v1`). |
| **Hermes Agent** | CLI Agéntico | `./scripts/hermes.sh` | Agente autónomo oficial de **Nous Research** con auto-mejora y herramientas. |

---

## 🤖 Uso de Hermes Agent (Nous Research Oficial)

El agente oficial de Nous Research está instalado en `hermes_agent_official/` y preconfigurado con el modelo local `qwen2.5:7b-64k` y ventana de contexto de 64,000 tokens.

### 1. Modo Interactivo en Terminal (Chat Continuo)
```bash
/home/ubuntuia/IAlocal/scripts/hermes.sh
```

### 2. Modo Consulta Rápida (One-Shot)
```bash
/home/ubuntuia/IAlocal/scripts/hermes.sh "Revisa los archivos de este directorio y haz un resumen"
```

---

## 🛠️ Scripts de Gestión Centralizados

En el directorio `scripts/` dispones de herramientas para controlar la plataforma:

```bash
# Iniciar todos los servicios en segundo plano (Ollama, WebUI, n8n)
./scripts/start_all.sh

# Comprobar el estado de los servicios, modelos, RAM y GPU VRAM
./scripts/status.sh

# Detener todos los servicios de forma limpia
./scripts/stop_all.sh

# Lanzar Hermes Agent
./scripts/hermes.sh
```

---

## ⚡ Configuración de n8n con el Modelo Local

1. Abre **n8n** en tu navegador: [http://localhost:5678](http://localhost:5678).
2. Crea tu cuenta de usuario local inicial.
3. Importa la plantilla lista para usar ubicada en `n8n_template_workflow.json` (*Settings -> Import Workflow*).
4. En el nodo **OpenAI Chat Model**, configura:
   * **API Key:** `ollama`
   * **Base URL:** `http://127.0.0.1:11434/v1`
   * **Model Name:** `qwen2.5:7b` (o `qwen2.5:7b-64k`).
5. ¡Listo! Puedes interactuar con el agente en tiempo real con memoria y herramientas.
