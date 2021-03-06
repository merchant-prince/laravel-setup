from fileinput import input
from os import getuid, getgid, getcwd
from pathlib import Path
from re import compile, Match, Pattern
from shutil import copyfile
from string import Template
from subprocess import run
from typing import Mapping, Union

from modules.configuration import ConfigurationAccessorType
from modules.configuration import create_argument_parser, validated_script_arguments, create_configuration_accessor
from modules.packages import setup_breeze, setup_horizon, setup_telescope
from modules.ssl import Generator as SslGenerator
from modules.utilities import cd, migrate_database, start_stack, template_path
from modules.verification import correct_version_is_installed


def preflight_checks() -> None:
    """
    Checks whether the correct version of the dependencies are installed.
    """
    requirements: Mapping[str, str] = {
        'docker.version': '20.10.5',
        'docker-compose.version': '1.28.0',
        'git.version': '2.31.0',
    }

    if not correct_version_is_installed(
            ('docker', 'version', '--format', '{{.Server.Version}}'), requirements['docker.version']):
        raise RuntimeError(
            'The correct docker version is not installed. '
            f"Docker >= v{requirements['docker.version']} is needed."
        )

    if not correct_version_is_installed(
            ('docker-compose', 'version', '--short'), requirements['docker-compose.version']):
        raise RuntimeError(
            'The correct docker-compose version is not installed. '
            f"Docker-Compose >= v{requirements['docker-compose.version']} is needed."
        )

    if not correct_version_is_installed(
            ('git', 'version'), requirements['git.version']):
        raise RuntimeError(
            f"The correct git version is not installed. Git >= v{requirements['git.version']} is needed."
        )


def configure() -> ConfigurationAccessorType:
    """
    Instantiates a configuration accessor for the project.
    """
    return create_configuration_accessor(
        **validated_script_arguments(
            create_argument_parser().parse_args()
        )
    )


def generate_configuration_files(configuration: ConfigurationAccessorType) -> None:
    with cd(configuration('project.name')):
        with cd('configuration/nginx/ssl'):
            ssl_generator: SslGenerator = SslGenerator(
                domain=configuration('project.domain'),
                certificate_name=configuration('services.nginx.ssl.certificate.name'),
                key_name=configuration('services.nginx.ssl.key.name')
            )

            if not ssl_generator.binary_is_present():
                ssl_generator.build_binary()

            ssl_generator.generate()

        with open('docker-compose.yml', 'w') as file, open(f"{template_path('docker-compose.yml')}") as template:
            file.write(
                Template(template.read()).substitute({
                    'PROJECT_NAME': configuration('project.name'),
                    'USER_ID': getuid(),
                    'GROUP_ID': getgid(),
                    'POSTGRES_DB': configuration('services.postgres.database'),
                    'POSTGRES_USER': configuration('services.postgres.username'),
                    'POSTGRES_PASSWORD': configuration('services.postgres.password'),
                    'ADMINER_PORT': configuration('services.adminer.port'),
                    'MAILHOG_PORT': configuration('services.mailhog.port'),
                })
            )

        with open('run', 'w') as file, open(f"{template_path('run')}") as template:
            file.write(
                Template(template.read()).substitute({
                    'PROJECT_NAME': configuration('project.name'),
                    'NODE_IMAGE_TAG': configuration('miscellaneous.node.image.tag'),
                })
            )

        Path('run').chmod(0o755)

        copyfile(template_path('.gitignore'), f'{Path.cwd()}/.gitignore')

        with open('README.md', 'w') as file, open(f"{template_path('README.md')}") as template:
            file.write(
                Template(template.read()).substitute({
                    'PROJECT_NAME': configuration('project.name'),
                    'PROJECT_DOMAIN': configuration('project.domain'),
                    'SSL_KEY_NAME': configuration('services.nginx.ssl.key.name'),
                    'SSL_CERTIFICATE_NAME': configuration('services.nginx.ssl.certificate.name'),
                    'ADMINER_PORT': configuration('services.adminer.port'),
                    'MAILHOG_PORT': configuration('services.mailhog.port'),
                })
            )

        with cd('configuration'):
            with cd('nginx/conf.d'):
                with open('default.conf', 'w') as file, \
                        open(f"{template_path('configuration/nginx/conf.d/default.conf')}") as template:
                    file.write(
                        Template(template.read()).substitute({
                            'PROJECT_DOMAIN': configuration('project.domain'),
                            'SSL_KEY_NAME': configuration('services.nginx.ssl.key.name'),
                            'SSL_CERTIFICATE_NAME': configuration('services.nginx.ssl.certificate.name'),
                        })
                    )

                with open('utils.conf', 'w') as file, \
                        open(f"{template_path('configuration/nginx/conf.d/utils.conf')}") as template:
                    file.write(
                        Template(template.read()).substitute({
                            'PROJECT_DOMAIN': configuration('project.domain'),
                            'ADMINER_PORT': configuration('services.adminer.port'),
                            'MAILHOG_PORT': configuration('services.mailhog.port'),
                        })
                    )

            with cd('supervisor/conf.d'):
                copyfile(
                    template_path('configuration/supervisor/conf.d/supervisord.conf'),
                    f'{Path.cwd()}/supervisord.conf'
                )

        with cd('docker-compose/services/php'):
            copyfile(template_path('docker-compose/services/php/Dockerfile'), f'{Path.cwd()}/Dockerfile')


def pull_fresh_laravel_project(configuration: ConfigurationAccessorType) -> None:
    with cd(f"{configuration('project.name')}/application/core"):
        run(
            (
                'docker', 'run',
                '--rm',
                '--interactive',
                '--tty',
                '--user', f'{getuid()}:{getgid()}',
                '--mount', f'type=bind,source={getcwd()},target=/application',
                '--workdir', '/application',
                'composer', 'create-project',
                '--prefer-dist',
                '--ignore-platform-reqs',
                'laravel/laravel', configuration('project.name'),
            ),
            check=True
        )


def initialize_git_repository(configuration: ConfigurationAccessorType) -> None:
    with cd(f"{configuration('project.name')}/application/core/{configuration('project.name')}"):
        run(('git', 'init'), check=True)
        run(('git', 'add', '*'), check=True)
        run(('git', 'commit', '--message', 'initial commit'), check=True)
        run(('git', 'checkout', '-b', 'development'), check=True)


def configure_environment_variables(configuration: ConfigurationAccessorType) -> None:
    environment: Mapping[str, Union[str, int]] = {
        'APP_NAME': configuration('project.name'),
        'APP_URL': f"https://{configuration('project.domain')}",

        'DB_CONNECTION': 'pgsql',
        'DB_HOST': 'postgresql',
        'DB_PORT': 5432,
        'DB_DATABASE': configuration('services.postgres.database'),
        'DB_USERNAME': configuration('services.postgres.username'),
        'DB_PASSWORD': configuration('services.postgres.password'),

        'CACHE_DRIVER': 'redis',
        'SESSION_DRIVER': 'redis',
        'QUEUE_CONNECTION': 'redis',

        'REDIS_HOST': 'redis',
        'REDIS_PORT': 6379,

        'MAIL_HOST': 'mailhog',
        'MAIL_PORT': 1025,
        'MAIL_FROM_NAME': configuration('project.name').lower(),
        'MAIL_FROM_ADDRESS': f"{configuration('project.name').lower()}@{configuration('project.domain')}"
    }

    with cd(f"{configuration('project.name')}/application/core/{configuration('project.name')}"):
        for environment_file in ['.env', '.env.example']:
            with input(environment_file, inplace=True) as file:
                environment_regex: Pattern = compile(r'^(?P<key>\w+)=(?P<value>.*?)?\s*$')

                for line in file:
                    line: str = line.strip()
                    matches: Match = environment_regex.match(line)

                    if matches is not None:
                        matches: Mapping[str, str] = matches.groupdict()
                        line = (f"{matches['key']}="
                                f"{environment[matches['key']] if matches['key'] in environment else matches['value']}")

                    print(line)

        run(('git', 'add', '*'), check=True)
        run(('git', 'commit', '--message', 'set environment variables for the project.'), check=True)

    with cd(configuration('project.name')):
        with start_stack():
            migrate_database()


def setup_laravel_packages(configuration: ConfigurationAccessorType) -> None:
    if 'breeze.inertia' in configuration('project.packages'):
        setup_breeze(configuration, inertia=True)
    elif 'breeze' in configuration('project.packages'):
        setup_breeze(configuration)

    if 'horizon' in configuration('project.packages'):
        setup_horizon(configuration)

    if 'telescope' in configuration('project.packages'):
        setup_telescope(configuration)
