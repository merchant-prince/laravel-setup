import unittest

from modules.validation import is_pascal_case, domain_is_valid


class PascalCaseTestCase(unittest.TestCase):
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


class DomainTestCase(unittest.TestCase):
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
