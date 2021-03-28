from os import getcwd
from unittest import TestCase

from modules.utilities import cd


class CdTestCase(TestCase):
    def setUp(self) -> None:
        self.old_cwd = getcwd()
        self.destination = '/tmp'

        self.assertNotEqual(self.old_cwd, self.destination)

    def test_changes_directory_context_successfully(self) -> None:
        with cd(self.destination):
            self.assertEqual(getcwd(), self.destination)

        self.assertEqual(getcwd(), self.old_cwd)

    def test_changes_directory_context_back_when_exception_is_raised_within_with_context(self) -> None:
        try:
            with cd(self.destination):
                raise RuntimeError()
        except RuntimeError:
            self.assertEqual(getcwd(), self.old_cwd)

    def test_does_not_change_directory_context_when_invalid_destination_is_passed(self) -> None:
        non_existent_destination = '/NON/EXISTENT_DIRECTORY'

        try:
            with cd(non_existent_destination):
                pass
        except FileNotFoundError:
            self.assertEqual(getcwd(), self.old_cwd)
