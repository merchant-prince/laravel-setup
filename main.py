#!/usr/bin/env python3

from os import getuid, getgid, getcwd
from subprocess import run
from typing import Mapping, Union

import modules.git as git
from modules.extracts import generate_configuration_files, parser, preliminary_checks, scaffold_directory_structure, \
    validate_script_arguments
from modules.utilities import cd

if __name__ == '__main__':
    preliminary_checks(requirements={
        'docker.version': '20.10.5',
        'docker-compose.version': '1.28.0',
        'openssl.version': '1.1.1',
        'git.version': '2.31.0',
    })

    validate_script_arguments(arguments := parser().parse_args())

    configuration: Mapping[str, Union[str, int]] = {
        'project.name': arguments.project_name,
        'project.domain': arguments.domain,

        'services.nginx.ssl.certificate.name': 'certificate.pem',
        'services.nginx.ssl.key.name': 'key.pem',

        'services.postgres.database': arguments.project_name.lower(),
        'services.postgres.username': 'username',
        'services.postgres.password': 'password',

        'services.adminer.port': 8080,
        'services.mailhog.port': 8025,

        'miscellaneous.node.image.tag': 'stretch',
    }

    scaffold_directory_structure({
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
                        # [ssl key]
                        # [ssl certificate]
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
                    # [laravel application]
                }
            }
        }
    })

    with cd(configuration['project.name']):
        generate_configuration_files(configuration)

        with cd('application/core'):
            run(
                (
                    'docker', 'run',
                    '--rm',
                    '--interactive',
                    '--tty',
                    '--user',
                    f'{getuid()}:{getgid()}',
                    '--mount', f'type=bind,source={getcwd()},target=/application',
                    '--workdir', '/application',
                    'composer', 'create-project',
                    '--prefer-dist',
                    '--ignore-platform-reqs',
                    'laravel/laravel', configuration['project.name']
                ),
                check=True
            )

            with cd(configuration['project.name']):
                git.init()
                git.add(('.',))
                git.commit('initial commit')
                git.checkout_to_new_branch('development')
