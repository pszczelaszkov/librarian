from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import librarian.models
import re


def check_duplicates(book):
    query = librarian.models.Book.objects.filter(
        isbn=book.isbn,
        title=book.title)
    if query:
        raise ValidationError(
            _('Possible Duplication'),
            code='duplicate_error')

    return False


def check_isbn(isbn):
    if len(isbn) != 13 and len(isbn) != 10 or re.match('0[10]', isbn):
        raise ValidationError(_('Wrong ISBN'), code='minor_error')
    return True


def check_author(author):
    if author == '':
        raise ValidationError(_('Empty Author'), code='minor_error')
    return True


def check_title(title):
    if title == '':
        raise ValidationError(_('Empty Title'), code='major_error')
    return True


def check_pages_count(page_count):
    if page_count == 0:
        raise ValidationError(_('Zero Pages'), code='minor_error')
    return True


def check_language(language):
    if not re.match("[a-zA-Z]", language) or len(language) != 2:
        raise ValidationError(
            _('Language code must be 2 letters'),
            code='minor_error')
    return True


def check_link(link):
    if not re.match("(http).*", link):
        raise ValidationError(
            _('Link must start with http'),
            code='minor_error')
    return True
