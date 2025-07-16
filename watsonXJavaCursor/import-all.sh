#!/usr/bin/env bash
set -x

orchestrate env activate local
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

# Import all individual Python tools
for python_tool in read_file.py write_file.py list_dir.py codebase_search.py run_terminal_cmd.py grep_search.py file_search.py delete_file.py web_search.py diff_history.py edit_file.py; do
  orchestrate tools import -k python -f "${SCRIPT_DIR}/tools/${python_tool}" -r "${SCRIPT_DIR}/tools/requirements.txt"
done

# Import the main agent
orchestrate agents import -f "${SCRIPT_DIR}/agente/agent.yml"
