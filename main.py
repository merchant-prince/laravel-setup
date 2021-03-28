#!/usr/bin/env python3

from typing import Mapping

from modules.extracts import parser
from modules.validation import directory_exists, domain_is_valid, is_pascal_case


if __name__ == '__main__':
    arguments = parser().parse_args()

    if not is_pascal_case(arguments.project_name):
        raise RuntimeError(f"The project name: '{arguments.project_name}' is not pascal-cased.")

    if directory_exists(arguments.project_name):
        raise RuntimeError(f"The directory: '{arguments.project_name}' already exists in the current directory.")

    if not domain_is_valid(arguments.domain):
        raise RuntimeError(f"The domain: '{arguments.domain}' is invalid.")

    configuration: Mapping[str, str] = {
        'project.name': arguments.project_name,
        'project.domain': arguments.domain,

        'services.nginx.ssl.certificate': 'certificate.pem',
        'services.nginx.ssl.key': 'key.pem',

        'services.postgres.database': arguments.project_name.lower(),
        'services.postgres.username': 'username',
        'services.postgres.password': 'password',
    }
