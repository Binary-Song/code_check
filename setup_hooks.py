import os
import stat
from pathlib import Path

if os.name == 'nt':
    python_cmd_name = 'python'
else:
    python_cmd_name = 'python3'

repo_path = Path(input("Repo dir: ")).resolve()
check_script_path = Path(__file__) / ".." / "main.py"

precommit_hook_content = f'''#!/bin/sh
{python_cmd_name} "{check_script_path}" "{repo_path}"
'''
postcommit_hook_content = f'''#!/bin/sh
{python_cmd_name} "{check_script_path}" "{repo_path}" --full
'''

def setupHook(filename, content):
    hook_dir = repo_path / '.git' / 'hooks'
    hook_file = hook_dir / filename
    hook_file.write_text(content)
    hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)
    print(f"hook set up: {hook_file}")

setupHook('pre-commit', precommit_hook_content)
#setupHook('post-commit', postcommit_hook_content)
