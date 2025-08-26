import asyncio
import aiohttp
from bs4 import BeautifulSoup
from duckduckgo_search import DDGS
from googlesearch import search as google_search

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_core.models import ModelInfo
from autogen_ext.models.ollama import OllamaChatCompletionClient
from autogen_agentchat.ui import Console
from autogen_agentchat.conditions import TextMentionTermination

# --- Herramienta: búsqueda web ---
async def web_search(query: str, max_results: int = 5) -> str:
    """Busca información en la web (DuckDuckGo con fallback a Google)."""
    try:
        with DDGS() as ddgs:
            results = ddgs.text(query, max_results=max_results)
            if results:
                return "\n".join([f"- {r['title']}: {r['href']}" for r in results])
    except Exception as e:
        print(f"DuckDuckGo falló: {e}")

    try:
        results = list(google_search(query, num_results=max_results))
        if results:
            return "\n".join([f"- {url}" for url in results])
        else:
            return "No se encontraron resultados en Google."
    except Exception as e:
        print(f"Google falló: {e}")
        return "No se pudieron obtener resultados de búsqueda."
    
#--Herramienta para obtener el contenido en texto de una web segun la url --
async def fetch_web_content(url: str) -> str:
    """Obtiene el contenido en texto de una página web dada su URL."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    return soup.get_text()
                else:
                    return f"Error al acceder a {url}: {response.status}"
    except Exception as e:
        return f"Error al obtener contenido de {url}: {e}"


# --- Definir modelo Ollama ---
model_info = ModelInfo(
    vision=False,
    function_calling=True,
    json_output=True,
    structured_output=True,
    family="qwen3"
)

model_client = OllamaChatCompletionClient(
    model="qwen3:0.6b",
    model_info=model_info
)

# Envolver la herramienta como Function


# --- Crear agentes especializados ---
investigador = AssistantAgent(
    name="investigador",
    model_client=model_client,
    # Pasa la función directamente aquí
    tools=[web_search, fetch_web_content],
    system_message=(
        "Eres un investigador experto. "
        "Tu tarea es buscar información confiable usando la función 'web_search'. "
        "Si es necesario, también puedes usar 'fetch_web_content' para obtener información de páginas web."
        "Devuelve únicamente datos y enlaces relevantes, sin interpretaciones largas."
    ),
    max_tool_iterations=3
)

redactor = AssistantAgent(
    name="redactor",
    model_client=model_client,
    system_message=(
        "Eres un redactor experto. "
        "Recibes la información del investigador y la transformas en un texto claro, sencillo y bien explicado, "
        "como si se lo contaras a alguien sin conocimientos técnicos."
    )
)

verificador = AssistantAgent(
    name="verificador",
    model_client=model_client,
    system_message=(
        "Eres un verificador crítico. "
        "Revisas la respuesta del redactor para detectar posibles errores, incoherencias o falta de claridad. "
        "Tu respuesta debe ser la versión final, corregida y mejorada. "
        "**Cuando la respuesta sea definitiva, finaliza tu mensaje con la palabra TERMINATE.**"
    )
)
# --- Team (RoundRobin = turno por turno) ---
stop_condition = TextMentionTermination(text="TERMINATE")

# Asigna la condición al crear el equipo
team = RoundRobinGroupChat(
    [investigador, redactor, verificador],
    termination_condition=stop_condition
)


# --- Ejecución ---
async def main():
    task = "¿Quién es David Montero Crespo de Uruguay?"
    
    # Usa Console para imprimir la conversación en tiempo real
    await Console(team.run_stream(task=task))

    # Ya no necesitas las líneas de print, Console se encarga de todo.

    await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())