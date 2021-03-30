#!/usr/bin/env python3

from typing import Mapping

from modules.extracts import parser, preliminary_checks, validate_script_arguments
from modules.scaffolding import directory_structure_is_valid, create_directory_structure

if __name__ == '__main__':
    preliminary_checks(requirements={
        'docker.version': '20.10.5',
        'docker-compose.version': '1.28.0',
        'openssl.version': '1.1.1',
        'git.version': '2.31.0',
    })

    validate_script_arguments(arguments := parser().parse_args())

    configuration: Mapping[str, str] = {
        'project.name': arguments.project_name,
        'project.domain': arguments.domain,

        'services.nginx.ssl.certificate': 'certificate.pem',
        'services.nginx.ssl.key': 'key.pem',

        'services.postgres.database': arguments.project_name.lower(),
        'services.postgres.username': 'username',
        'services.postgres.password': 'password',
    }

    project_directory_structure: Mapping[str, ...] = {
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
                'core': {
                    # Laravel application
                }
            }
        }
    }

    if not directory_structure_is_valid(project_directory_structure):
        raise RuntimeError("The project's provided directory structure is invalid.")

    create_directory_structure(project_directory_structure)
