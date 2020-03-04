from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import librarian.models
import re

validation_levels = {
    "minor_error": [
        'Wrong ISBN', 'Empty Author', 'Zero Pages',
        'Language code must be letters', 'Link must start with http'],
    "major_error": ['Incorrect Format'],
    "duplicate_error": ['Possible Duplication']
}


def check_duplicates(book):
    query = librarian.models.Book.objects.filter(
        isbn=book.isbn,
        title=book.title)
    if query:
        raise ValidationError(_('Possible Duplication'))

    return False


def check_isbn(isbn):
    if len(isbn) != 13 and len(isbn) != 10 or re.match('0[10]', isbn):
        raise ValidationError(_('Wrong ISBN'))
    return True


def check_author(author):
    if author == '':
        raise ValidationError(_('Empty Author'))
    return True


def check_pages_count(page_count):
    if page_count == 0:
        raise ValidationError(_('Zero Pages'))
    return True


def check_language(language):
    if not re.match("[a-zA-Z]", language) or len(language) != 2:
        raise ValidationError(_('Language code must be 2 letters'))
    return True


def check_link(link):
    if not re.match("(http).*", link):
        raise ValidationError(_('Link must start with http'))
    return True
