from django.test import TransactionTestCase, Client
from django.core import serializers
from django.core.exceptions import ValidationError
from librarian.models import Book
from librarian.forms import BooksChangeForm
from . import validators
from . import helpers


class BookTestCase(TransactionTestCase):

    def setUp(self):
        Book.objects.create(
            title="Marry",
            author="Noname",
            publication_date="2010-05-20",
            isbn="9780547951915",
            page_count=5,
            cover_link="https://books.google.com/books/",
            language="it"
            )

        Book.objects.create(
            title="John",
            author="Terry",
            publication_date="2020-05-20",
            isbn="9780547951910",
            page_count=5,
            cover_link="https://books.google.com/books/",
            language="pl"
            )

        Book.objects.create(
            title="Kaliba",
            author="Muzyka",
            publication_date="1980-05-20",
            isbn="9780547951976",
            page_count=5,
            cover_link="https://books.google.com/books/",
            language="en"
            )

        Book.objects.create(
            title="Books",
            author="Wisdom",
            publication_date="2000-01-14",
            isbn="9780547951978",
            page_count=5,
            cover_link="https://books.google.com/books/",
            language="es"
            )

        self.broken_book = Book(
            title="Ursa Major",
            author="Universe",
            publication_date="",
            isbn="9780544519789",
            page_count="56",
            cover_link="https://books.google.com/books/",
            language="it"
        )

        self.single_book = {
            'kind': 'books#volume',
            'volumeInfo': {
                'title': 'Ursa Major',
                'authors': ['Universe'],
                'publishedDate': '2020-05-10',
                'industryIdentifiers': [
                    {
                        'type': "ISBN_10",
                        'identifier': '9780547451'
                    },
                    {
                        'type': "ISBN_13",
                        'identifier': '9780544519789'
                    }
                ],
                'pageCount': '56',
                'imageLinks': {
                    'thumbnail': 'https://books.google.com/books/'
                },
                'language': 'it'
            },
            'id': '12345'
        }

        self.single_minor_broken_book = {
            'kind': 'books#volume',
            'volumeInfo': {
                'title': 'Alpha Centauri',
                'authors': ['Universe'],
                'publishedDate': '2020-05-10',
                'industryIdentifiers': [
                    {
                        'type': "ISBN_10",
                        'identifier': '978054745'
                    },
                    {
                        'type': "ISBN_13",
                        'identifier': '97805445178'
                    }
                ],
                'pageCount': '56',
                'imageLinks': {
                    'thumbnail': 'https://books.google.com/books/'
                },
                'language': 'it'
            },
            'id': '12347'
        }

        self.single_major_broken_book = {
            'kind': 'books#volume',
            'volumeInfo': {
                'title': 'Sigarius B',
                'authors': [
                    'Marian Bisanz-Prakken',
                    'Rembrandt Harmenszoon van Rijn',
                    'Milwaukee Art Museum'],
                'publishedDate': '16??',
                'industryIdentifiers': [
                    {
                        'type': "ISBN_10",
                        'identifier': '9780547451'
                    },
                    {
                        'type': "ISBN_13",
                        'identifier': '978054451978'
                    }
                ],
                'pageCount': '56',
                'imageLinks': {
                    'thumbnail': 'https://books.google.com/books/'
                },
                'language': 'it'
            },
            'id': '12346'
        }

        self.multiple_books = {
            'kind': 'books#volumes',
            'items': [
                self.single_book,
                self.single_minor_broken_book,
                self.single_major_broken_book
            ]
        }

        self.examplePost = {
            'title': 'Pan Kracy', 'author': 'Szymon',
            'publication_date': '1990-05-20',
            'isbn': '9781456781767',
            'page_count': '5',
            'cover_link': 'http://www.google.pl',
            'language': 'en'
            }

    def test_duplicate(self):
        duplicate = Book.objects.get(title="Marry")
        self.assertRaises(
            ValidationError,
            validators.check_duplicates, duplicate)

        duplicate.title = "Mary"
        self.assertFalse(validators.check_duplicates(duplicate))

        duplicate.title = "Marry"
        duplicate.isbn = "9780557951973"
        self.assertFalse(validators.check_duplicates(duplicate))

    def test_get_form_instance(self):
        instance = Book.objects.get(title="Marry")

        # Must return same instance value
        form = helpers.books_get_form_instance(id=1)
        self.assertEquals(form.instance, instance)

        # Must return instance of BookChangeForm
        form = helpers.books_get_form_instance(id=0)
        self.assertIsInstance(form, BooksChangeForm)

        # Must return same form with altered instance
        form = BooksChangeForm()
        return_form = helpers.books_get_form_instance(id=1, form=form)
        self.assertIs(form, return_form)
        self.assertEquals(form.instance, instance)

        # Must be intact
        form = BooksChangeForm()
        return_form = helpers.books_get_form_instance(id=0, form=form)
        self.assertIs(form, return_form)
        self.assertIs(form.instance, return_form.instance)

    def test_books_fetch(self):
        result = helpers.books_google_fetch()
        self.assertEquals(
            result.get("error", '')
            .get('code'),
            400)

        result = helpers.books_google_fetch(direct_id="xxxxxxxxxxxx")
        self.assertEquals(
            result.get("error", '')
            .get('code'),
            404)

        result = helpers.books_google_fetch(search_data={'search': "book"})
        self.assertEquals(
            result.get("kind", ''),
            'books#volumes')

    def test_books_parse(self):
        result = helpers.books_google_parse(self.single_book)
        self.assertEqual(len(result), 2)
        self.assertIn('id', result)
        self.assertIn('book', result)

        result = helpers.books_google_parse(self.multiple_books)
        self.assertEqual(len(result), 3)
        self.assertEqual(result[1]["book"].isbn, '0000000000')  # broken isbn's
        self.assertEqual(result[2]["book"].publication_date, '')  # broken date
        self.assertEqual(result[2]["book"].isbn, '9780547451')  # revert to 10s

    def test_books_compatibility(self):
        result = helpers.books_google_parse(self.multiple_books)
        duplicate = Book.objects.get(id=1)
        result.append({'id': '123353', 'book': duplicate})
        helpers.books_check_compatibility(result)
        self.assertNotIn('validation', result[0])
        self.assertEqual(result[1]['validation'], "minor_error")
        self.assertEqual(result[2]['validation'], "major_error")
        self.assertEqual(result[3]['validation'], "duplicate_error")

    def test_google_import(self):
        data = {'importxxxxxxxx': "xxxxxxxxxxxx"}
        self.assertFalse(helpers.books_google_import(data))

    def test_books_filter(self):
        books = Book.objects.all()
        result = helpers.books_filter(books, {'title': 'Kaliba'})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "Kaliba")

        result = helpers.books_filter(books, {'author': 'Wisdom'})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "Books")

        result = helpers.books_filter(books, {'language': 'pl'})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "John")

        result = helpers.books_filter(books, {
            'publication_from': '1999-01-01', 'publication_to': '2001-01-01'})
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].title, "Books")

    def test_save_book_form(self):
        form = BooksChangeForm()
        self.assertFalse(helpers.books_save_book_form(0, form))
        form = BooksChangeForm(self.examplePost)
        self.assertTrue(helpers.books_save_book_form(0, form))

    def test_rest(self):
        client = Client()
        response = client.get('/books_rest/?author=Terry')

        result = serializers.deserialize("json", response.content)
        data = eval(response.content.decode())
        self.assertEqual(data[0]['fields']['title'], 'John')
