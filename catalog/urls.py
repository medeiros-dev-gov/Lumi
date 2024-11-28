from django.urls import path, register_converter
from . import views

# Conversor UUID
class UUIDConverter:
    regex = '[0-9a-fA-F-]{36}'  # Expressão regular para identificar UUIDs

    def to_python(self, value):
        return value  # Retorna o valor como está (sem modificação)

    def to_url(self, value):
        return str(value)  # Converte o valor para string ao gerar a URL

register_converter(UUIDConverter, 'uuid')  # Registra o conversor UUID no Django

urlpatterns = [
    # URL padrão
    path('', views.index, name='index'),

    # URLs para livros
    path('books/', views.BookListView.as_view(), name='books'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),
    path('book/create/', views.BookCreate.as_view(), name='book-create'),
    path('book/<int:pk>/update/', views.BookUpdate.as_view(), name='book-update'),
    path('book/<int:pk>/delete/', views.BookDelete.as_view(), name='book-delete'),
    path('book/<int:pk>/borrow/', views.borrow_book, name='borrow-book'),

    # URLs para autores
    path('authors/', views.AuthorListView.as_view(), name='authors'),
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),
    path('author/create/', views.AuthorCreate.as_view(), name='author-create'),
    path('author/<int:pk>/update/', views.AuthorUpdate.as_view(), name='author-update'),
    path('author/<int:pk>/delete/', views.AuthorDelete.as_view(), name='author-delete'),

    # URLs para gêneros
    path('genres/', views.GenreListView.as_view(), name='genres'),
    path('genre/<int:pk>/', views.GenreDetailView.as_view(), name='genre-detail'),
    path('genre/create/', views.GenreCreate.as_view(), name='genre-create'),
    path('genre/<int:pk>/update/', views.GenreUpdate.as_view(), name='genre-update'),
    path('genre/<int:pk>/delete/', views.GenreDelete.as_view(), name='genre-delete'),

    # URLs para idiomas
    path('languages/', views.LanguageListView.as_view(), name='languages'),
    path('language/<int:pk>/', views.LanguageDetailView.as_view(), name='language-detail'),
    path('language/create/', views.LanguageCreate.as_view(), name='language-create'),
    path('language/<int:pk>/update/', views.LanguageUpdate.as_view(), name='language-update'),
    path('language/<int:pk>/delete/', views.LanguageDelete.as_view(), name='language-delete'),

    # URLs para instâncias de livros
    path('bookinstances/', views.BookInstanceListView.as_view(), name='bookinstances'),
    path('bookinstance/<uuid:pk>/', views.BookInstanceDetailView.as_view(), name='bookinstance-detail'),
    path('bookinstance/create/', views.BookInstanceCreate.as_view(), name='bookinstance-create'),
    path('bookinstance/<uuid:pk>/update/', views.BookInstanceUpdate.as_view(), name='bookinstance-update'),
    path('bookinstance/<uuid:pk>/delete/', views.BookInstanceDelete.as_view(), name='bookinstance-delete'),
    path('bookinstance/<uuid:pk>/renew/', views.renew_book, name='renew-book'),

    # URLs para livros emprestados
    path('my-borrowed/', views.my_borrowed_books, name='my-borrowed'),
    path('borrow-book/', views.borrow_book, name='borrow-book'),

        # URL para renovar livro para usuário comum
     path('catalog/bookinstance/<uuid:pk>/renew/', views.renew_book, name='renew-book'),


    # URL para renovar livro do bibliotecário
    path('catalog/renew-book/<uuid:pk>/', views.renew_book, name='renew-book'),
]
