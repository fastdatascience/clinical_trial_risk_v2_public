import unittest

from app.models.user.base import is_password_allowed_pattern


class TestValidPasswords(unittest.TestCase):

    def test_all_lower(self):
        self.assertFalse(is_password_allowed_pattern("aaaaa"))

    def test_all_upper(self):
        self.assertFalse(is_password_allowed_pattern("AAAAA"))

    def test_randomly_generated_password(self):
        self.assertTrue(is_password_allowed_pattern("N6dfdmIMg9NYaJZe3MM="))

    def test_randomly_generated_password_too_long(self):
        self.assertFalse(is_password_allowed_pattern("N6dfdmIMg9NYaJZe3MM=A"))

    def test_randomly_generated_password_too_short(self):
        self.assertFalse(is_password_allowed_pattern("N6d="))

    def test_only_uppercase_and_special_chars_and_numbers_not_allowed(self):
        # we also need a lowercase
        self.assertFalse(is_password_allowed_pattern("A1@AAAAAAA"))

    def test_contains_asterisk(self):
        # we also need a lowercase
        self.assertTrue(is_password_allowed_pattern("HELLOo1*"))

    def test_contains_backslash(self):
        # we also need a lowercase
        self.assertTrue(is_password_allowed_pattern("HELLOo1\\"))
