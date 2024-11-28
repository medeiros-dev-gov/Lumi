from django import forms
import datetime

class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(
        help_text="Insira uma data de renovação entre 1 e 4 semanas a partir de hoje.",
        widget=forms.SelectDateWidget(),
    )

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']
        if data < datetime.date.today():
            raise forms.ValidationError("A data de renovação não pode ser no passado!")
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise forms.ValidationError("A data de renovação não pode ser mais de 4 semanas a partir de hoje.")
        return data
