from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils.dateparse import parse_date
from .forms import UserRegisterForm

# Create your views here.

from .models import Book, Author, BookInstance, BorrowedBook, Genre, Language

def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    # Available copies of books
    num_instances_available = BookInstance.objects.filter(
        status__exact='a').count()
    num_authors = Author.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    num_visits += 1
    request.session['num_visits'] = num_visits

    # Render the HTML template index.html with the data in the context variable.
    return render(
        request,
        'index.html',
        context={'num_books': num_books, 'num_instances': num_instances,
                 'num_instances_available': num_instances_available, 'num_authors': num_authors,
                 'num_visits': num_visits},
    )

from django.views import generic



from django.db.models import Count, Q

class BookListView(generic.ListView):
    """Lista livros com a quantidade de exemplares disponíveis."""
    model = Book
    paginate_by = 12

    def get_queryset(self):
        return Book.objects.annotate(
            available_copies=Count(
                'bookinstance',
                filter=Q(bookinstance__status='a')
            )
        )
class BookDetailView(generic.DetailView):
    """Exibe os detalhes do livro e sua disponibilidade."""
    model = Book

    def get_queryset(self):
        return Book.objects.annotate(
            available_copies=Count(
                'bookinstance',
                filter=Q(bookinstance__status='a')
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['today'] = timezone.localdate()

        context['user_has_borrowed'] = (
            self.request.user.is_authenticated
            and BookInstance.objects.filter(
                book=self.object,
                borrower=self.request.user,
                status='o'
            ).exists()
        )

        return context
class AuthorListView(generic.ListView):
    """Generic class-based list view for a list of authors."""
    model = Author
    paginate_by = 12

class AuthorDetailView(generic.DetailView):
    """Generic class-based detail view for an author."""
    model = Author


class GenreDetailView(generic.DetailView):
    """Generic class-based detail view for a genre."""
    model = Genre

class GenreListView(generic.ListView):
    """Generic class-based list view for a list of genres."""
    model = Genre
    paginate_by = 12

class LanguageDetailView(generic.DetailView):
    """Generic class-based detail view for a genre."""
    model = Language

class LanguageListView(generic.ListView):
    """Generic class-based list view for a list of genres."""
    model = Language
    paginate_by = 12

class BookInstanceListView(generic.ListView):
    """Generic class-based view for a list of books."""
    model = BookInstance
    paginate_by = 12

class BookInstanceDetailView(generic.DetailView):
    """Generic class-based detail view for a book."""
    model = BookInstance

from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name = 'catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 12

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact='o')
            .order_by('due_back')
        )

# Added as part of challenge!
from django.contrib.auth.mixins import PermissionRequiredMixin


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 12

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')

from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import datetime
from django.contrib.auth.decorators import login_required, permission_required
from .forms import RenewBookForm
from django.contrib import messages

@login_required
@permission_required('catalog.can_mark_returned', raise_exception=True)
def renew_book_librarian(request, pk):
    """View function for renewing a specific BookInstance by librarian."""
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request, then process the form data
    if request.method == 'POST':
        form = RenewBookForm(request.POST)
        
        if form.is_valid():
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # Add success message
            messages.success(request, f"Book renewed successfully. New due date: {book_instance.due_back}")
            
            return HttpResponseRedirect(reverse('all-borrowed'))

    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)


from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Author


class AuthorCreate(PermissionRequiredMixin, CreateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']
    initial = {'date_of_death': '11/11/2023'}
    permission_required = 'catalog.add_author'

class AuthorUpdate(PermissionRequiredMixin, UpdateView):
    model = Author
    # Not recommended (potential security issue if more fields added)
    fields = '__all__'
    permission_required = 'catalog.change_author'

class AuthorDelete(PermissionRequiredMixin, DeleteView):
    model = Author
    success_url = reverse_lazy('authors')
    permission_required = 'catalog.delete_author'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("author-delete", kwargs={"pk": self.object.pk})
            )

# Classes created for the forms challenge


class BookCreate(PermissionRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.add_book'


class BookUpdate(PermissionRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'summary', 'isbn', 'genre', 'language']
    permission_required = 'catalog.change_book'


class BookDelete(PermissionRequiredMixin, DeleteView):
    model = Book
    success_url = reverse_lazy('books')
    permission_required = 'catalog.delete_book'

    def form_valid(self, form):
        try:
            self.object.delete()
            return HttpResponseRedirect(self.success_url)
        except Exception as e:
            return HttpResponseRedirect(
                reverse("book-delete", kwargs={"pk": self.object.pk})
            )


class GenreCreate(PermissionRequiredMixin, CreateView):
    model = Genre
    fields = ['name', ]
    permission_required = 'catalog.add_genre'


class GenreUpdate(PermissionRequiredMixin, UpdateView):
    model = Genre
    fields = ['name', ]
    permission_required = 'catalog.change_genre'


class GenreDelete(PermissionRequiredMixin, DeleteView):
    model = Genre
    success_url = reverse_lazy('genres')
    permission_required = 'catalog.delete_genre'


class LanguageCreate(PermissionRequiredMixin, CreateView):
    model = Language
    fields = ['name', ]
    permission_required = 'catalog.add_language'


class LanguageUpdate(PermissionRequiredMixin, UpdateView):
    model = Language
    fields = ['name', ]
    permission_required = 'catalog.change_language'


class LanguageDelete(PermissionRequiredMixin, DeleteView):
    model = Language
    success_url = reverse_lazy('languages')
    permission_required = 'catalog.delete_language'


class BookInstanceCreate(PermissionRequiredMixin, CreateView):
    model = BookInstance
    fields = ['book', 'imprint', 'due_back', 'borrower', 'status']
    permission_required = 'catalog.add_bookinstance'


class BookInstanceUpdate(PermissionRequiredMixin, UpdateView):
    model = BookInstance
    # fields = "__all__"
    fields = ['imprint', 'due_back', 'borrower', 'status']
    permission_required = 'catalog.change_bookinstance'


class BookInstanceDelete(PermissionRequiredMixin, DeleteView):
    model = BookInstance
    success_url = reverse_lazy('bookinstances')
    permission_required = 'catalog.delete_bookinstance'



@login_required
@require_POST
def renew_book(request, pk):
    instance = get_object_or_404(BookInstance, pk=pk)
    if instance.borrower_id != request.user.id:
        messages.error(request, "Você não tem permissão para renovar este livro.")
    elif not instance.renew():
        messages.error(request, "Este empréstimo não pode ser renovado (limite, status ou prazo).")
    else:
        messages.success(request, "Empréstimo renovado por mais 7 dias.")
    return redirect('my-borrowed')


@login_required
@require_POST
def borrow_book(request):
    book_id = request.POST.get('book')
    due_back_raw = request.POST.get('due_back', '').strip()
    due_back = parse_date(due_back_raw) if due_back_raw else None

    if due_back_raw and due_back is None:
        messages.error(request, "Informe uma data de devolução válida.")
        return redirect('books')

    book = get_object_or_404(Book, pk=book_id)

    with transaction.atomic():

        # Verifica se o usuário já possui este título emprestado
        already_borrowed = BookInstance.objects.filter(
            book=book,
            borrower=request.user,
            status='o'
        ).exists()

        if already_borrowed:
            messages.error(
                request,
                f"Você já possui um exemplar de '{book.title}' emprestado."
            )

        else:
            instance = BookInstance.objects.select_for_update().filter(
                book=book,
                status='a'
            ).first()

            if instance is None:
                messages.error(
                    request,
                    "Este livro não está disponível no momento."
                )

            elif due_back and due_back < timezone.localdate():
                messages.error(
                    request,
                    "A data de devolução não pode estar no passado."
                )

            elif instance.borrow(request.user, due_back=due_back):
                messages.success(
                    request,
                    f"Você emprestou o livro '{book.title}'!"
                )

            else:
                messages.error(
                    request,
                    "Não foi possível concluir o empréstimo."
                )

    return redirect('my-borrowed')


@login_required
def my_borrowed_books(request):
    borrowed_books = BookInstance.objects.filter(
        borrower=request.user,
        status='o'
    ).select_related('book').order_by('due_back')

    return render(
        request,
        'catalog/my_borrowed_books.html',
        {'borrowed_books': borrowed_books}
    )
    return render(request, 'catalog/my_borrowed_books.html', {'borrowed_books': borrowed_books})

def listar_livros(request):
    livros = Book.objects.all()  # Certifique-se de estar buscando todos os livros.
    return render(request, 'nome_do_template.html', {'livros': livros})



@login_required
@require_POST
def return_book(request, pk):
    with transaction.atomic():
        instance = get_object_or_404(
            BookInstance.objects.select_for_update(),
            pk=pk,
            borrower=request.user,
            status='o'
        )

        instance.return_book()

    messages.success(
        request,
        f"Você devolveu o livro '{instance.book.title}' com sucesso!"
    )

    return redirect('my-borrowed')


def register(request):
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            messages.success(
                request,
                "Sua conta foi criada com sucesso! Faça login para acessar a biblioteca."
            )

            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(
        request,
        'registration/register.html',
        {'form': form}
    )
