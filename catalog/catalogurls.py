# catalog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # URL para a página de todos os livros
    path('', views.BookListView.as_view(), name='book-list'),

    # URL para o detalhe de um livro específico
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book-detail'),

    # URL para a página de livros emprestados do usuário
    path('myborrowed/', views.BorrowedBooksListView.as_view(), name='my-borrowed-books'),

    # URL para listar todos os livros emprestados
    path('allborrowed/', views.AllBorrowedBooksListView.as_view(), name='all-borrowed-books'),

    # URL para o painel de autores
    path('authors/', views.AuthorListView.as_view(), name='author-list'),

    # URL para o detalhe de um autor
    path('author/<int:pk>/', views.AuthorDetailView.as_view(), name='author-detail'),

    # URL para outras views, como pesquisa ou filtros, se necessário
]
