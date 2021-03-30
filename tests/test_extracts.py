from argparse import ArgumentParser, Namespace
from typing import Mapping
from unittest import TestCase

from modules.extracts import parser, preliminary_checks


class ParserTestCase(TestCase):
    def setUp(self) -> None:
        self.argument_parser: ArgumentParser = parser()

    def test_script_name_is_laravel(self) -> None:
        self.assertEqual(self.argument_parser.prog, 'laravel')

    def test_script_has_an_action_subparser(self) -> None:
        arguments: Namespace = self.argument_parser.parse_args(['setup', 'placeholder_project_name'])

        self.assertTrue(hasattr(arguments, 'action'))

    def test_script_has_an_action_subparser_that_accepts_setup_as_its_argument(self) -> None:
        arguments: Namespace = self.argument_parser.parse_args(['setup', 'placeholder_project_name'])

        self.assertEqual(arguments.action, 'setup')

    def test_script_has_a_project_name_argument(self) -> None:
        project_name: str = 'OneTwo'
        arguments: Namespace = self.argument_parser.parse_args(['setup', project_name])

        self.assertEqual(arguments.project_name, project_name)

    def test_script_has_a_domain_optional_argument(self) -> None:
        project_domain = 'example.local'
        arguments: Namespace = self.argument_parser.parse_args(['setup', 'One', '--domain', project_domain])

        self.assertEqual(arguments.domain, project_domain)

    def test_script_domain_argument_defaults_to_applicationDOTlocal(self) -> None:
        arguments: Namespace = self.argument_parser.parse_args(['setup', 'One'])

        self.assertEqual(arguments.domain, 'application.local')

    def test_script_has_a_with_optional_argument_that_defaults_to_None(self) -> None:
        arguments: Namespace = self.argument_parser.parse_args(['setup', 'One'])

        self.assertIsNone(arguments.__getattribute__('with'))

    def test_script_with_argument_accepts_several_choices(self) -> None:
        choices = ['everything', 'horizon', 'sanctum', 'scout', 'socialite', 'telescope']

        arguments: Namespace = self.argument_parser.parse_args(['setup', 'One', '--with', *choices])

        self.assertListEqual(arguments.__getattribute__('with'), choices)

    def test_script_has_a_development_optional_switch(self) -> None:
        arguments: Namespace = self.argument_parser.parse_args(['setup', 'One'])

        self.assertFalse(arguments.development)

    def test_script_has_a_development_optional_switch_that_returns_True(self) -> None:
        arguments: Namespace = self.argument_parser.parse_args(['setup', 'One', '--development'])

        self.assertTrue(arguments.development)


class PreliminaryChecksTestCase(TestCase):
    def setUp(self) -> None:
        self.requirements: Mapping[str, str] = {
            'docker.version': '20.10.5',
            'docker-compose.version': '1.28.0',
            'openssl.version': '1.1.1',
            'git.version': '2.31.0',
        }

    def remove_program_version_key_and_assert_raises_keyerror(self, key: str):
        del self.requirements[key]

        with self.assertRaises(KeyError):
            preliminary_checks(requirements=self.requirements)

    def test_the_function_fails_if_docker_version_is_not_specified(self) -> None:
        self.remove_program_version_key_and_assert_raises_keyerror('docker.version')

    def test_the_function_fails_if_docker_compose_version_is_not_specified(self) -> None:
        self.remove_program_version_key_and_assert_raises_keyerror('docker-compose.version')

    def test_the_function_fails_if_openssl_version_is_not_specified(self) -> None:
        self.remove_program_version_key_and_assert_raises_keyerror('openssl.version')

    def test_the_function_fails_if_git_version_is_not_specified(self) -> None:
        self.remove_program_version_key_and_assert_raises_keyerror('git.version')
