import datetime
from pyexpat.errors import messages
from django.db import models
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.db.models import UniqueConstraint
from django.db.models.functions import Lower
from django.conf import settings  # Required to assign User as a borrower
import uuid
from datetime import date, timedelta, timezone
from django.contrib.auth.models import User
from django.utils import timezone



class Genre(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        help_text="Enter a book genre (e.g. Science Fiction, French Poetry etc.)"
    )

    def __str__(self):
        return self.name


    class Meta:
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
    """Model representing a specific copy of a book that can be borrowed from the library."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          help_text="Unique ID for this particular book across the whole library")
    book = models.ForeignKey(Book, on_delete=models.RESTRICT, null=True)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=1,
        choices=[
            ('o', 'On loan'),
            ('a', 'Available'),
            ('r', 'Reserved'),
        ],
        blank=True,
        default='a',
    )

    LOAN_STATUS = (
        ('d', 'Maintenance'),
        ('o', 'On loan'),
        ('a', 'Available'),
        ('r', 'Reserved'),
    )

    status = models.CharField(max_length=1, choices=LOAN_STATUS, blank=True, default='d', help_text='Book availability')

    class Meta:
        ordering = ['due_back']
        permissions = (("can_mark_returned", "Set book as returned"),)

    def renew(self):
        """Renews the book loan, extending the due date by 7 days."""
        if self.status == 'o':
            self.due_back = timezone.now().date() + timedelta(days=7)
            self.save()

    @property
    def is_overdue(self):
        """Checks if the book is overdue based on its due date."""
        return bool(self.due_back and date.today() > self.due_back)

    def get_absolute_url(self):
        return reverse('bookinstance-detail', args=[str(self.id)])

    def __str__(self):
        return f'{self.id} ({self.book.title})'

    def borrow(self, user):
        """Loans the book to a user."""
        if self.status == 'a':  # Only loan if available
            self.status = 'o'  # Marks as loaned
            self.borrower = user
            self.due_back = timezone.now().date() + timedelta(weeks=2)  # Sets due date
            self.save()

    def return_book(self):
        """Returns the book, making it available again."""
        if self.status == 'o':  # Only return if loaned
            self.status = 'a'  # Marks as available
            self.borrower = None
            self.due_back = None
            self.save()
    
    renewal_count = models.PositiveIntegerField(default=0)
    
    def can_renew(self):
        return self.renewal_count < 3 
    
    def can_be_renewed(self):
        if not self.due_back:  # Check if 'due_back' is None
            return False  # If it's None, we can't renew it
    
    # If due_back is not None, continue with your logic
        return self.due_back > timezone.now().date()  # Use timezone.now().date() instead of datetime.now()

def renew_book(request, pk):
    """Renews the loan of a specific book."""
    book_instance = get_object_or_404(BookInstance, pk=pk)
    
    # Verifica se o usuário tem permissão (opcional, mas recomendado)
    if book_instance.borrower != request.user:
        messages.error(request, "Você não tem permissão para renovar este livro.")
        return redirect('my-borrowed')
    
    # Renova o empréstimo
    book_instance.renew()
    messages.success(request, "Empréstimo renovado com sucesso!")
    
    # Redireciona para a página de livros emprestados
    return redirect('my-borrowed')


class BorrowedBook(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="borrowed_books")
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"