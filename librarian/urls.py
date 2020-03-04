from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('books_list/', views.books_list, name='books_list'),
    path('books_manage/', views.books_manage, name='books_manage'),
    path('books_import/', views.books_import, name='books_import'),
    path('books_rest/', views.books_rest, name='books_rest')
]
