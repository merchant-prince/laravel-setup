#!/usr/bin/env python3

from typing import Mapping

from modules.extracts import parser, preliminary_checks, scaffold_project_directory_structure, validate_script_arguments
from modules.scaffolding import generate_self_signed_tls_certificate
from modules.utilities import cd

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

    scaffold_project_directory_structure(
        project_directory_structure := {
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
    )

    with cd(configuration['project.name']):
        with cd('configuration/nginx/ssl'):
            generate_self_signed_tls_certificate(
                certificate_name=configuration['services.nginx.ssl.certificate'],
                key_name=configuration['services.nginx.ssl.key'],
                domain=configuration['project.domain']
            )
