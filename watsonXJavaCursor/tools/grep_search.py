import re
import glob
import os
import fnmatch

# Importa el decorador de herramientas desde el ADK de watsonx Orchestrate
from ibm_watsonx_orchestrate.agent_builder.tools import tool

@tool
def grep_search(query, case_sensitive=True, include_pattern=None, exclude_pattern=None, explanation=None):
    """
    Busca un patrón regex en archivos usando filtros de inclusión y exclusión.
    
    Args:
        query (str): El patrón regex a buscar
        case_sensitive (bool): Si la búsqueda debe ser sensible a mayúsculas/minúsculas
        include_pattern (str): Patrón glob para archivos a incluir (ej: '*.py')
        exclude_pattern (str): Patrón glob para archivos a excluir
        explanation (str): Explicación de una oración del propósito de la búsqueda
    
    Returns:
        list: Lista de diccionarios con los resultados encontrados
    """
    results = []
    
    # Configurar flags para regex
    flags = 0 if case_sensitive else re.IGNORECASE
    
    try:
        # Compilar el patrón regex
        pattern = re.compile(query, flags)
    except re.error as e:
        return [{"error": f"Patrón regex inválido: {e}"}]
    
    # Obtener lista de archivos a procesar
    files_to_search = []
    
    if include_pattern:
        # Usar el patrón de inclusión
        files_to_search = glob.glob(include_pattern, recursive=True)
    else:
        # Buscar todos los archivos en el directorio actual
        files_to_search = glob.glob("**/*", recursive=True)
    
    # Filtrar solo archivos (no directorios)
    files_to_search = [f for f in files_to_search if os.path.isfile(f)]
    
    # Aplicar patrón de exclusión si existe
    if exclude_pattern:
        files_to_search = [f for f in files_to_search 
                          if not fnmatch.fnmatch(f, exclude_pattern)]
    
    # Buscar en cada archivo
    for file_path in files_to_search:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                for line_num, line in enumerate(file, 1):
                    matches = pattern.finditer(line)
                    for match in matches:
                        results.append({
                            "file": file_path,
                            "line_number": line_num,
                            "line_content": line.rstrip('\n'),
                            "match": match.group(),
                            "start_pos": match.start(),
                            "end_pos": match.end()
                        })
        except (IOError, UnicodeDecodeError) as e:
            results.append({
                "file": file_path,
                "error": f"Error al leer archivo: {e}"
            })
    
    return results
