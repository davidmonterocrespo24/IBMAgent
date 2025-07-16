import subprocess

# Importa el decorador de herramientas desde el ADK de watsonx Orchestrate
from ibm_watsonx_orchestrate.agent_builder.tools import tool

@tool
def diff_history(explanation: str = "") -> str:
    """
    Retrieve the history of recent changes made to files in the workspace.
    """
    try:
        # This would typically integrate with git or file system monitoring
        result = subprocess.run(['git', 'log', '--oneline', '--stat', '-5'], 
                              capture_output=True, text=True, cwd='.')
        
        if result.returncode == 0:
            return f"Recent git history:\n{result.stdout}"
        else:
            return "No git repository found or git not available"
    except Exception as e:
        return f"Error retrieving diff history: {str(e)}"
