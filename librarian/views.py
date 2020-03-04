from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.http import HttpResponse
from django.urls import reverse
from django.core import serializers
from librarian.models import Book

from . import forms
from . import helpers


def index(request):
    return render(request, "librarian/index.html")


def books_list(request):
    books = Book.objects.all()
    if(request.method == "POST"):
        form = forms.BooksFilterForm(request.POST)
        if(form.is_valid()):
            books = helpers.books_filter(books, form.cleaned_data)
            print(type(form.cleaned_data['publication_from']))
    else:
        form = forms.BooksFilterForm()

    context = {"form": form, "books": books}
    return render(request, "librarian/books_list.html", context)


def books_manage(request):
    if(request.method == "GET"):
        id = request.GET.get('editid', False)
        form = helpers.books_get_form_instance(id)
    elif(request.method == "POST"):
        id = request.POST.get('id', False)
        form = forms.BooksChangeForm(request.POST)
        print(request.POST)
        if helpers.books_save_book_form(id, form):
            return HttpResponseRedirect(reverse("books_list"))

    context = {"form": form}
    return render(request, "librarian/books_manage.html", context)


def books_import(request):
    books = []
    if(request.method == "POST"):
        form = forms.BooksImportForm(request.POST)
        books_saved = helpers.books_google_import(request.POST)
        if(form.is_valid()):
            data = helpers.books_google_fetch(search_data=form.cleaned_data)
            books = helpers.books_google_parse(data)
            helpers.books_check_compatibility(books)
        if books_saved:
            return HttpResponseRedirect(reverse("books_list"))
    else:
        form = forms.BooksImportForm()

    context = {"form": form, "books": books}
    return render(request, "librarian/books_import.html", context)


def books_rest(request):
    books = Book.objects.all()
    books = helpers.books_filter(books, request.GET)
    json_data = serializers.serialize('json', books, ensure_ascii=False)
    return HttpResponse(json_data, content_type="application/json")
