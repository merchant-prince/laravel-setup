from os import chdir, getcwd, listdir
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory
from unittest import TestCase

from modules.scaffolding import (
    directory_structure_is_valid, create_directory_structure, generate_self_signed_tls_certificate
)


class DirectoryStructureIsValidTestCase(TestCase):
    def test_correct_directory_structure_returns_true(self) -> None:
        correct_directory_structure = {
            'one': {
                'one_two': {
                    'one_two_three': {}
                }
            },
            'two': {}
        }

        self.assertTrue(directory_structure_is_valid(correct_directory_structure))

    def test_incorrect_directory_structures_return_false(self) -> None:
        incorrect_directory_structures = [
            {
                'one': {
                    'one_two': {
                        'one_two_three': {}
                    }
                },
                'two': {},
                'three': []
            },
            {
                'one': 'two',
                'three': {}
            },
            {
                'five': 5,
                'six': 'six?'
            }
        ]

        for incorrect_directory_structure in incorrect_directory_structures:
            self.assertFalse(directory_structure_is_valid(incorrect_directory_structure))


class CreateDirectoryStructureTestCase(TestCase):
    def setUp(self) -> None:
        self.old_cwd: str = getcwd()
        self.tmp_dir: TemporaryDirectory = TemporaryDirectory()

        chdir(self.tmp_dir.name)

    def tearDown(self) -> None:
        chdir(self.old_cwd)
        self.tmp_dir.cleanup()

    def test_directories_are_properly_created(self) -> None:
        directory_structure = {
            'one': {
                'one_two': {
                    'one_two_three': {}
                }
            },
            'two': {}
        }
        current_directory = self.tmp_dir.name

        create_directory_structure(directory_structure)

        self.assertTrue('one' in listdir())
        self.assertTrue('two' in listdir())

        self.assertTrue('one_two' in listdir(f'{current_directory}/one'))
        self.assertTrue('one_two_three' in listdir(f'{current_directory}/one/one_two'))


class GenerateSelfSignedTlsCertificateTestCase(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.CERTIFICATE_NAME = 'certificate.pem'
        cls.KEY_NAME = 'key.pem'

    def setUp(self) -> None:
        self.old_cwd: str = getcwd()
        self.tmp_dir: TemporaryDirectory = TemporaryDirectory()

        chdir(self.tmp_dir.name)

    def tearDown(self) -> None:
        chdir(self.old_cwd)
        self.tmp_dir.cleanup()

    def test_tls_certificate_is_successfully_generated(self) -> None:
        generate_self_signed_tls_certificate(
            certificate_name=self.CERTIFICATE_NAME,
            key_name=self.KEY_NAME,
            domain='example.com'
        )

        self.assertTrue(Path(self.CERTIFICATE_NAME).is_file() and Path(self.KEY_NAME).is_file())

    def test_generated_tls_certificate_is_valid(self) -> None:
        generate_self_signed_tls_certificate(
            certificate_name=self.CERTIFICATE_NAME,
            key_name=self.KEY_NAME,
            domain='example.com'
        )

        self.assertEqual(
            run(('openssl', 'x509', '-noout', '-in', self.CERTIFICATE_NAME), capture_output=True).returncode,
            0
        )
