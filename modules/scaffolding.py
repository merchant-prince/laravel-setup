from os import mkdir
from subprocess import run
from typing import Mapping

from modules.utilities import cd


def directory_structure_is_valid(directory_structure: Mapping) -> bool:
    """
    A function to check if the directory structure provided is valid

    Args:
        directory_structure (Mapping):
            The directory structure. This is a mapping of mappings (of mappings of mappings ...).
            e.g.:
            {
                'one': {
                    'eleven': {},   # creates an empty directory
                    'twelve': {     # creates a directory named 'twelve' with 'inner-directory' inside it
                        'inner-directory': {
                            ...
                        }
                    }
                }
            }
    """
    for directory_name, inner_structure in directory_structure.items():
        if not isinstance(inner_structure, Mapping):
            return False

    return True


def create_directory_structure(directory_structure: Mapping) -> None:
    """
    A function to create a directory structure in the current directory.

    Args:
        directory_structure (Mapping):
            The directory structure to create in the current directory.
            This is a mapping of mappings (of mappings of mappings ...).
            The empty dictionaries represent the directories to be created.
            e.g.:
            {
                'one': {
                    'eleven': {},   # creates an empty directory
                    'twelve': {     # creates a directory named 'twelve' with 'inner-directory' inside it
                        'inner-directory': {
                            ...
                        }
                    }
                }
            }
    """
    for directory_name, inner_structure in directory_structure.items():
        mkdir(directory_name)

        with cd(directory_name):
            create_directory_structure(inner_structure)


def generate_self_signed_tls_certificate(*, certificate_name: str, key_name: str, domain: str) -> None:
    """
    Generate an SSL certificate with its associated key in the current working directory.

    Args:
        certificate_name: Name of the certificate file.
        key_name: Name of the key file.
        domain: The domain for which the SSL certificate is being created.
    """
    run(
        (
            'openssl', 'req',
            '-x509',
            '-newkey', 'rsa:4096',
            '-sha256',
            '-days', '730',
            '-nodes',
            '-keyout', key_name,
            '-out', certificate_name,
            '-subj', f'/CN={domain}',
            '-addext', f'subjectAltName=DNS:{domain}',
        ),
        capture_output=True,
        check=True
    )
