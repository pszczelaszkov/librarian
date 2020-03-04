from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.utils import DataError
from dateutil.parser import parse, ParserError
import requests
import re
from librarian.models import Book
from . import validators
from . import forms

book_filters = {
    'author': lambda books, author: books.filter(author__exact=author),
    'title': lambda books, title: books.filter(title__icontains=title),
    'language': lambda books, language: books.filter(language__exact=language),
    'publication_from': lambda books, publication_from: books.filter(
        publication_date__gte=publication_from),
    'publication_to': lambda books, publication_to: books.filter(
        publication_date__lte=publication_to),
}


def books_get_form_instance(id, form=None):
    ''' Return BooksChangeForm with attached instance.

        Keyword arguments:
        id -- database id of desired instance
        form -- optional form at which instance should be attached
    '''
    try:
        instance = Book.objects.get(id=id)
    except ObjectDoesNotExist:
        instance = False

    if instance:
        if form:
            form.instance = instance
            form.id = id
        else:
            form = forms.BooksChangeForm(instance=instance)
            form.id = id
    elif not form:
        form = forms.BooksChangeForm()

    return form


def books_save_book_form(id, form):
    ''' Saves provided form, alters existing if provided id exist.
        Return True if succeeded.

        Keyword arguments:
        id -- database id of desired instance
        form -- form to save
    '''
    form = books_get_form_instance(id, form)
    if(form.is_valid()):
        form.save()
        return True
    return False


def books_filter(books, filters):
    ''' Return QuerySet filtered version of provided one.
        Uses book_filters dict as filters register.

        Keyword arguments:
        books -- QuerySet that should be filtered
        filters -- Dict with filter key: value
    '''
    for field in filters:
        if field in book_filters:
            value = filters[field]
            if(value):
                books = book_filters[field](books, value)
    return books


def books_google_fetch(search_data=None, direct_id=None):
    ''' Return string of json formatted result from google api.
        Only one argument should be provided.

        Keyword arguments:
        search_data -- Dict with provided 'q' values for group search
        direct_id -- direct id of single book volume
    '''
    url = "https://www.googleapis.com/books/v1/volumes"
    q = ''
    if search_data:
        q = search_data['search']
        for k, v in search_data.items():
            if(k == "search" or not v):
                continue
            q += '+' + k + ":" + v

        if len(q) and q[0] == '+':
            q = q[1:]
    elif direct_id:
        url += "/" + direct_id

    querystring = {"q": q, 'country': 'pl'}
    response = requests.request("GET", url, params=querystring)
    return response.json()


def books_google_import(data):
    ''' Import directly volumes from google api.
        Return True if at least one was saved.

        Keyword argument:
        data -- Dict of import ids i.e. {'import<id>: id'}
    '''
    done = False
    for checkbox in data:
        if re.match('import.*', checkbox):
            json_data = books_google_fetch(direct_id=data[checkbox])
            try:
                book = books_google_parse(json_data)
                if book:
                    book.get('book').save()
                    done = True
            except (ValidationError, DataError):
                pass

    return done


def books_google_get_book(data):
    ''' Return {'direct_id': 'id','book': Book} parsed from json stream

        Keyword argument:
        data -- str json stream that contains "item" from google api
    '''
    volume = data.get('volumeInfo', {})
    id = data.get('id', '')

    new_book = Book()
    new_book.title = volume.get('title', '')
    new_book.author = ','.join(
        [author for author in volume.get('authors', '')])
    new_book.page_count = volume.get('pageCount', 0)
    new_book.language = volume.get('language', '--')
    new_book.cover_link = volume.get('imageLinks', {}).get('thumbnail', "None")

    isbn = []
    for identifier in volume.get('industryIdentifiers', []):
        if re.match("ISBN.*", identifier['type']):
            isbn.append(identifier['identifier'])
    new_book.set_best_isbn(isbn)

    try:
        new_book.publication_date = parse(
            volume.get('publishedDate', '')).date()
    except ParserError:
        new_book.publication_date = ''

    return {'id': id, 'book': new_book}


def books_check_compatibility(books):
    ''' Checks database compatibility of provided books
        Alters provided Dict with "validation": level,
        only if validation issue is detected

        Keyword argument:
        books -- List with {'direct_id': 'id','book': Book} dicts
    '''
    for book_bundle in books:
        book = book_bundle.get("book")
        try:
            validators.check_duplicates(book)
            book.clean()
        except ValidationError as validation:
            book_bundle["validation"] = validation.code


def books_google_parse(data):
    ''' Return {'direct_id': id, 'book': Book} or List of them,
        Depends on how many books holds provided json stream.

        Keyword argument:
        data -- json stream obtained from google api
    '''
    books = []
    kind = data.get("kind", '')
    if kind == "books#volumes":
        for volume in data.get('items', []):
            books.append(books_google_get_book(volume))
        return books
    elif kind == "books#volume":
        return books_google_get_book(data)

    return books
