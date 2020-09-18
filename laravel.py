"""
A script to automate the installation of Laravel projects on Docker.
"""

import fileinput
import logging
import os
import re
from argparse import ArgumentParser
from collections import namedtuple
from collections.abc import Mapping
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from string import Template
from subprocess import run
from types import SimpleNamespace
from typing import Optional

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


@contextmanager
def cd(destination: str) -> None:
    """
    A context manager to change directory. Mimics unix's cd.

    Args:
        destination (str): The directory to cd into.
    """

    cwd = os.getcwd()

    try:
        os.chdir(destination)
        yield
    finally:
        os.chdir(cwd)


@contextmanager
def start_stack() -> None:
    """
    A context manager to start and stop the project stack using docker-compose.
    """

    try:
        run(('docker-compose', 'up', '-d'))
        yield
    finally:
        run(('docker-compose', 'down'))


class Validation:
    """
    This class takes care of the validation needs of the application.

    Every validation rule is defined as a static method.
    """

    @staticmethod
    def is_pascal_case(string: str) -> bool:
        pascal_case_regex = re.compile(r'^[A-Z][a-z]+(?:[A-Z][a-z]+)*$')

        return pascal_case_regex.match(string) is not None

    @staticmethod
    def domain_is_valid(domain: str) -> bool:
        domain_regex = re.compile(
            r'^'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?))'  # domain
            r'(?:/?|[/?]\S+)'  # path
            r'$',
            re.IGNORECASE
        )

        return domain_regex.match(domain) is not None

    @staticmethod
    def directory_exists(name: str) -> bool:
        return Path(name).is_dir()


class Skeleton:
    """
    A class to create a directory structure in the current directory.
    """

    @staticmethod
    def create(structure: Mapping) -> None:
        """
        Validate and create directories based on the provided structure.

        Args:
            structure (dict):
                The directory structure to create in the current directory.
                This is a dictionary of dictionaries (of dictionaries of dictionaries ...).
                The empty dictionaries represent the directories to be created.

                e.g.: { 'one': {
                            'eleven': {},
                            'twelve': {
                                'inner-directory': {
                                    ...
                                }
                            }
                        }
                    }
        """

        for name, inner_structure in structure.items():
            if isinstance(inner_structure, Mapping):
                os.mkdir(name)
            else:
                raise ValueError('The directory structure provided is ill-formed.')

            with cd(name):
                Skeleton.create(inner_structure)


class Ssl:
    """
    This class is responsible for creating a x509 TLS/SSL certificate, and its associated key.

    Attributes:
        _hostname (str):
            The hostname/domain of the machine on which the application will be hosted.

        _key_size (int):
            The size of the SSL key.

        _validity (int):
            The number number of days for which the certificate will remain valid.

        _key (bytes):
            The TLS key content.

        _certificate (bytes):
            The TLS certificate content.
    """

    def __init__(self, hostname: str, key_size: int = 4096, validity: int = 365):
        self._hostname: str = hostname
        self._key_size: int = key_size
        self._validity: int = validity
        self._key: Optional[bytes] = None
        self._certificate: Optional[bytes] = None

    def generate(self):
        """
        Generate the TLS/SSL key and certificate.

        Return:
            self
        """

        key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self._key_size,
            backend=default_backend(),
        )

        name = x509.Name([
            x509.NameAttribute(x509.NameOID.COMMON_NAME, self._hostname)
        ])

        san = x509.SubjectAlternativeName([
            x509.DNSName(self._hostname)
        ])

        basic_constraints = x509.BasicConstraints(ca=True, path_length=0)
        now = datetime.utcnow()

        cert = (
            x509.CertificateBuilder()
                .subject_name(name)
                .issuer_name(name)
                .public_key(key.public_key())
                .serial_number(1000)
                .not_valid_before(now)
                .not_valid_after(now + timedelta(days=self._validity))
                .add_extension(basic_constraints, False)
                .add_extension(san, False)
                .sign(key, hashes.SHA256(), default_backend())
        )

        self._certificate = cert.public_bytes(encoding=serialization.Encoding.PEM)
        self._key = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        )

        return self

    def write(self, key_name: str, certificate_name: str) -> None:
        """
        Write the generated certificates to a binary file.

        Args:
            key_name (str): The filename of the key.
            certificate_name (str): The filename of the certificate.
        """

        with open(key_name, 'wb') as key:
            key.write(self._key)

        with open(certificate_name, 'wb') as certificate:
            certificate.write(self._certificate)


def template_path(path: str = '') -> Path:
    """Get a template's absolute path from a path relative to the 'templates' directory."""

    return Path(f'{Path(__file__).parent}/templates/{path}')


class Git:
    @staticmethod
    def init() -> None:
        run(('git', 'init'))

    @staticmethod
    def add(files: str) -> None:
        run(('git', 'add', files))

    @staticmethod
    def commit(message: str) -> None:
        run(('git', 'commit', '-m', message))

    @staticmethod
    def new_branch(branch_name: str) -> None:
        run(('git', 'checkout', '-b', branch_name))


# START #
if __name__ == '__main__':

    logging.basicConfig(
        format='[%(levelname)s]: %(msg)s',
        level=logging.INFO
    )

    parser = namedtuple('Parser', ('main', 'subparser', 'subparsers'))(
        main := ArgumentParser(
            prog='laravel',
            description='A script to scaffold Laravel projects.',
            epilog='Build something awesome!',
            allow_abbrev=False
        ),
        main.add_subparsers(
            title='Action',
            description='The action to take.',
            dest='action',
            required=True
        ),
        SimpleNamespace()
    )

    # setup
    parser.subparsers.setup = parser.subparser.add_parser(
        'setup',
        description='Setup a new Laravel project.',
        epilog='Do it!',
        add_help=True,
        allow_abbrev=False
    )
    parser.subparsers.setup.add_argument(
        'project_name',
        help='The name of the project to scaffold.'
    )
    parser.subparsers.setup.add_argument(
        '--domain',
        default='application.local',
        help='The domain name where the project will be hosted.'
    )
    parser.subparsers.setup.add_argument(
        '--with',
        nargs='*',
        choices=('authentication', 'horizon', 'telescope'),
        help='Additional modules to be installed.'
    )
    parser.subparsers.setup.add_argument(
        '--jetstream',
        choices=tuple(
            f"{stack}{('.' + teams_support) if teams_support else ''}"
            for stack in ('inertia', 'livewire')
            for teams_support in ('', 'teams')
        ),
        help='Install the laravel/jetstream package with the appropriate stack, and activate team-support if needed.'
    )
    parser.subparsers.setup.add_argument(
        '--development',
        action='store_true',
        help='Install the development version of laravel.'
    )

    # parse arguments
    arguments = parser.main.parse_args()

    if arguments.action == 'setup':

        # validation
        logging.info('Validating provided values...')

        if not Validation.is_pascal_case(arguments.project_name):
            raise RuntimeError(f"The project name: '{arguments.project_name}' is not pascal-cased.")

        if Validation.directory_exists(arguments.project_name):
            raise RuntimeError(f"The directory: '{arguments.project_name}' already exists at `{Path.cwd()}`.")

        if not Validation.domain_is_valid(arguments.domain):
            raise RuntimeError(f"The domain: '{arguments.domain}' is invalid.")

        # configuration
        logging.info('Creating configuration values...')

        configuration = {
            # project-level configuration values.
            'project': {
                'name': arguments.project_name,
                'domain': arguments.domain
            },
            'services': {
                'nginx': {
                    'ssl': {
                        'key': 'key.pem',
                        'certificate': 'certificate.pem'
                    }
                },
                'postgres': {
                    'environment': {
                        'db': arguments.project_name.lower(),
                        'user': 'username',
                        'password': 'password'
                    }
                }
            }
        }

        # directory structure
        logging.info('Creating directory structure...')

        Skeleton.create({
            configuration['project']['name']: {
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
        })

        # Generate ssl certificates
        logging.info('Generating SSL certificates...')

        with cd(f"{configuration['project']['name']}/configuration/nginx/ssl"):
            Ssl(
                hostname=configuration['project']['domain']
            ).generate(
                # generate the ssl certificates...
            ).write(
                key_name=configuration['services']['nginx']['ssl']['key'],
                certificate_name=configuration['services']['nginx']['ssl']['certificate']
            )

        # Create configuration files
        logging.info("Generating the project's configuration files...")

        with cd(configuration['project']['name']):

            # docker-compose.yml
            with open('docker-compose.yml', 'w') as file, \
                    open(f"{template_path('docker-compose.yml')}") as template:
                file.write(
                    Template(template.read()).substitute(
                        project_name=configuration['project']['name'],
                        user_id=os.geteuid(),
                        group_id=os.getegid(),
                        postgres_db=configuration['services']['postgres']['environment']['db'],
                        postgres_user=configuration['services']['postgres']['environment']['user'],
                        postgres_password=configuration['services']['postgres']['environment']['password']
                    )
                )

            # run
            with open('run', 'w') as file, \
                    open(f"{template_path('run')}") as template:
                file.write(
                    Template(template.read()).substitute(
                        project_name=configuration['project']['name']
                    )
                )

            Path('run').chmod(0o755)

            # .gitignore
            with open('.gitignore', 'w') as file, \
                    open(f"{template_path('.gitignore')}") as template:
                file.write(
                    Template(template.read()).substitute(
                        # intentionally left blank
                    )
                )

            # README.md
            with open('README.md', 'w') as file, \
                    open(f"{template_path('README.md')}") as template:
                file.write(
                    Template(template.read()).substitute(
                        project_name=configuration['project']['name'],
                        project_domain=configuration['project']['domain']
                    )
                )

            with cd('configuration'):
                # nginx
                with cd('nginx/conf.d'):
                    # default.conf
                    with open('default.conf', 'w') as file, \
                            open(f"{template_path('configuration/nginx/conf.d/default.conf')}") as template:
                        file.write(
                            Template(template.read()).substitute(
                                project_domain=configuration['project']['domain'],
                                ssl_key=configuration['services']['nginx']['ssl']['key'],
                                ssl_certificate=configuration['services']['nginx']['ssl']['certificate']
                            )
                        )

                    # utils.conf
                    with open('utils.conf', 'w') as file, \
                            open(f"{template_path('configuration/nginx/conf.d/utils.conf')}") as template:
                        file.write(
                            Template(template.read()).substitute(
                                project_domain=configuration['project']['domain']
                            )
                        )

                # supervisor
                with cd('supervisor/conf.d'):
                    with open('supervisord.conf', 'w') as file, \
                            open(
                                f"{template_path('configuration/supervisor/conf.d/supervisord.conf')}"
                            ) as template:
                        file.write(
                            Template(template.read()).substitute(
                                # intentionally left blank
                            )
                        )

            with cd('docker-compose/services/php'):
                # Dockerfile (php)
                with open('Dockerfile', 'w') as file, \
                        open(f"{template_path('docker-compose/services/php/Dockerfile')}") as template:
                    file.write(
                        Template(template.read()).substitute(
                            # intentionally left blank
                        )
                    )

        # Pull Laravel project
        logging.info('Pulling a fresh Laravel project...')

        with cd(f"{configuration['project']['name']}/application"):
            installation_command = (
                'docker', 'run',
                '--rm',
                '--interactive',
                '--tty',
                '--user',
                f'{os.geteuid()}:{os.getegid()}',
                '--mount', f'type=bind,source={os.getcwd()},target=/application',
                '--workdir', '/application',
                'composer', 'create-project',
                '--prefer-dist',
                '--ignore-platform-reqs',
                'laravel/laravel', configuration['project']['name']
            )

            if arguments.development:
                installation_command += ('dev-develop',)

            run(installation_command, check=True)

        # Initialize git
        logging.info('Initializing a git repository for the project...')

        with cd(configuration['project']['name']):
            Git.init()
            Git.add('.')
            Git.commit('initial commit')
            Git.new_branch('development')

        # Set environment variables for the Laravel project
        logging.info('Setting the environment variables for the Laravel project...')

        with cd(configuration['project']['name']):

            with cd(f"application/{configuration['project']['name']}"):
                env = {
                    'APP_NAME': configuration['project']['name'],
                    'APP_URL': f"https://{configuration['project']['domain']}",

                    'DB_CONNECTION': 'pgsql',
                    'DB_HOST': 'postgresql',
                    'DB_PORT': 5432,
                    'DB_DATABASE': configuration['services']['postgres']['environment']['db'],
                    'DB_USERNAME': configuration['services']['postgres']['environment']['user'],
                    'DB_PASSWORD': configuration['services']['postgres']['environment']['password'],

                    'CACHE_DRIVER': 'redis',
                    'SESSION_DRIVER': 'redis',
                    'QUEUE_CONNECTION': 'redis',

                    'REDIS_HOST': 'redis',
                    'REDIS_PORT': 6379,

                    'MAIL_HOST': 'mailhog',
                    'MAIL_PORT': 1025,
                    'MAIL_FROM_NAME': (configuration['project']['name']).lower(),
                    'MAIL_FROM_ADDRESS': f"{(configuration['project']['name']).lower()}@{configuration['project']['domain']}"
                }

                # .env
                with fileinput.input('.env', inplace=True) as file:
                    env_regex = re.compile(r'^(?P<key>\w+)=(?P<value>[\S]+)?\s*$')

                    for line in file:
                        line = line.strip()
                        matches = env_regex.match(line)

                        if matches is not None:
                            matches = matches.groupdict()
                            line = (f"{matches['key']}="
                                    f"{env[matches['key']] if matches['key'] in env else matches['value']}")

                        print(line)

            logging.info('Migrating the database...')

            with start_stack():
                run(('./run', 'artisan', 'migrate:fresh'))

            logging.info('The base project has been successfully set-up.')

            # post-installation tasks
            additional_modules = arguments.__getattribute__('with') or []

            # authentication
            if 'authentication' in additional_modules:
                with start_stack():
                    logging.info('Pulling the authentication module...')
                    run(('./run', 'composer', 'require', 'laravel/ui'))

                    logging.info('Setting up authentication with Vue...')
                    run(('./run', 'artisan', 'ui', 'vue', '--auth'))

                    run(('./run', 'artisan', 'migrate:fresh'))

                Git.add('.')
                Git.commit('scaffold authentication')

            # horizon
            horizon_block_regex = re.compile(r'<horizon>\n(?P<block>.*)\n</horizon>', re.DOTALL)

            if 'horizon' in additional_modules:
                with start_stack():
                    logging.info('Pulling laravel/horizon package...')
                    run(('./run', 'composer', 'require', 'laravel/horizon'))

                    logging.info('Setting up horizon in the project...')
                    run(('./run', 'artisan', 'horizon:install'))

                    run(('./run', 'artisan', 'migrate:fresh'))

                # uncomment horizon block in supervisord.conf
                with cd('configuration/supervisor/conf.d'):
                    with open('supervisord.conf') as file:
                        file_contents = file.read()

                    with open('supervisord.conf', 'w') as file:
                        file.write(
                            horizon_block_regex.sub(
                                '\n'.join([
                                    line.strip()
                                    for line in horizon_block_regex.search(file_contents).group('block').split('\n')
                                ]),
                                file_contents
                            )
                        )

                Git.add('.')
                Git.commit('scaffold horizon')

            else:
                # remove horizon commented block from supervisord.conf
                with cd('configuration/supervisor/conf.d'):
                    with open('supervisord.conf') as file:
                        file_contents = file.read()

                    with open('supervisord.conf', 'w') as file:
                        file.write(horizon_block_regex.sub('', file_contents))

                Git.add('.')
                Git.commit('remove horizon comments in configuration files')

            # telescope
            if 'telescope' in additional_modules:
                with start_stack():
                    logging.info('Pulling laravel/telescope package...')
                    run(('./run', 'composer', 'require', 'laravel/telescope', '--dev'))

                    logging.info('Setting up telescope in the project...')
                    run(('./run', 'artisan', 'telescope:install'))

                    run(('./run', 'artisan', 'migrate:fresh'))

                # change the telescope service provider to allow telescope to run in development environment only
                with cd(f"application/{configuration['project']['name']}"):
                    with fileinput.FileInput('app/Providers/TelescopeServiceProvider.php', inplace=True) as file:
                        for line in file:
                            if line.strip() == 'public function register()':
                                line = '''\
    public function register()
    {
        if ($this->app->isLocal()) {
            $this->app->register(\\Laravel\\Telescope\\TelescopeServiceProvider::class);
            $this->registerTelescope();
        }
    }

    /**
     * Register telescope services.
     *
     * @return void
     */
    protected function registerTelescope()
'''

                            print(line, end='')

                    with fileinput.FileInput('app/Console/Kernel.php', inplace=True) as file:
                        for line in file:
                            if line.strip() == "// $schedule->command('inspire')->hourly();":
                                line = '''\
        $schedule->command('horizon:snapshot')->everyFiveMinutes();
'''

                            print(line, end='')

                    with fileinput.FileInput('composer.json', inplace=True) as file:
                        for line in file:
                            if line.strip() == '"dont-discover": []':
                                line = '''\
            "dont-discover": [
                "laravel/telescope"
            ]
'''

                            print(line, end='')

                Git.add('.')
                Git.commit('scaffold telescope')

            # jetstream
            if arguments.jetstream:
                with start_stack():
                    logging.info('Pulling laravel/jetstream package...')
                    run(('./run', 'composer', 'require', 'laravel/jetstream'))

                    jetstream_options = arguments.jetstream.split('.')

                    if len(jetstream_options) == 1:
                        jetstream_options.append(None)

                    [stack, teams_support] = jetstream_options
                    logging.info(f"Setting up jetstream with {stack}{' and teams support' if teams_support else ''}...")
                    installation_command = ('./run', 'artisan', 'jetstream:install', stack)

                    if teams_support:
                        installation_command += ('--teams',)

                    run(installation_command)

                    logging.info('Pulling yarn assets...')
                    run(('./run', 'yarn', 'install'))

                    logging.info('Compiling yarn assets...')
                    run(('./run', 'yarn', 'run', 'dev'))

                    run(('./run', 'artisan', 'migrate:fresh'))

                Git.add('.')
                Git.commit('scaffold jetstream')

            # Project successfully set-up
            logging.info('Set-up complete. Build something awesome!')
