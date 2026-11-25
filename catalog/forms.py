
import datetime
from django import forms
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(
        label="Data de devolução",
        help_text="Escolha uma data entre hoje e quatro semanas a partir de hoje.",
        widget=forms.SelectDateWidget(),
    )

    def clean_renewal_date(self):
        value = self.cleaned_data["renewal_date"]
        today = timezone.localdate()

        if value < today:
            raise forms.ValidationError(
                "A data não pode estar no passado."
            )

        if value > today + datetime.timedelta(weeks=4):
            raise forms.ValidationError(
                "A data não pode ultrapassar quatro semanas."
            )

        return value


User = get_user_model()


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        label="E-mail"
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

        labels = {
            "username": "Nome de usuário",
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "Este e-mail já está cadastrado."
            )

        return email
