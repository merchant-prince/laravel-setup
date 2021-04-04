from pathlib import Path
from subprocess import run
from typing import List


def setup_directory_structure(project_name: str) -> None:
    directories: List[str] = [
        f'{project_name}/configuration/nginx/conf.d',
        f'{project_name}/configuration/nginx/ssl',
        f'{project_name}/configuration/supervisor/conf.d',
        f'{project_name}/docker-compose/services/php',
        f'{project_name}/application/core',
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def generate_self_signed_tls_certificate(domain: str, certificate_name: str, key_name: str) -> None:
    """
    Generate an SSL certificate with its associated key in the current working directory.

    Args:
        domain: The domain for which the SSL certificate is being created.
        certificate_name: Name of the certificate file.
        key_name: Name of the key file.
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
