from subprocess import run
from typing import Tuple


def init() -> None:
    run(('git', 'init'), check=True)


def add(files: Tuple[str]) -> None:
    run(('git', 'add', *files), check=True)


def commit(message: str) -> None:
    run(('git', 'commit', '--message', message), check=True)


def checkout_to_new_branch(branch_name: str) -> None:
    run(('git', 'checkout', '-b', branch_name), check=True)
