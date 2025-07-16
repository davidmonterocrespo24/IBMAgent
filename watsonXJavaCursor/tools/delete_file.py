import os

# Importa el decorador de herramientas desde el ADK de watsonx Orchestrate
from ibm_watsonx_orchestrate.agent_builder.tools import tool

@tool
def delete_file(target_file: str, explanation: str = "") -> str:
    """
    Delete a file at the specified path.
    """
    try:
        if os.path.exists(target_file):
            os.remove(target_file)
            return f"Successfully deleted file: {target_file}"
        else:
            return f"File not found: {target_file}"
    except Exception as e:
        return f"Error deleting file: {str(e)}"