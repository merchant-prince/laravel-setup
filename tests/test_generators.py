from pathlib import Path
from subprocess import run
from typing import List
from unittest import TestCase

from modules.generators import generate_self_signed_tls_certificate, setup_directory_structure
from tests.utilities import tmpdir


class CreateDirectoryStructureTestCase(TestCase):
    def test_directories_are_properly_created(self) -> None:
        with tmpdir():
            project_name: str = 'OneTwo'

            directories: List[str] = [
                f'{project_name}/configuration/nginx/conf.d',
                f'{project_name}/configuration/nginx/ssl',
                f'{project_name}/configuration/supervisor/conf.d',
                f'{project_name}/docker-compose/services/php',
                f'{project_name}/application/core',
            ]

            setup_directory_structure(project_name)

            for directory in directories:
                self.assertTrue(Path(directory).is_dir())


class GenerateSelfSignedTlsCertificateTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.CERTIFICATE_NAME = 'certificate.pem'
        cls.KEY_NAME = 'key.pem'

    def test_tls_certificate_is_successfully_generated(self) -> None:
        with tmpdir():
            generate_self_signed_tls_certificate(
                certificate_name=self.CERTIFICATE_NAME,
                key_name=self.KEY_NAME,
                domain='example.com'
            )

            self.assertTrue(Path(self.CERTIFICATE_NAME).is_file() and Path(self.KEY_NAME).is_file())

    def test_generated_tls_certificate_is_valid(self) -> None:
        with tmpdir():
            generate_self_signed_tls_certificate(
                certificate_name=self.CERTIFICATE_NAME,
                key_name=self.KEY_NAME,
                domain='example.com'
            )

            self.assertEqual(
                run(('openssl', 'x509', '-noout', '-in', self.CERTIFICATE_NAME), capture_output=True).returncode,
                0
            )
