import os
from typing import Union
from pathlib import Path

# Importa el decorador de herramientas desde el ADK de watsonx Orchestrate
from ibm_watsonx_orchestrate.agent_builder.tools import tool

WORKSPACE = Path(r"/home/testagent/workspace").resolve()

# Validación: la carpeta debe existir
WORKSPACE.mkdir(parents=True, exist_ok=True)

# Cambiar cwd *una sola vez* para todo el proceso
os.chdir(WORKSPACE)
print(f"[Init] Current working dir set to {os.getcwd()}")

def to_workspace_path(path_like: Union[str, Path]) -> Path:
    """
    Devuelve la ruta ABSOLUTA dentro del WORKSPACE.
    • Si el path es relativo → WORKSPACE / path
    • Si es absoluto y ya está dentro del WORKSPACE → se devuelve tal cual
    • Si es absoluto y sale del WORKSPACE → ValueError
    """
    p = Path(path_like)
    if not p.is_absolute():
        p = WORKSPACE / p
    p = p.resolve()

    if WORKSPACE not in p.parents and p != WORKSPACE:
        raise ValueError(f"Ruta fuera del workspace: {p}")
    return p

@tool
def read_file(target_file: str, should_read_entire_file: bool, start_line_one_indexed: int, 
              end_line_one_indexed_inclusive: int, explanation: str = "") -> str:
    """
    Read the contents of a file with line range support.
    
    Parameters:
        target_file (str): Path to the file to be read
        should_read_entire_file (bool): Whether to read the entire file or use line range
        start_line_one_indexed (int): Starting line number (1-based indexing)
        end_line_one_indexed_inclusive (int): Ending line number (1-based, inclusive)
        explanation (str): Optional explanation for the read operation
    
    Returns:
        str: File contents with line range information, or error message if file not found
    """
    target_file = to_workspace_path(target_file) 
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if should_read_entire_file:
            return f"File: {target_file}\n" + "".join(lines)
        
        # Convert to 0-indexed for Python
        start_idx = max(0, start_line_one_indexed - 1)
        end_idx = min(len(lines), end_line_one_indexed_inclusive)
        
        selected_lines = lines[start_idx:end_idx]
        
        result = f"File: {target_file} (lines {start_line_one_indexed}-{end_line_one_indexed_inclusive})\n"
        if start_idx > 0:
            result += f"... {start_idx} lines above not shown ...\n"
        
        result += "".join(selected_lines)
        
        if end_idx < len(lines):
            result += f"... {len(lines) - end_idx} lines below not shown ...\n"
        
        return result
        
    except FileNotFoundError:
        return f"Error: File '{target_file}' not found"
    except Exception as e:
        return f"Error reading file: {str(e)}"
    

