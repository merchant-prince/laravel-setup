from contextlib import contextmanager
from os import chdir, getcwd
from pathlib import Path


@contextmanager
def cd(destination: str) -> None:
    """
    A context manager to change directory. Mimics unix's cd.

    Args:
        destination (str): The directory to cd into.
    """
    current_working_directory = getcwd()

    try:
        chdir(destination)
        yield
    finally:
        chdir(current_working_directory)


def template_path(path: str) -> Path:
    """
    Get a template's absolute path from a path relative to the 'templates' directory.

    Args:
        path: Template's path relative to the 'templates' directory.

    Returns:
        A Path object pointing to the template.
    """
    return Path(f'{Path(__file__).parent.parent}/templates/{path}')
