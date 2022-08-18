from unittest import TestCase

import phonenumbers
from ..phonenumbers import format_number


class TestFormatPhoneNumber(TestCase):

    def test_format_number(self):
        formatted_number = "+919072822520"

        # Type 1
        self.assertEqual(
            format_number("919072822520"),
            formatted_number
        )

        # Type 2
        self.assertEqual(
            format_number("+919072822520"),
            formatted_number
        )

        # Type 3
        self.assertEqual(
            format_number("00919072822520"),
            formatted_number
        )

        # Type 4
        self.assertEqual(
            format_number("+91 9072822520"),
            formatted_number
        )

        # Type 5
        self.assertEqual(
            format_number("0091 9072822520"),
            formatted_number
        )

    def test_invalid_number(self):
        with self.assertRaises(phonenumbers.NumberParseException):
            format_number("non-number")

        with self.assertRaises(phonenumbers.NumberParseException):
            format_number("91 907282252011")

    def test_empty(self):
        self.assertEqual(
            "",
            format_number("")
        )
