"""
A script to automate the installation of Laravel projects on Docker.
"""

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
from types import SimpleNamespace

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
                This is generally a dictionary of dictionaries.
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

        for name, structure in structure.items():
            os.mkdir(name)

            with cd(name):
                Skeleton._create(structure)

    @staticmethod
    def _validate(structure: Mapping) -> None:
        """
        Validate the directory structure provided.

        Args:
            structure (Mapping): The directory structure to validate.

        Raises:
            ValueError: If the given structure is invalid.
        """

        for name, structure in structure.items():
            if isinstance(structure, Mapping):
                Skeleton._validate(structure)
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
        self._key: bytes = None
        self._certificate: bytes = None

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

    # parse arguments
    arguments = parser.main.parse_args()

    if arguments.action == 'setup':

        # validation
        logging.info('Validating provided values...')

        if not Validation.is_pascal_case(arguments.project_name):
            raise RuntimeError(f'The project name: {arguments.project_name} is not pascal-cased.')

        if Validation.directory_exists(arguments.project_name):
            raise RuntimeError(f'The directory {arguments.project_name} already exists in {Path.cwd()}.')

        if not Validation.domain_is_valid(arguments.domain):
            raise RuntimeError(f'The domain: {arguments.domain} is invalid.')

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
                'adminer': {
                    'port': 8080  # for the administration panel (ui)
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
                'configuration': {
                    'nginx': {
                        'conf.d': {},
                        'ssl': {}
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
                'application': {}
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
                        postgres_password=configuration['services']['postgres']['environment']['password'],
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

            # README.md     @todo: fill the README.md file
            with open('README.md', 'w') as file, \
                    open(f"{template_path('README.md')}") as template:
                file.write(
                    Template(template.read()).substitute(
                        # intentionally left blank
                    )
                )

            with cd('configuration'):
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
                                    project_domain=configuration['project']['domain'],
                                    adminer_port=configuration['services']['adminer']['port']
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
