from django.urls import path, register_converter
from . import views

# Registrar o conversor UUID
class UUIDConverter:
    regex = '[0-9a-fA-F-]{36}'  # Expressão regular para identificar UUIDs

    def to_python(self, value):
        return value  # Retorna o valor como está (sem modificação)

    def to_url(self, value):
        return str(value)  # Converte o valor para string ao gerar a URL

register_converter(UUIDConverter, 'uuid')  # Registra o conversor UUID no Django

urlpatterns = [
    path('', views.index, name='index'),
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>', views.BookDetailView.as_view(), name='book-detail'),
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>', views.AuthorDetailView.as_view(), name='author-detail'),
]

# Adicionando configurações de URL para a visualização dos livros emprestados pelo usuário
urlpatterns += [
    path('my-borrowed/', views.my_borrowed_books, name='my-borrowed'),
    path('borrow-book/', views.borrow_book, name='borrow-book'),
]

# URLConf para o bibliotecário renovar um livro
urlpatterns += [
    path('book/<int:pk>/renew/', views.renew_book_librarian, name='renew-book-librarian'),
]

# Adicionando URLs para criar, atualizar e excluir autores
urlpatterns += [
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),
    path('bookinstance/<uuid:pk>/renew/', views.renew_book, name='renew-book'),  # URL para renovar instâncias de livros
]

# Adicionando URLs para criar, atualizar e excluir livros
urlpatterns += [
    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
]

# Adicionando URLs para listar, ver, criar, atualizar e excluir gêneros
urlpatterns += [
    path('genres/', views.GenreListView.as_view(), name='genres'),
    path('genre/<int:pk>', views.GenreDetailView.as_view(), name='genre-detail'),
    path('genre/create/', views.GenreCreate.as_view(), name='genre-create'),
    path('genre/<int:pk>/update/', views.GenreUpdate.as_view(), name='genre-update'),
    path('genre/<int:pk>/delete/', views.GenreDelete.as_view(), name='genre-delete'),
]

# Adicionando URLs para listar, ver, criar, atualizar e excluir idiomas
urlpatterns += [
    path('languages/', views.LanguageListView.as_view(), name='languages'),
    path('language/<int:pk>', views.LanguageDetailView.as_view(), name='language-detail'),
    path('language/create/', views.LanguageCreate.as_view(), name='language-create'),
    path('language/<int:pk>/update/', views.LanguageUpdate.as_view(), name='language-update'),
    path('language/<int:pk>/delete/', views.LanguageDelete.as_view(), name='language-delete'),
]

# Adicionando URLs para listar, ver, criar, atualizar e excluir instâncias de livros
urlpatterns += [
    path('bookinstances/', views.BookInstanceListView.as_view(), name='bookinstances'),
    path('bookinstance/<uuid:pk>', views.BookInstanceDetailView.as_view(), name='bookinstance-detail'),
    path('bookinstance/create/', views.BookInstanceCreate.as_view(), name='bookinstance-create'),
    path('bookinstance/<uuid:pk>/update/', views.BookInstanceUpdate.as_view(), name='bookinstance-update'),
    path('bookinstance/<uuid:pk>/delete/', views.BookInstanceDelete.as_view(), name='bookinstance-delete'),
    path('bookinstance/<uuid:pk>/renew/', views.renew_book, name='renew-book'),
]

urlpatterns += [
    path('book/<int:pk>/borrow/', views.borrow_book, name='borrow-book'),
]