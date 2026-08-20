#!/usr/bin/env python3
"""
Hermes Agent - Agente Autónomo Local con Qwen 2.5 7B y Tool Calling
====================================================================
Este módulo implementa un agente autónomo multi-paso capaz de invocar
herramientas locales (Function Calling) usando el endpoint compatible
con OpenAI de Ollama en localhost:11434/v1.
"""

import os
import sys
import json
import psutil
import subprocess
from typing import List, Dict, Any, Callable
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

console = Console()

# Definición de herramientas del agente
def get_system_metrics(**kwargs) -> Dict[str, Any]:
    """Obtiene métricas en tiempo real del sistema (CPU, RAM y GPU si está disponible)."""
    ram = psutil.virtual_memory()
    metrics = {
        "cpu_percent": psutil.cpu_percent(interval=0.5),
        "ram_total_gb": round(ram.total / (1024**3), 2),
        "ram_used_gb": round(ram.used / (1024**3), 2),
        "ram_percent": ram.percent,
    }
    try:
        gpu_out = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=name,memory.used,memory.total,temperature.gpu", "--format=csv,noheader"],
            text=True
        ).strip()
        metrics["gpu_info"] = gpu_out
    except Exception:
        metrics["gpu_info"] = "GPU NVIDIA no accesible"
    return metrics

def calculate(expression: str) -> str:
    """Evalúa de forma segura expresiones matemáticas."""
    try:
        # Permitir solo operaciones matemáticas seguras
        allowed_names = {"abs": abs, "round": round, "min": min, "max": max, "pow": pow}
        result = eval(expression, {"__builtins__": None}, allowed_names)
        return f"Resultado: {result}"
    except Exception as e:
        return f"Error calculando '{expression}': {str(e)}"

def run_bash_command(command: str) -> str:
    """Ejecuta un comando bash seguro dentro del espacio de trabajo y devuelve la salida."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd="/home/ubuntuia/IAlocal"
        )
        out = result.stdout.strip()
        err = result.stderr.strip()
        if err:
            return f"STDOUT:\n{out}\nSTDERR:\n{err}"
        return out if out else "(Comando ejecutado sin salida)"
    except Exception as e:
        return f"Error ejecutando comando: {str(e)}"

def read_workspace_file(filepath: str) -> str:
    """Lee el contenido de un archivo dentro del directorio de trabajo."""
    full_path = os.path.join("/home/ubuntuia/IAlocal", filepath.lstrip("/"))
    try:
        if not os.path.exists(full_path):
            return f"Error: El archivo '{filepath}' no existe."
        with open(full_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Error leyendo archivo: {str(e)}"

# Registro de esquemas de herramientas para el modelo (Formato OpenAI Tools)
TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "get_system_metrics",
            "description": "Obtiene las métricas de rendimiento en tiempo real del servidor (CPU, RAM, GPU VRAM).",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Calcula una expresión matemática compleja o evalúa números de forma precisa.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "La expresión matemática a evaluar, e.g. '(1024 * 64) / 8'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_bash_command",
            "description": "Ejecuta comandos de shell en Linux para listar archivos, comprobar estado o tareas del sistema.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "Comando bash a ejecutar."
                    }
                },
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_workspace_file",
            "description": "Lee el contenido de un archivo del proyecto.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {
                        "type": "string",
                        "description": "Ruta relativa del archivo a leer."
                    }
                },
                "required": ["filepath"]
            }
        }
    }
]

# Mapa de funciones ejecutables
TOOL_FUNCTIONS: Dict[str, Callable] = {
    "get_system_metrics": get_system_metrics,
    "calculate": calculate,
    "run_bash_command": run_bash_command,
    "read_workspace_file": read_workspace_file,
}

class HermesAgent:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:11434/v1",
        api_key: str = "ollama",
        model: str = "qwen2.5:7b"
    ):
        self.client = OpenAI(base_url=base_url, api_key=api_key)
        self.model = model
        self.system_prompt = (
            "Eres un Agente Inteligente y Autónomo de alto nivel impulsado por Qwen 2.5 7B. "
            "Tienes a tu disposición un conjunto de herramientas para consultar el sistema, realizar cálculos, "
            "leer archivos y ejecutar comandos. Piensa paso a paso y usa las herramientas cuando sea necesario "
            "para dar respuestas exactas y comprobadas."
        )

    def run(self, user_query: str, max_turns: int = 6) -> str:
        """Ejecuta el ciclo agéntico multi-paso hasta completar la tarea."""
        console.print(Panel(f"[bold cyan]Query:[/bold cyan] {user_query}", title="🤖 Hermes Agent"))

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": user_query}
        ]

        for turn in range(max_turns):
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS_SCHEMA,
                tool_choice="auto",
                temperature=0.2
            )

            message = response.choices[0].message
            messages.append(message)

            # Si el modelo no solicita más herramientas, terminamos
            if not message.tool_calls:
                console.print(Panel(Markdown(message.content or ""), title="🎯 Respuesta Final", style="green"))
                return message.content or ""

            # Procesar las herramientas solicitadas
            for tool_call in message.tool_calls:
                func_name = tool_call.function.name
                arguments_raw = tool_call.function.arguments
                try:
                    arguments = json.loads(arguments_raw)
                except Exception:
                    arguments = {}

                console.print(f"🔧 [bold yellow]Llamando herramienta:[/bold yellow] `{func_name}` con args: `{arguments}`")

                if func_name in TOOL_FUNCTIONS:
                    try:
                        tool_output = TOOL_FUNCTIONS[func_name](**arguments)
                    except Exception as e:
                        tool_output = f"Error ejecutando {func_name}: {str(e)}"
                else:
                    tool_output = f"Herramienta '{func_name}' no encontrada."

                console.print(f"📄 [dim]Resultado:[/dim] {str(tool_output)[:200]}...")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(tool_output) if not isinstance(tool_output, str) else tool_output
                })

        return "Se alcanzó el límite máximo de turnos agénticos."

    def interactive_chat(self):
        """Inicia una sesión de chat interactiva continua en terminal."""
        console.print(Panel(
            "[bold green]Bienvenido a Hermes Agent (Qwen 2.5 7B)[/bold green]\n"
            "• Escribe tu consulta o tarea para que el agente la resuelva usando herramientas locales.\n"
            "• Comandos especiales: [yellow]/tools[/yellow] (ver herramientas), [yellow]/clear[/yellow] (limpiar historial), [yellow]/exit[/yellow] o [yellow]/quit[/yellow] (salir).",
            title="🤖 Hermes Agent Interactive CLI",
            style="bold cyan"
        ))

        history = [{"role": "system", "content": self.system_prompt}]

        while True:
            try:
                user_input = console.input("\n[bold cyan]Hermes ❯ [/bold cyan]").strip()
                if not user_input:
                    continue

                if user_input.lower() in ["/exit", "/quit", "exit", "quit"]:
                    console.print("[yellow]¡Hasta pronto![/yellow]")
                    break

                if user_input.lower() == "/clear":
                    history = [{"role": "system", "content": self.system_prompt}]
                    console.print("[green]Historial de conversación reiniciado.[/green]")
                    continue

                if user_input.lower() == "/tools":
                    console.print(Panel(
                        "\n".join([f"• [bold yellow]{t['function']['name']}[/bold yellow]: {t['function']['description']}" for t in TOOLS_SCHEMA]),
                        title="🔧 Herramientas Disponibles"
                    ))
                    continue

                # Agregar mensaje del usuario al historial
                history.append({"role": "user", "content": user_input})

                # Ejecutar ciclo agéntico
                max_turns = 6
                for turn in range(max_turns):
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=history,
                        tools=TOOLS_SCHEMA,
                        tool_choice="auto",
                        temperature=0.2
                    )

                    message = response.choices[0].message
                    history.append(message)

                    if not message.tool_calls:
                        console.print(Panel(Markdown(message.content or ""), title="🎯 Hermes", style="green"))
                        break

                    for tool_call in message.tool_calls:
                        func_name = tool_call.function.name
                        arguments_raw = tool_call.function.arguments
                        try:
                            arguments = json.loads(arguments_raw)
                        except Exception:
                            arguments = {}

                        console.print(f"🔧 [bold yellow]Ejecutando herramienta:[/bold yellow] `{func_name}` con {arguments}")

                        if func_name in TOOL_FUNCTIONS:
                            try:
                                tool_output = TOOL_FUNCTIONS[func_name](**arguments)
                            except Exception as e:
                                tool_output = f"Error ejecutando {func_name}: {str(e)}"
                        else:
                            tool_output = f"Herramienta '{func_name}' no encontrada."

                        console.print(f"📄 [dim]Resultado:[/dim] {str(tool_output)[:200]}...")

                        history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_output) if not isinstance(tool_output, str) else tool_output
                        })

            except (KeyboardInterrupt, EOFError):
                console.print("\n[yellow]Sesión finalizada.[/yellow]")
                break
            except Exception as e:
                console.print(f"[bold red]Error durante la ejecución:[/bold red] {e}")

if __name__ == "__main__":
    agent = HermesAgent()
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        agent.run(query)
    else:
        agent.interactive_chat()

