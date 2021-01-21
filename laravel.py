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


#############
# FUNCTIONS #
#############

def template_path(path: str) -> Path:
    """ Get a template's absolute path from a path relative to the 'templates' directory. """

    return Path(f'{Path(__file__).parent}/templates/{path}')


def migrate_database() -> None:
    """ Migrate the application's database. """

    run(('./run', 'artisan', 'migrate:fresh'), check=True)


####################
# CONTEXT MANAGERS #
####################

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
    A context manager to start and stop the application's stack using docker-compose.
    """

    try:
        run(('docker-compose', 'up', '-d'), check=True)
        yield
    finally:
        run(('docker-compose', 'down'), check=True)


###########
# CLASSES #
###########

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

                e.g.:
                {
                    'one': {
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


class Block:
    """
    This class is responsible for adding or removing tags' contents from files.
    The tags are in the form `<tag>...</tag>`

    Args:
        filename (str): The name of the file to manipulate
        tag (str): The name of the tag to manipulate
    """

    def __init__(self, filename: str, tag: str):
        with open(filename) as file:
            self.contents = file.read()

        self.tag = tag
        self.regex = re.compile(
            r' *'
            f'<{tag}>'
            r'\n(?P<block>.*?)'
            r' *'
            f'</{tag}>'
            r'\n',
            re.DOTALL
        )

    def add(self):
        """ Replace a `<tag>` with its contents """
        self.contents = self.regex.sub(r'\g<block>', self.contents)
        return self

    def remove(self):
        """ Remove a `<tag>` and its contents """
        self.contents = self.regex.sub('', self.contents)
        return self

    def __str__(self) -> str:
        """ Get the block's contents when casting to string """
        return self.contents


class Git:
    @staticmethod
    def init() -> None:
        run(('git', 'init'), check=True)

    @staticmethod
    def add(files: str) -> None:
        run(('git', 'add', files), check=True)

    @staticmethod
    def commit(message: str) -> None:
        run(('git', 'commit', '-m', message), check=True)

    @staticmethod
    def new_branch(branch_name: str) -> None:
        run(('git', 'checkout', '-b', branch_name), check=True)


#########
# START #
#########

if __name__ == '__main__':

    logging.basicConfig(
        format='[%(levelname)s] [%(asctime)s]: %(msg)s',
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
        choices=('authentication', 'dusk', 'horizon', 'telescope'),
        help='Additional modules to install.'
    )
    parser.subparsers.setup.add_argument(
        '--development',
        action='store_true',
        help='Install the development version of laravel.'
    )

    arguments = parser.main.parse_args()
    additional_modules = arguments.__getattribute__('with') or []

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
        logging.info('Initializing configuration values...')

        configuration = {
            'project': {
                'name': arguments.project_name,
                'domain': arguments.domain
            },
            'services': {
                'nginx': {
                    'ssl': {
                        'certificate': 'cert.pem',
                        'key': 'key.pem'
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
                # intentionally left blank
            ).write(
                key_name=configuration['services']['nginx']['ssl']['key'],
                certificate_name=configuration['services']['nginx']['ssl']['certificate']
            )

        # Create configuration files
        with cd(configuration['project']['name']):

            # Generate
            logging.info("Generating the project's configuration files...")

            # docker-compose.yml
            with open('docker-compose.yml', 'w') as file, \
                    open(f"{template_path('docker-compose.yml')}") as template:
                file.write(
                    Template(template.read()).substitute(
                        project_name=configuration['project']['name'],
                        project_domain=configuration['project']['domain'],
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
                    # supervisord.conf
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

            # add or remove blocks to configuration files
            logging.info('Adding & removing blocks to configuration files...')

            # dusk
            contents = str(
                Block('docker-compose.yml', 'dusk').add()
                if 'dusk' in additional_modules
                else Block('docker-compose.yml', 'dusk').remove()
            )

            with open('docker-compose.yml', 'w') as file:
                file.write(contents)

            # horizon
            with cd('configuration/supervisor/conf.d'):
                contents = str(
                    Block('supervisord.conf', 'horizon').add()
                    if 'horizon' in additional_modules
                    else Block('supervisord.conf', 'horizon').remove()
                )

                with open('supervisord.conf', 'w') as file:
                    file.write(contents)

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

        with cd(f"{configuration['project']['name']}/application/{configuration['project']['name']}"):
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
                    env_regex = re.compile(r'^(?P<key>\w+)=(?P<value>.*?)?\s*$')

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
                migrate_database()

            logging.info('The base project has been successfully set-up.')

            ########################
            # MODULES INSTALLATION #
            ########################

            # authentication
            if 'authentication' in additional_modules:
                with start_stack():
                    logging.info('Pulling the authentication module...')
                    run(('./run', 'composer', 'require', 'laravel/ui'), check=True)

                    logging.info('Setting up authentication with Vue...')
                    run(('./run', 'artisan', 'ui', 'vue', '--auth'), check=True)

                    migrate_database()

                with cd(f"application/{configuration['project']['name']}"):
                    Git.add('.')
                    Git.commit('scaffold authentication')

            # dusk
            if 'dusk' in additional_modules:
                with start_stack():
                    logging.info('Pulling laravel/dusk package...')
                    run(('./run', 'composer', 'require', 'laravel/dusk', '--dev'), check=True)

                    logging.info('Setting up dusk in the project...')
                    run(('./run', 'artisan', 'dusk:install'), check=True)

                    migrate_database()

                    with cd(f"application/{configuration['project']['name']}/tests"):
                        with open('DuskTestCase.php', 'r+') as file:
                            regex = re.compile(
                                r'(?P<block> *return RemoteWebDriver::create\(.*\);\n)',
                                re.DOTALL
                            )
                            file_contents = file.read()
                            file.seek(0)
                            file_contents = file_contents.replace(
                                'static::startChromeDriver();',
                                '// static::startChromeDriver();',
                                1
                            )
                            file.write(
                                regex.sub('''\
        return RemoteWebDriver::create(
            'http://selenium:4444/wd/hub',
            DesiredCapabilities::chrome()
                ->setCapability(ChromeOptions::CAPABILITY, $options)
                ->setCapability('acceptInsecureCerts', true)
        );
''', file_contents)
                            )
                            file.truncate()

                with cd(f"application/{configuration['project']['name']}"):
                    Git.add('.')
                    Git.commit('scaffold dusk')

            # horizon
            if 'horizon' in additional_modules:
                with start_stack():
                    logging.info('Pulling laravel/horizon package...')
                    run(('./run', 'composer', 'require', 'laravel/horizon'), check=True)

                    logging.info('Setting up horizon in the project...')
                    run(('./run', 'artisan', 'horizon:install'), check=True)

                    migrate_database()

                # Console Kernel
                with cd(f"application/{configuration['project']['name']}/app/Console"):
                    with open('Kernel.php', 'r+') as file:
                        file_contents = file.read()
                        file.seek(0)
                        command_regex = re.compile(
                            r' *' + re.escape("// $schedule->command('inspire')->hourly();")
                        )
                        new_file_contents = command_regex.sub(
                            "        $schedule->command('horizon:snapshot')->everyFiveMinutes();",
                            file_contents
                        )

                        file.write(new_file_contents)
                        file.truncate()

                with cd(f"application/{configuration['project']['name']}"):
                    Git.add('.')
                    Git.commit('scaffold horizon')

            # telescope
            if 'telescope' in additional_modules:
                with start_stack():
                    logging.info('Pulling laravel/telescope package...')
                    run(('./run', 'composer', 'require', 'laravel/telescope', '--dev'), check=True)

                    logging.info('Setting up telescope in the project...')
                    run(('./run', 'artisan', 'telescope:install'), check=True)

                    migrate_database()

                with cd(f"application/{configuration['project']['name']}"):
                    # TelescopeServiceProvider.php
                    with cd('app/Providers'):
                        with open('TelescopeServiceProvider.php', 'r+') as file:
                            file_contents = file.read()
                            file.seek(0)
                            regex = re.compile(r' *' + re.escape('public function register()'))
                            new_file_contents = regex.sub('''\
    public function register()
    {
        if ($this->app->isLocal()) {
            $this->app->register(\\\\Laravel\\\\Telescope\\\\TelescopeServiceProvider::class);
            $this->registerTelescope();
        }
    }

    /**
     * Register telescope services.
     *
     * @return void
     */
    protected function registerTelescope()\
''', file_contents)

                            file.write(new_file_contents)
                            file.truncate()

                    # composer.json
                    with open('composer.json', 'r+') as file:
                        file_contents = file.read()
                        file.seek(0)
                        regex = re.compile(
                            r' *' + re.escape('"dont-discover": []') + r'\n'
                        )
                        new_file_contents = regex.sub('''\
            "dont-discover": [
                "laravel/telescope"
            ]
''', file_contents)

                        file.write(new_file_contents)
                        file.truncate()

                with cd(f"application/{configuration['project']['name']}"):
                    Git.add('.')
                    Git.commit('scaffold telescope')

            # Project successfully set-up
            logging.info('Set-up complete. Build something awesome!')
