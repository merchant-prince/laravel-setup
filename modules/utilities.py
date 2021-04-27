from contextlib import contextmanager
from os import chdir, getcwd
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
from typing import Union


@contextmanager
def cd(destination: Union[str, Path]) -> None:
    """
    A context manager to change directory. Mimics unix's cd.

    Args:
        destination (str|Path): The directory to cd into.
    """
    current_working_directory: str = getcwd()

    try:
        chdir(str(destination))
        yield
    finally:
        chdir(current_working_directory)


@contextmanager
def tmpdir() -> None:
    """
    A context manager to create a temporary directory and cd into it.
    """
    current_working_directory: str = getcwd()

    with TemporaryDirectory() as temporary_directory:
        try:
            chdir(temporary_directory)
            yield
        finally:
            chdir(current_working_directory)


@contextmanager
def start_stack() -> None:
    """
    A context manager to start and stop the application's stack using docker-compose.
    """
    try:
        run(('docker-compose', 'up', '-d'), check=True)
        yield
    finally:
        run(('docker-compose', 'down'), check=True)


def migrate_database() -> None:
    """
    Migrate the application's database.
    """
    run(('./run', 'artisan', 'migrate:fresh'), check=True)


def project_path(path: str = '') -> Path:
    """
    Get a file's absolute path from a path relative to the root project directory.

    Args:
        path: File's path relative to the root project directory.

    Returns:
        A Path object pointing to the file.
    """
    return Path(f'{Path(__file__).parent.parent}/{path}')


def template_path(path: str) -> Path:
    """
    Get a template's absolute path from a path relative to the 'templates' directory.

    Args:
        path: Template's path relative to the 'templates' directory.

    Returns:
        A Path object pointing to the template.
    """
    return project_path(f'templates/{path}')
