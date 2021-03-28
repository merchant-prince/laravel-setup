import os
import unittest

from modules.utilities import cd


class CdTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.old_cwd = os.getcwd()
        self.destination = '/tmp'

        self.assertNotEqual(self.old_cwd, self.destination)

    def test_changes_directory_context_successfully(self) -> None:
        with cd(self.destination):
            self.assertEqual(os.getcwd(), self.destination)

        self.assertEqual(os.getcwd(), self.old_cwd)

    def test_changes_directory_context_back_when_exception_is_raised_within_with_context(self) -> None:
        try:
            with cd(self.destination):
                raise RuntimeError()
        except RuntimeError:
            self.assertEqual(os.getcwd(), self.old_cwd)

    def test_does_not_change_directory_context_when_invalid_destination_is_passed(self) -> None:
        non_existent_destination = '/NON/EXISTENT_DIRECTORY'

        try:
            with cd(non_existent_destination):
                pass
        except FileNotFoundError:
            self.assertEqual(os.getcwd(), self.old_cwd)
