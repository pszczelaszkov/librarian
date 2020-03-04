from librarian import validators
from django.core.exceptions import ValidationError
import unittest


class ValidatorsTestCase(unittest.TestCase):
    def test_isbn(self):
        self.assertRaises(ValidationError, validators.check_isbn, "12345")
        self.assertRaises(ValidationError, validators.check_isbn, "0000000000")
        self.assertTrue(validators.check_isbn, "0000000001")
        self.assertTrue(validators.check_isbn, "0000000001234")

    def test_author(self):
        self.assertRaises(ValidationError, validators.check_author, "")
        self.assertTrue(validators.check_author, "Autor")

    def test_pages_count(self):
        self.assertRaises(ValidationError, validators.check_pages_count, 0)
        self.assertTrue(validators.check_pages_count, 28)

    def test_language(self):
        self.assertRaises(ValidationError, validators.check_language, "")
        self.assertRaises(ValidationError, validators.check_language, "11")
        self.assertRaises(ValidationError, validators.check_language, "A")
        self.assertTrue(validators.check_language, "PL")
        self.assertTrue(validators.check_language, "pl")

    def test_link(self):
        self.assertRaises(
            ValidationError, validators.check_link, "books.google.pl/foto.jpg")
        self.assertTrue(
            validators.check_link, "https://books.google.pl/foto.jpg")


if __name__ == "__main__":
    unittest.main()
