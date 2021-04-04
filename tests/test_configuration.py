from argparse import ArgumentParser, Namespace
from os import mkdir
from typing import List, Mapping, Union
from unittest import TestCase

from modules.configuration import ConfigurationAccessorType
from modules.configuration import create_argument_parser, create_configuration_accessor, validated_script_arguments
from tests.utilities import tmpdir


class ParserTestCase(TestCase):
    def setUp(self) -> None:
        self.argument_parser: ArgumentParser = create_argument_parser()

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

    def test_script_domain_argument_defaults_to_application_local(self) -> None:
        arguments: Namespace = self.argument_parser.parse_args(['setup', 'One'])

        self.assertEqual(arguments.domain, 'application.local')

    def test_script_has_a_with_optional_argument_that_defaults_to_None(self) -> None:
        arguments: Namespace = self.argument_parser.parse_args(['setup', 'One'])

        self.assertIsNone(arguments.__getattribute__('with'))

    def test_script_with_argument_accepts_several_choices(self) -> None:
        choices = ['horizon', 'sanctum', 'scout', 'socialite', 'telescope']

        arguments: Namespace = self.argument_parser.parse_args(['setup', 'One', '--with', *choices])

        self.assertListEqual(arguments.__getattribute__('with'), choices)


class ValidatedScriptArgumentsTestCase(TestCase):
    def setUp(self) -> None:
        self.script_arguments: Namespace = Namespace()

    def test_raises_runtime_error_if_project_name_is_not_pascal_cased(self) -> None:
        self.script_arguments.__setattr__('project_name', 'not_pascalCased')

        with self.assertRaises(RuntimeError):
            validated_script_arguments(self.script_arguments)

    def test_raises_runtime_error_if_directory_with_same_name_as_project_exists_in_cwd(self) -> None:
        project_name: str = 'OneTwo'

        self.script_arguments.__setattr__('project_name', project_name)

        with tmpdir():
            mkdir(project_name)

            with self.assertRaises(RuntimeError):
                validated_script_arguments(self.script_arguments)

    def test_raises_runtime_error_if_domain_name_is_invalid(self) -> None:
        self.script_arguments.__setattr__('project_name', 'CorrectProjectName')
        self.script_arguments.__setattr__('domain', 'invalid//domain::tld')

        with self.assertRaises(RuntimeError):
            validated_script_arguments(self.script_arguments)

    def test_returns_project_name_domain_and_modules(self) -> None:
        project_name: str = 'ProjectName'
        domain: str = 'domain.tld'
        packages: List = ['one', 'two', 'three']

        self.script_arguments.__setattr__('project_name', project_name)
        self.script_arguments.__setattr__('domain', domain)
        self.script_arguments.__setattr__('with', packages)

        result: Mapping[str, Union[str, List]] = validated_script_arguments(self.script_arguments)

        self.assertDictEqual(
            {
                'project_name': project_name,
                'project_domain': domain,
                'project_packages': packages,
            },
            dict(result)
        )


class CreateConfigurationAccessorTestCase(TestCase):
    def setUp(self) -> None:
        self.script_arguments: Mapping[str, Union[str, List]] = {
            'project_name': 'ProjectName',
            'project_domain': 'project-domain.tld',
            'project_packages': ['one', 'two', 'three'],
        }
        self.configuration: ConfigurationAccessorType = create_configuration_accessor(**self.script_arguments)

    def test_configuration_accessor_returns_the_appropriate_values_when_queried(self) -> None:
        self.assertEqual(self.configuration('project.name'), self.script_arguments['project_name'])
        self.assertEqual(self.configuration('project.domain'), self.script_arguments['project_domain'])
        self.assertListEqual(self.configuration('project.packages'), self.script_arguments['project_packages'])
        self.assertEqual(self.configuration('services.postgres.database'),
                         self.script_arguments['project_name'].lower())
