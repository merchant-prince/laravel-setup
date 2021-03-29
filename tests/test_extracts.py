from argparse import ArgumentParser, Namespace
from unittest import TestCase

from modules.extracts import parser


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
