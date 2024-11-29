from django.contrib import admin
from .models import Author, Genre, Book, BookInstance, Language
from django.utils.html import mark_safe
# Registrando os modelos para o admin
admin.site.register(Genre)
admin.site.register(Language)


class BooksInline(admin.TabularInline):
    """Define o formato de inserção de livros (usado no AuthorAdmin)"""
    model = Book


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    """Administração para o modelo Author.
    Define:
     - campos para exibição na visualização de lista (list_display)
     - ordem dos campos na visualização de detalhes (fields)
     - adiciona livros como inserção inline na visualização de autor (inlines)
    """
    list_display = ('last_name', 'first_name', 'date_of_birth', 'date_of_death')
    fields = ['first_name', 'last_name', ('date_of_birth', 'date_of_death')]
    inlines = [BooksInline]


class BooksInstanceInline(admin.TabularInline):
    """Define o formato de inserção de instâncias de livros (usado no BookAdmin)"""
    model = BookInstance


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'image_tag')  # Use o método 'image_tag' em vez do campo direto
    search_fields = ('title', 'author')

    def image_tag(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="50" height="50" />')
        return 'Sem imagem'

    image_tag.short_description = 'Imagem'

admin.site.register(Book, BookAdmin)


@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    """Administração para o modelo BookInstance.
    Define:
     - campos para exibição na visualização de lista (list_display)
     - filtros exibidos na barra lateral (list_filter)
     - agrupamento de campos em seções (fieldsets)
    """
    list_display = ('book', 'status', 'borrower', 'due_back', 'id')
    list_filter = ('status', 'due_back', 'borrower')

    fieldsets = (
        (None, {
            'fields': ('book', 'imprint', 'id')
        }),
        ('Disponibilidade', {
            'fields': ('status', 'due_back', 'borrower')
        }),
    )
