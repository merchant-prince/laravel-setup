from pathlib import Path
from typing import List


def setup_directory_structure(project_name: str) -> None:
    directories: List[str] = [
        f'{project_name}/configuration/nginx/conf.d',
        f'{project_name}/configuration/nginx/ssl',
        f'{project_name}/configuration/supervisor/conf.d',
        f'{project_name}/docker-compose/services/php',
        f'{project_name}/application/core',
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
