from unittest import TestCase
from re import sub
from subprocess import run

from modules.verification import (
    is_pascal_case, domain_is_valid,
    correct_docker_version_is_installed, correct_docker_compose_version_is_installed,
    correct_openssl_version_is_installed
)


class PascalCaseTestCase(TestCase):
    def test_returns_true_for_correctly_pascal_cased_strings(self) -> None:
        pascal_case_strings = [
            'One',
            'OneTwo',
            'OneTwoThree',
        ]

        for pascal_case_string in pascal_case_strings:
            self.assertTrue(is_pascal_case(pascal_case_string))

    def test_returns_false_for_incorrectly_pascal_cased_strings(self) -> None:
        non_pascal_cased_strings = [
            '',
            ' ',
            'one',
            'onE',
            'One Two',
            'OneTwo3',
            'oneTwo',
            'One-Two',
            'one-two',
            'One_two',
        ]

        for non_pascal_cased_string in non_pascal_cased_strings:
            self.assertFalse(is_pascal_case(non_pascal_cased_string))


class DomainTestCase(TestCase):
    def test_returns_true_for_valid_domains(self) -> None:
        valid_domains = [
            'application.local',
            'example.com',
            'one-two.gg',
            'api.application.org',
            'onetwo33.com',
        ]

        for valid_domain in valid_domains:
            self.assertTrue(domain_is_valid(valid_domain))

    def test_returns_false_for_invalid_domains(self) -> None:
        invalid_domains = [
            '://one.com',
            'one**.com',
        ]

        for invalid_domain in invalid_domains:
            self.assertFalse(domain_is_valid(invalid_domain))


class DockerVersionTestCase(TestCase):
    def setUp(self) -> None:
        self.current_docker_version = tuple(
            int(v) for v in
            run(
                ('docker', 'version', '--format', '{{.Server.Version}}'),
                capture_output=True,
                check=True
            ).stdout.decode('utf-8').strip().split('.')[:2]
        )

    def test_returns_true_for_correct_docker_version(self) -> None:
        self.assertTrue(correct_docker_version_is_installed(self.current_docker_version))

    def test_returns_false_for_smaller_docker_version(self) -> None:
        self.assertFalse(correct_docker_version_is_installed(tuple(v + 1 for v in self.current_docker_version)))


class DockerComposeVersionTestCase(TestCase):
    def setUp(self) -> None:
        self.current_docker_compose_version = tuple(
            int(v) for v in
            run(
                ('docker-compose', 'version', '--short'),
                capture_output=True,
                check=True
            ).stdout.decode('utf-8').strip().split('.')[:2]
        )

    def test_returns_true_for_correct_docker_compose_version(self) -> None:
        self.assertTrue(correct_docker_compose_version_is_installed(self.current_docker_compose_version))

    def test_returns_false_for_smaller_docker_compose_version(self) -> None:
        self.assertFalse(correct_docker_compose_version_is_installed(tuple(v + 1 for v in self.current_docker_compose_version)))


class OpensslVersionTestCase(TestCase):
    def setUp(self) -> None:
        self.current_openssl_version = tuple(
            int(sub(r'\D', '', v)) for v in
            run(
                ('openssl', 'version'),
                capture_output=True,
                check=True
            ).stdout.decode('utf-8').strip().split(' ')[1].split('.')
        )

    def test_returns_true_for_correct_openssl_version(self) -> None:
        self.assertTrue(correct_openssl_version_is_installed(self.current_openssl_version))

    def test_returns_false_for_smaller_openssl_version(self) -> None:
        self.assertFalse(correct_openssl_version_is_installed(tuple(v + 1 for v in self.current_openssl_version)))
