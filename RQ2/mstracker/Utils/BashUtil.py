import subprocess
from pathlib import Path


def run(command: str, cwd=None) -> str:
    working_dir = cwd
    if cwd is not None:
        p = Path(cwd)
        if p.is_file():
            working_dir = p.parent
    return subprocess.run(command, shell=True, cwd=working_dir, stdout=subprocess.PIPE).stdout.decode('utf-8')
