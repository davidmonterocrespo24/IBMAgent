import subprocess
from pathlib import Path

# Importa el decorador de herramientas desde el ADK de watsonx Orchestrate
from ibm_watsonx_orchestrate.agent_builder.tools import tool

WORKSPACE = Path(r"/home/testagent/workspace").resolve()

# Validación: la carpeta debe existir
WORKSPACE.mkdir(parents=True, exist_ok=True)

@tool
def run_terminal_cmd(command: str, is_background: bool = False, require_user_approval: bool = True,
                    explanation: str = "") -> str:
    """
    Execute a terminal command in the workspace with optional user approval for safety.
    
    Parameters:
        command (str): The shell command to execute
        is_background (bool): Whether to run the command in background mode
        require_user_approval (bool): Whether user approval is required before execution
        explanation (str): Optional explanation for the command execution
    
    Returns:
        str: Command output and error information, or approval request message if user approval required
    """
    if require_user_approval:
        # In a real implementation, you'd present this to the user for approval
        print(f"Command requires approval: {command}")
        return f"Command '{command}' submitted for user approval. Explanation: {explanation}"
    
    try:
        if is_background:
            process = subprocess.Popen(command, shell=True, cwd=WORKSPACE,stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, text=True)
            return f"Background command started: {command}"
        else:
            result = subprocess.run(command, shell=True, capture_output=True,cwd=WORKSPACE, text=True, timeout=30)
            return f"Command: {command}\nOutput:\n{result.stdout}\nErrors:\n{result.stderr}"
    except subprocess.TimeoutExpired:
        return f"Command timed out: {command}"
    except Exception as e:
        return f"Error executing command: {str(e)}"
    
