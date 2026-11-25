import uuid
from datetime import timedelta
from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils import timezone
from django.conf import settings


class Genre(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)"
    )

    def __str__(self):
        return self.name


    class Meta:
        ordering = ['name']
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='genre_name_case_insensitive_unique',
                violation_error_message="Genre already exists (case insensitive match)"
            ),
        ]

class Language(models.Model):
    """Model representing a Language (e.g. English, French, Japanese, etc.)"""
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Enter the book's natural language (e.g. English, French, Japanese etc.)"
    )

    def get_absolute_url(self):
        return reverse('language-detail', args=[str(self.id)])

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
        constraints = [
            UniqueConstraint(
                Lower('name'),
                name='language_name_case_insensitive_unique',
                violation_error_message="Language already exists (case insensitive match)"
            ),
        ]

class Author(models.Model):
    """Model representing an author."""
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField('died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def get_absolute_url(self):
        return reverse('author-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.last_name}, {self.first_name}'

class Book(models.Model):
    """Model representing a book (but not a specific copy of a book)."""
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.RESTRICT, null=True)
    summary = models.TextField(max_length=1000, help_text="Enter a brief description of the book")
    isbn = models.CharField('ISBN', max_length=13, unique=True,
                            help_text='13 Character ISBN number')
    genre = models.ManyToManyField(Genre, help_text="Select a genre for this book")
    language = models.ForeignKey('Language', on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='book_images/', null=True, blank=True)  # Campo de imagem

    def __str__(self):
        return self.title
    
    class Meta:
        ordering = ['title', 'author']

    def display_genre(self):
        return ', '.join([genre.name for genre in self.genre.all()[:3]])

    display_genre.short_description = 'Genre'

    def get_absolute_url(self):
        return reverse('book-detail', args=[str(self.id)])

    def __str__(self):
        return self.title

class BookInstance(models.Model):
    """Exemplar individual de um livro disponível para empréstimo."""
    LOAN_STATUS = (
        ('d', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        help_text="Identificador único deste exemplar",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.RESTRICT,
        null=True,
        blank=True,
    )
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    status = models.CharField(
        max_length=1,
        choices=LOAN_STATUS,
        default='a',
        help_text='Disponibilidade do exemplar',
    )
    renewal_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def renew(self, days=7, max_renewals=3):
        """Renova empréstimo ativo, respeitando limite e vencimento."""
        if self.status != 'o' or not self.borrower:
            return False
        if self.renewal_count >= max_renewals:
            return False
        today = timezone.localdate()
        if not self.due_back or self.due_back < today:
            return False
        self.due_back = max(self.due_back, today) + timedelta(days=days)
        self.renewal_count += 1
        self.save(update_fields=['due_back', 'renewal_count'])
        return True

    @property
    def is_overdue(self):
        return bool(self.due_back and timezone.localdate() > self.due_back)

    def get_absolute_url(self):
        return reverse('bookinstance-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.id} ({self.book.title})'

    def borrow(self, user, due_back=None):
        """Empresta exemplar disponível; retorna False se indisponível."""
        if self.status != 'a':
            return False
        self.status = 'o'
        self.borrower = user
        self.due_back = due_back or (timezone.localdate() + timedelta(weeks=2))
        self.renewal_count = 0
        self.save(update_fields=['status', 'borrower', 'due_back', 'renewal_count'])
        return True

    def return_book(self):
        """Registra devolução de exemplar emprestado."""
        if self.status != 'o':
            return False
        self.status = 'a'
        self.borrower = None
        self.due_back = None
        self.renewal_count = 0
        self.save(update_fields=['status', 'borrower', 'due_back', 'renewal_count'])
        return True

    def can_renew(self):
        return bool(
            self.status == 'o'
            and self.borrower_id
            and self.due_back
            and self.due_back >= timezone.localdate()
            and self.renewal_count < 3
        )

    def can_be_renewed(self):
        return self.can_renew()


class BorrowedBook(models.Model):
    user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    related_name="borrowed_books"
)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"