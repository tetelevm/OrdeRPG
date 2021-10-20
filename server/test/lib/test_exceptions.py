from unittest import TestCase

from server.lib.exceptions import *


__all__ = ["ExceptionsTest"]


class ExceptionsTest(TestCase):
    def test_exception_from_doc(self):
        class TestException(ExceptionFromDoc):
            """This is test exception"""

        with self.assertRaises(TestException):
            raise TestException()

        try:
            raise TestException()
        except TestException as exc:
            self.assertEqual(exc.__str__(), "This is test exception")

    def test_exception_from_formatted_doc(self):
        class FirstTestException(ExceptionFromFormattedDoc):
            """Exception without parameters"""

        with self.assertRaises(FirstTestException):
            raise FirstTestException()

        try:
            raise FirstTestException()
        except FirstTestException as exc:
            self.assertEqual(exc.__str__(), "Exception without parameters")

        class SecondTestException(ExceptionFromFormattedDoc):
            """Exception with three parameters - {} - {} - {}"""

        try:
            raise SecondTestException("s", 1, list())
        except SecondTestException as exc:
            self.assertEqual(
                exc.__str__(),
                "Exception with three parameters - s - 1 - []"
            )

        try:
            raise SecondTestException("s")
        except SecondTestException as exc:
            expected_text = (
                "The error could not be formatted, but an error of the form\n"
                "Exception with three parameters - {} - {} - {}\n('s',)"
            )
            self.assertEqual(
                exc.__str__(),
                expected_text
            )
