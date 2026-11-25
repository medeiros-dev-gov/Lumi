import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse
from django.contrib.messages import get_messages

from .models import Author, Book, BookInstance, Genre, Language

User = get_user_model()


class BookInstanceModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="usuario_teste",
            password="SenhaTeste123!"
        )

        self.author = Author.objects.create(
            first_name="Autor",
            last_name="Teste"
        )

        self.language = Language.objects.create(name="Português")

        self.book = Book.objects.create(
            title="Livro de Teste",
            author=self.author,
            summary="Descrição do livro de teste.",
            isbn="9781234567890",
            language=self.language,
        )

        self.instance = BookInstance.objects.create(
            book=self.book,
            imprint="Exemplar de teste",
            status="a",
        )

    def test_exemplar_comeca_disponivel(self):
        self.assertEqual(self.instance.status, "a")
        self.assertIsNone(self.instance.borrower)

    def test_emprestar_exemplar_disponivel(self):
        resultado = self.instance.borrow(self.user)

        self.instance.refresh_from_db()

        self.assertTrue(resultado)
        self.assertEqual(self.instance.status, "o")
        self.assertEqual(self.instance.borrower, self.user)
        self.assertIsNotNone(self.instance.due_back)

    def test_nao_emprestar_exemplar_indisponivel(self):
        self.instance.borrow(self.user)

        outro_usuario = User.objects.create_user(
            username="outro_usuario",
            password="SenhaTeste123!"
        )

        resultado = self.instance.borrow(outro_usuario)

        self.instance.refresh_from_db()

        self.assertFalse(resultado)
        self.assertEqual(self.instance.borrower, self.user)

    def test_devolver_exemplar(self):
        self.instance.borrow(self.user)

        resultado = self.instance.return_book()

        self.instance.refresh_from_db()

        self.assertTrue(resultado)
        self.assertEqual(self.instance.status, "a")
        self.assertIsNone(self.instance.borrower)
        self.assertIsNone(self.instance.due_back)

    def test_nao_devolver_exemplar_que_nao_esta_emprestado(self):
        resultado = self.instance.return_book()

        self.assertFalse(resultado)

    def test_renovar_emprestimo(self):
        self.instance.borrow(self.user)

        data_anterior = self.instance.due_back

        resultado = self.instance.renew(days=7)

        self.instance.refresh_from_db()

        self.assertTrue(resultado)
        self.assertEqual(
            self.instance.due_back,
            data_anterior + datetime.timedelta(days=7)
        )
        self.assertEqual(self.instance.renewal_count, 1)

    def test_bloquear_renovacao_apos_limite(self):
        self.instance.borrow(self.user)
        self.instance.renewal_count = 3
        self.instance.save(update_fields=["renewal_count"])

        resultado = self.instance.renew()

        self.assertFalse(resultado)

    def test_identificar_emprestimo_atrasado(self):
        self.instance.borrow(self.user)
        self.instance.due_back = timezone.localdate() - datetime.timedelta(days=1)
        self.instance.save(update_fields=["due_back"])

        self.instance.refresh_from_db()

        self.assertTrue(self.instance.is_overdue)
        self.assertFalse(self.instance.can_renew())



class BorrowBookViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="emprestimo_teste",
            password="SenhaTeste123!"
        )

        self.author = Author.objects.create(
            first_name="Autor",
            last_name="Empréstimo"
        )

        self.language = Language.objects.create(name="Português")

        self.book = Book.objects.create(
            title="Livro para Teste de Empréstimo",
            author=self.author,
            summary="Livro utilizado nos testes de empréstimo.",
            isbn="9780000000001",
            language=self.language,
        )

        self.instance = BookInstance.objects.create(
            book=self.book,
            imprint="Exemplar de teste",
            status="a",
        )

        self.url = reverse("borrow-book")

        self.client.login(
            username="emprestimo_teste",
            password="SenhaTeste123!"
        )

    def test_emprestar_livro_sem_informar_data(self):
        response = self.client.post(
            self.url,
            {"book": self.book.id}
        )

        self.instance.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("my-borrowed")
        )
        self.assertEqual(self.instance.status, "o")
        self.assertEqual(self.instance.borrower, self.user)
        self.assertEqual(
            self.instance.due_back,
            timezone.localdate() + datetime.timedelta(days=14)
        )

    def test_impedir_segundo_emprestimo_do_mesmo_livro(self):
        self.instance.borrow(self.user)

        response = self.client.post(
            self.url,
            {"book": self.book.id}
        )

        self.instance.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("my-borrowed")
        )
        self.assertEqual(self.instance.status, "o")
        self.assertEqual(self.instance.borrower, self.user)

        messages_list = [str(message) for message in get_messages(response.wsgi_request)]

        self.assertTrue(
            any("já possui um exemplar" in message for message in messages_list)
        )

    def test_impedir_emprestimo_com_data_no_passado(self):
        ontem = timezone.localdate() - datetime.timedelta(days=1)

        response = self.client.post(
            self.url,
            {
                "book": self.book.id,
                "due_back": ontem.isoformat(),
            }
        )

        self.instance.refresh_from_db()

        self.assertEqual(self.instance.status, "a")
        self.assertIsNone(self.instance.borrower)
        self.assertRedirects(
            response,
            reverse("my-borrowed")
        )

    def test_impedir_emprestimo_sem_exemplar_disponivel(self):
        self.instance.borrow(self.user)

        outro_usuario = User.objects.create_user(
            username="outro_teste",
            password="SenhaTeste123!"
        )

        self.client.logout()
        self.client.login(
            username="outro_teste",
            password="SenhaTeste123!"
        )

        response = self.client.post(
            self.url,
            {"book": self.book.id}
        )

        self.instance.refresh_from_db()

        self.assertEqual(self.instance.status, "o")
        self.assertEqual(self.instance.borrower, self.user)
        self.assertRedirects(
            response,
            reverse("my-borrowed")
        )

    def test_usuario_nao_autenticado_nao_pode_emprestar(self):
        self.client.logout()

        response = self.client.post(
            self.url,
            {"book": self.book.id}
        )

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={self.url}"
        )



class ReturnBookViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="devolucao_teste",
            password="SenhaTeste123!"
        )

        self.outro_usuario = User.objects.create_user(
            username="outro_usuario",
            password="SenhaTeste123!"
        )

        self.author = Author.objects.create(
            first_name="Autor",
            last_name="Devolução"
        )

        self.language = Language.objects.create(name="Português")

        self.book = Book.objects.create(
            title="Livro para Teste de Devolução",
            author=self.author,
            summary="Livro utilizado nos testes de devolução.",
            isbn="9780000000002",
            language=self.language,
        )

        self.instance = BookInstance.objects.create(
            book=self.book,
            imprint="Exemplar de devolução",
            status="o",
            borrower=self.user,
            due_back=timezone.localdate() + datetime.timedelta(days=14),
            renewal_count=2,
        )

        self.url = reverse(
            "return-book",
            kwargs={"pk": self.instance.pk}
        )

        self.client.login(
            username="devolucao_teste",
            password="SenhaTeste123!"
        )

    def test_devolver_proprio_livro(self):
        response = self.client.post(self.url)

        self.instance.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("my-borrowed")
        )
        self.assertEqual(self.instance.status, "a")
        self.assertIsNone(self.instance.borrower)
        self.assertIsNone(self.instance.due_back)
        self.assertEqual(self.instance.renewal_count, 0)

    def test_impedir_devolver_livro_de_outro_usuario(self):
        self.client.logout()
        self.client.login(
            username="outro_usuario",
            password="SenhaTeste123!"
        )

        response = self.client.post(self.url)

        self.instance.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.instance.status, "o")
        self.assertEqual(self.instance.borrower, self.user)

    def test_impedir_devolver_livro_ja_disponivel(self):
        self.instance.return_book()

        response = self.client.post(self.url)

        self.instance.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.instance.status, "a")
        self.assertIsNone(self.instance.borrower)

    def test_usuario_nao_autenticado_nao_pode_devolver(self):
        self.client.logout()

        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={self.url}"
        )

class RenewBookViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="renovacao_teste",
            password="SenhaTeste123!"
        )

        self.outro_usuario = User.objects.create_user(
            username="outro_usuario",
            password="SenhaTeste123!"
        )

        self.author = Author.objects.create(
            first_name="Autor",
            last_name="Renovacao"
        )

        self.language = Language.objects.create(name="Portugues")

        self.book = Book.objects.create(
            title="Livro para Teste de Renovacao",
            author=self.author,
            summary="Livro utilizado nos testes de renovacao.",
            isbn="9780000000003",
            language=self.language,
        )

        self.instance = BookInstance.objects.create(
            book=self.book,
            imprint="Exemplar de renovacao",
            status="o",
            borrower=self.user,
            due_back=timezone.localdate() + datetime.timedelta(days=14),
            renewal_count=0,
        )

        self.url = reverse(
            "renew-book",
            kwargs={"pk": self.instance.pk}
        )

        self.client.login(
            username="renovacao_teste",
            password="SenhaTeste123!"
        )

    def test_renovar_proprio_livro(self):
        vencimento_original = self.instance.due_back

        response = self.client.post(self.url)

        self.instance.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("my-borrowed")
        )
        self.assertEqual(
            self.instance.due_back,
            vencimento_original + datetime.timedelta(days=7)
        )
        self.assertEqual(self.instance.renewal_count, 1)

    def test_impedir_renovacao_acima_do_limite(self):
        self.instance.renewal_count = 3
        self.instance.save(update_fields=["renewal_count"])

        vencimento_original = self.instance.due_back

        response = self.client.post(self.url)

        self.instance.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("my-borrowed")
        )
        self.assertEqual(self.instance.due_back, vencimento_original)
        self.assertEqual(self.instance.renewal_count, 3)

    def test_impedir_outro_usuario_de_renovar(self):
        vencimento_original = self.instance.due_back

        self.client.logout()
        self.client.login(
            username="outro_usuario",
            password="SenhaTeste123!"
        )

        response = self.client.post(self.url)

        self.instance.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("my-borrowed")
        )
        self.assertEqual(self.instance.borrower, self.user)
        self.assertEqual(self.instance.due_back, vencimento_original)
        self.assertEqual(self.instance.renewal_count, 0)

    def test_impedir_renovar_livro_devolvido(self):
        self.instance.status = "a"
        self.instance.borrower = None
        self.instance.save(update_fields=["status", "borrower"])

        response = self.client.post(self.url)

        self.instance.refresh_from_db()

        self.assertRedirects(
            response,
            reverse("my-borrowed")
        )
        self.assertEqual(self.instance.status, "a")
        self.assertIsNone(self.instance.borrower)
        self.assertEqual(self.instance.renewal_count, 0)

    def test_usuario_nao_autenticado_nao_pode_renovar(self):
        self.client.logout()

        response = self.client.post(self.url)

        self.assertRedirects(
            response,
            f"{reverse('login')}?next={self.url}"
        )

    def test_impedir_renovacao_por_requisicao_get(self):
        response = self.client.get(self.url)

        self.instance.refresh_from_db()

        self.assertEqual(response.status_code, 405)
        self.assertEqual(self.instance.renewal_count, 0)
