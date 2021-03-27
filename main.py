#!/usr/bin/env python3

from pathlib import Path

from modules.extracts import parser
from modules.validation import directory_exists, domain_is_valid, is_pascal_case

if __name__ == '__main__':
    arguments = parser().parse_args()

    if not is_pascal_case(arguments.project_name):
        raise RuntimeError(f"The project name: '{arguments.project_name}' is not pascal-cased.")

    if directory_exists(arguments.project_name):
        raise RuntimeError(f"The directory: '{arguments.project_name}' already exists at `{Path.cwd()}`.")

    if not domain_is_valid(arguments.domain):
        raise RuntimeError(f"The domain: '{arguments.domain}' is invalid.")
