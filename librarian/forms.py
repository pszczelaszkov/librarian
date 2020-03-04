from django import forms
from django.forms import ModelForm
from librarian import models


class BooksImportForm(forms.Form):
    search = forms.CharField(
        max_length=100, label="search",
        required=False, widget=forms.TextInput())
    inauthor = forms.CharField(
        max_length=models.AUTHOR_MAX, label="author",
        required=False, widget=forms.TextInput())
    intitle = forms.CharField(
        max_length=models.TITLE_MAX, label="title",
        required=False, widget=forms.TextInput())
    inpublisher = forms.CharField(
        max_length=40, label="publisher",
        required=False, widget=forms.TextInput())
    subject = forms.CharField(
        max_length=20, label="subject",
        required=False, widget=forms.TextInput())
    isbn = forms.CharField(
        max_length=models.ISBN_MAX, label="isbn",
        required=False, widget=forms.TextInput())


class BooksFilterForm(forms.Form):
    author = forms.CharField(
        max_length=models.AUTHOR_MAX, label="author",
        required=False, widget=forms.TextInput())
    title = forms.CharField(
        max_length=models.TITLE_MAX, label="title",
        required=False, widget=forms.TextInput())
    language = forms.CharField(
        max_length=models.LANGUAGE_MAX, label="language",
        required=False, widget=forms.TextInput(attrs={"style": "width: 50px"}))
    publication_from = forms.DateField(
        label="from", required=False,
        widget=forms.TextInput(attrs={"placeholder": "YYYY-mm-dd"}))
    publication_to = forms.DateField(
        label="to", required=False,
        widget=forms.TextInput(attrs={"placeholder": "YYYY-mm-dd"}))


class BooksChangeForm(ModelForm):
    class Meta:
        model = models.Book
        fields = '__all__'
        widgets = {
            "publication_date": forms.TextInput(
                attrs={"placeholder": "YYYY-mm-dd"}),
            "id": forms.HiddenInput
        }
