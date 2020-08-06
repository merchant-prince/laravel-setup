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
        return Path(f'{Path.cwd()}/{name}').is_dir()


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
                The empty dictionaries represent directories to be created.

                e.g.: { 'one': {
                            'eleven': {},
                            'twelve': {
                                'inner-directory': {}
                            }
                        }
                    }
        """

        Skeleton._validate(structure)
        Skeleton._create(structure)

    @staticmethod
    def _create(structure: Mapping) -> None:
        """
        Create directories according to the structure provided.

        Args:
            structure (Mapping): The directory structure to create in the current directory.
        """

        for name, inner_structure in structure.items():
            os.mkdir(name)

            with cd(name):
                Skeleton._create(inner_structure)

    @staticmethod
    def _validate(structure: Mapping) -> None:
        """
        Validate the directory structure provided.

        Args:
            structure (Mapping): The directory structure to validate.

        Raises:
            ValueError: If the given structure is invalid.
        """

        for name, inner_structure in structure.items():
            if isinstance(inner_structure, Mapping):
                Skeleton._validate(inner_structure)
            else:
                raise ValueError('The directory structure provided is ill-formed.')


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
    """Get a template's absolute path from the relative path specified."""

    return Path(f'{Path(__file__).parent}/templates/{path}')


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
        choices=('authentication', 'dusk', 'horizon', 'telescope'),
        help='Additional modules to be installed.'
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
                        },
                        'supervisor': {
                            'conf.d': {
                                # supervisord.conf
                            }
                        }
                    }
                },
                'docker-compose': {
                    'services': {
                        'php': {
                            # Dockerfile
                            # entrypoint.sh*
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

        with cd(configuration['project']['name']):
            with cd('configuration'):
                with cd('nginx'):
                    with cd('ssl'):
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

            with cd('configuration'):
                # nginx
                with cd('nginx'):
                    with cd('conf.d'):
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

                with cd('supervisor'):
                    with cd('conf.d'):
                        with open('supervisord.conf', 'w') as file, \
                                open(
                                    f"{template_path('configuration/supervisor/conf.d/supervisord.conf')}") as template:
                            file.write(
                                Template(template.read()).substitute(
                                    # intentionally left blank
                                )
                            )

            with cd('docker-compose'):
                with cd('services'):
                    with cd('php'):
                        # Dockerfile (php)
                        with open('Dockerfile', 'w') as file, \
                                open(f"{template_path('docker-compose/services/php/Dockerfile')}") as template:
                            file.write(
                                Template(template.read()).substitute(
                                    # intentionally left blank
                                )
                            )

                        # entrypoint.sh (php)
                        with open('entrypoint.sh', 'w') as file, \
                                open(f"{template_path('docker-compose/services/php/entrypoint.sh')}") as template:
                            file.write(
                                Template(template.read()).substitute(
                                    # intentionally left blank
                                )
                            )

                        Path('entrypoint.sh').chmod(0o755)

        # Pull Laravel project
        logging.info('Pulling a fresh Laravel project...')

        with cd(configuration['project']['name']):
            with cd('application'):
                run(
                    ('docker', 'run',
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
                     'laravel/laravel', configuration['project']['name']),
                    check=True
                )

        # Initialize git
        logging.info('Initializing a git repository for the project...')

        with cd(configuration['project']['name']):
            git_commands = (
                ('git', 'init'),
                ('git', 'add', '.'),
                ('git', 'commit', '-m', 'initial commit'),
                ('git', 'checkout', '-b', 'development')
            )

            for git_command in git_commands:
                run(git_command, check=True)

        # Set environment variables for the Laravel project
        logging.info('Setting the environment variables for the Laravel project...')

        with cd(configuration['project']['name']):
            with cd('application'):
                with cd(configuration['project']['name']):
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
                        env_regex = re.compile(r'^(?P<key>\w+)=(?P<value>[\S]+)?\s*(?P<remaining>#.*)?$')

                        for line in file:
                            line = line.strip()
                            matches = env_regex.match(line)

                            if matches is not None:
                                matches = matches.groupdict()
                                line = (f"{matches['key']}="
                                        f"{env[matches['key']] if matches['key'] in env else matches['value']}"
                                        f"{' ' * 4}{matches['remaining'] or ''}").strip()

                            print(line)

            logging.info('Migrating the database...')
            run(('docker-compose', 'up', '-d'))
            run(('./run', 'artisan', 'migrate:fresh'))
            run(('docker-compose', 'down'))

            logging.info('The base project has been successfully set-up.')

            # post-installation tasks
            additional_modules = arguments.__getattribute__('with') or []

            # authentication
            if 'authentication' in additional_modules:
                run(('docker-compose', 'up', '-d'))

                logging.info('Pulling the authentication module...')
                run(('./run', 'composer', 'require', 'laravel/ui'))

                logging.info('Setting up authentication with Vue...')
                run(('./run', 'artisan', 'ui', 'vue', '--auth'))

                run(('./run', 'artisan', 'migrate:fresh'))

                run(('docker-compose', 'down'))

                git_commands = (
                    ('git', 'add', '.'),
                    ('git', 'commit', '-m', 'scaffold authentication')
                )

                for git_command in git_commands:
                    run(git_command, check=True)

            # dusk
            if 'dusk' in additional_modules:
                run(('docker-compose', 'up', '-d'))

                logging.info('Pulling the dusk module...')
                run(('./run', 'composer', 'require', 'laravel/dusk', '--dev'))

                logging.info('Setting up dusk...')
                run(('./run', 'artisan', 'dusk:install'))

                run(('docker-compose', 'down'))

                # edit docker-compose.yml
                with fileinput.FileInput('docker-compose.yml', inplace=True) as file:
                    for line in file:
                        if line.strip() == '# [selenium-nginx-network-alias]':
                            line = f'''\
      selenium:
        aliases:
          - {configuration['project']['domain']}
'''

                        #TODO: REFACTOR TO KEY: VALUE
                        if line.strip() == '# [selenium-php-network]':
                            line = f'''\
      - selenium
'''

                        if line.strip() == '# [selenium-service]':
                            line = '''\
  selenium:
    image: selenium/hub:latest
    depends_on:
      - php
    ports:
      - "4444:4444"
    networks:
      - selenium

  firefox:
    image: selenium/node-firefox:latest
    depends_on:
      - selenium
    volumes:
      - /dev/shm:/dev/shm
    environment:
      HUB_HOST: selenium
    networks:
      - selenium
'''

                        if line.strip() == '# [selenium-network]':
                            line = '''\
  selenium:
'''

                        print(line, end='')

                with cd('application'):
                    with cd(configuration['project']['name']):
                        # edit tests/DuskTestCase.php
                        with cd('tests'):
                            with open('DuskTestCase.php') as file:
                                contents = file.read()

                            # comment chrome-driver start
                            contents = contents.replace(
                                'static::startChromeDriver();',
                                '// static::startChromeDriver();',
                                1
                            )

                            # edit driver method to use selenium's firefox node
                            match = tuple(
                                re.finditer(
                                    r' {4}protected function driver\(\)\n {4}\{\n {8}.*?\n {4}\}',
                                    contents,
                                    re.MULTILINE | re.DOTALL
                                )
                            )[0]

                            replacement = '''\
    protected function driver()
    {
        return RemoteWebDriver::create(
            'http://selenium:4444/wd/hub',
            DesiredCapabilities::firefox()
                ->setCapability("acceptInsecureCerts", true)
        );
    }
'''

                            contents = ''.join((contents[:match.start()], replacement, contents[match.end():]))

                            with open('DuskTestCase.php', 'w') as file:
                                file.write(contents)

                git_commands = (
                    ('git', 'add', '.'),
                    ('git', 'commit', '-m', 'scaffold dusk')
                )

                for git_command in git_commands:
                    run(git_command, check=True)

            else:
                # remove selenium comments from docker-compose.yml
                with fileinput.FileInput('docker-compose.yml', inplace=True) as file:
                    selenium_comments = (
                        '# [selenium-nginx-network-alias]',
                        '# [selenium-php-network]',
                        '# [selenium-service]',
                        '# [selenium-network]'
                    )

                    for line in file:
                        if line.strip() not in selenium_comments:
                            print(line, end='')

                git_commands = (
                    ('git', 'add', '.'),
                    ('git', 'commit', '-m', 'remove selenium comments')
                )

                for git_command in git_commands:
                    run(git_command, check=True)

            # horizon
            if 'horizon' in additional_modules:
                run(('docker-compose', 'up', '-d'))

                logging.info('Pulling laravel/horizon package...')
                run(('./run', 'composer', 'require', 'laravel/horizon'))

                logging.info('Setting up horizon in the project...')
                run(('./run', 'artisan', 'horizon:install'))

                run(('./run', 'artisan', 'migrate:fresh'))

                run(('docker-compose', 'down'))

                # edit supervisord.conf
                with cd('configuration'):
                    with cd('supervisor'):
                        with cd('conf.d'):
                            with fileinput.FileInput('supervisord.conf', inplace=True) as file:
                                for line in file:
                                    if line.strip() == '# [horizon]':
                                        line = '''\
[program:horizon]
command=php /var/www/html/artisan horizon
user=www-data
stopwaitsecs=3600
autorestart=true
redirect_stderr=true
'''
                                    print(line, end='')

                git_commands = (
                    ('git', 'add', '.'),
                    ('git', 'commit', '-m', 'scaffold horizon')
                )

                for git_command in git_commands:
                    run(git_command, check=True)

            else:
                # remove horizon comment from supervisord.conf
                with cd('configuration'):
                    with cd('supervisor'):
                        with cd('conf.d'):
                            with fileinput.FileInput('supervisord.conf', inplace=True) as file:
                                for line in file:
                                    if line.strip() != '# [horizon]':
                                        print(line, end='')

                git_commands = (
                    ('git', 'add', '.'),
                    ('git', 'commit', '-m', 'remove horizon comment')
                )

                for git_command in git_commands:
                    run(git_command, check=True)

            # telescope
            if 'telescope' in additional_modules:
                run(('docker-compose', 'up', '-d'))

                logging.info('Pulling laravel/telescope package...')
                run(('./run', 'composer', 'require', 'laravel/telescope', '--dev'))

                logging.info('Setting up telescope in the project...')
                run(('./run', 'artisan', 'telescope:install'))

                run(('./run', 'artisan', 'migrate:fresh'))

                run(('docker-compose', 'down'))

                # change the telescope service provider to allow telescope to run in development environment only
                with cd('application'):
                    with cd(configuration['project']['name']):
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

                git_commands = (
                    ('git', 'add', '.'),
                    ('git', 'commit', '-m', 'scaffold telescope')
                )

                for git_command in git_commands:
                    run(git_command, check=True)

        # Project successfully set-up
        logging.info('Set-up complete. Build something awesome!')
