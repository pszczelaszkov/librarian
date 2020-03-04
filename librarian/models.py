from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import models
from . import validators

AUTHOR_MAX = 60
TITLE_MAX = 200
ISBN_MAX = 13
LINK_MAX = 300
LANGUAGE_MAX = 2


class Book(models.Model):
    title = models.CharField(max_length=TITLE_MAX)
    author = models.CharField(max_length=AUTHOR_MAX)
    publication_date = models.DateField()
    isbn = models.CharField(max_length=ISBN_MAX)
    page_count = models.IntegerField()
    cover_link = models.CharField(max_length=LINK_MAX)
    language = models.CharField(max_length=LANGUAGE_MAX)

    def clean(self):
        try:
            self.clean_fields()
        except ValidationError:
            raise ValidationError(_('Incorrect Format'), code='major_error')

        validators.check_isbn(self.isbn)
        validators.check_author(self.author)
        validators.check_title(self.title)
        validators.check_pages_count(self.page_count)
        validators.check_language(self.language)
        validators.check_link(self.cover_link)

    def set_best_isbn(self, candidates):
        best_candidate = "0000000000"
        for length in [10, 13]:
            for isbn in candidates:
                if len(isbn) == length:
                    best_candidate = isbn

        self.isbn = best_candidate
        return best_candidate
