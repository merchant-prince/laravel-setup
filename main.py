#!/usr/bin/env python3

# TODO: main should delegate to other modules. its only purpose is to be a clear entrypoint

from typing import Mapping

from modules.extracts import parser, preliminary_checks
from modules.scaffolding import directory_structure_is_valid, create_directory_structure
from modules.verification import (
    directory_exists, domain_is_valid, is_pascal_case,
)

if __name__ == '__main__':
    preliminary_checks(requirements={
        'docker.version': '20.10.5',
        'docker-compose.version': '1.28.0',
        'openssl.version': '1.1.1',
        'git.version': '2.31.0',
    })

    arguments = parser().parse_args()

    if not is_pascal_case(arguments.project_name):
        raise RuntimeError(f"The project name: '{arguments.project_name}' is not pascal-cased.")

    if directory_exists(arguments.project_name):
        raise RuntimeError(
            f"The directory: '{arguments.project_name}' already exists in the current working directory.")

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

    project_directory_structure = {
        configuration['project.name']: {
            # docker-compose.yml
            # .gitignore
            # README.md

            'configuration': {
                'nginx': {
                    'conf.d': {
                        # default.conf
                        # utils.conf
                    },
                    'ssl': {
                        # key.pem
                        # certificate.pem
                    }
                },
                'supervisor': {
                    'conf.d': {
                        # supervisord.conf
                    }
                }
            },
            'docker-compose': {
                'services': {
                    'php': {
                        # Dockerfile
                    }
                }
            },
            'application': {
                # Laravel application
            }
        }
    }

    if not directory_structure_is_valid(project_directory_structure):
        raise RuntimeError("The project's provided directory structure is invalid.")

    create_directory_structure(project_directory_structure)
