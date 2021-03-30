from re import compile
from subprocess import run
from typing import Tuple
from unittest import TestCase

from modules.verification import is_pascal_case, domain_is_valid, correct_version_is_installed


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


class CorrectVersionIsInstalledTestCase(TestCase):
    @staticmethod
    def docker_version_command() -> Tuple[str, ...]:
        return 'docker', 'version', '--format', '{{.Server.Version}}'

    @staticmethod
    def docker_compose_version_command() -> Tuple[str, ...]:
        return 'docker-compose', 'version', '--short'

    @staticmethod
    def openssl_version_command() -> Tuple[str, ...]:
        return 'openssl', 'version'

    @staticmethod
    def git_version_command() -> Tuple[str, ...]:
        return 'git', 'version'

    @staticmethod
    def current_version(command: Tuple[str, ...]) -> str:
        return run(command, capture_output=True, check=True).stdout.decode('utf-8').strip()

    def test_returns_true_for_correct_docker_version(self) -> None:
        self.assertTrue(
            correct_version_is_installed(
                self.docker_version_command(),
                self.current_version(self.docker_version_command())
            )
        )

    def test_returns_true_for_correct_docker_compose_version(self) -> None:
        self.assertTrue(
            correct_version_is_installed(
                self.docker_compose_version_command(),
                self.current_version(self.docker_compose_version_command())
            )
        )

    def test_returns_true_for_correct_openssl_version(self) -> None:
        self.assertTrue(
            correct_version_is_installed(
                self.openssl_version_command(),
                self.current_version(self.openssl_version_command())
            )
        )

    def test_returns_true_for_correct_git_version(self) -> None:
        self.assertTrue(
            correct_version_is_installed(
                self.git_version_command(),
                self.current_version(self.git_version_command())
            )
        )

    def test_returns_false_for_smaller_docker_version(self) -> None:
        self.assertFalse(
            correct_version_is_installed(
                self.docker_version_command(),
                '.'.join(str(int(v) + 1) for v in self.current_version(self.docker_version_command()).split('.'))
            )
        )

    def test_returns_false_for_smaller_docker_compose_version(self) -> None:
        self.assertFalse(
            correct_version_is_installed(
                self.docker_compose_version_command(),
                '.'.join(
                    str(int(v) + 1) for v in self.current_version(self.docker_compose_version_command()).split('.')
                )
            )
        )

    def test_returns_false_for_smaller_openssl_version(self) -> None:
        self.assertFalse(
            correct_version_is_installed(
                self.openssl_version_command(),
                '.'.join(
                    str(int(v) + 1) for v in
                    compile(r'.*?(?P<version>\d+\.\d+\.\d+).*?').match(
                        self.current_version(self.openssl_version_command())
                    ).groupdict()['version'].split('.')
                )
            )
        )

    def test_returns_false_for_smaller_git_version(self) -> None:
        self.assertFalse(
            correct_version_is_installed(
                self.git_version_command(),
                '.'.join(
                    str(int(v) + 1) for v in
                    compile(r'.*?(?P<version>\d+\.\d+\.\d+).*?').match(
                        self.current_version(self.git_version_command())
                    ).groupdict()['version'].split('.')
                )
            )
        )
