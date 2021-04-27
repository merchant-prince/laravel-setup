from pathlib import Path
from typing import List
from unittest import TestCase

from modules.generators import setup_directory_structure
from modules.utilities import tmpdir


class CreateDirectoryStructureTestCase(TestCase):
    def test_directories_are_properly_created(self) -> None:
        with tmpdir():
            project_name: str = 'OneTwo'

            directories: List[str] = [
                f'{project_name}/configuration/nginx/conf.d',
                f'{project_name}/configuration/nginx/ssl',
                f'{project_name}/configuration/supervisor/conf.d',
                f'{project_name}/docker-compose/services/php',
                f'{project_name}/application/core',
            ]

            setup_directory_structure(project_name)

            for directory in directories:
                self.assertTrue(Path(directory).is_dir())
