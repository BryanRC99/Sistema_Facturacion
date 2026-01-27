from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm

class CrearUsuarioForm(UserCreationForm):
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "grupo", "password1", "password2"]


class EditarUsuarioForm(forms.ModelForm):
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False
    )

    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "grupo"]

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()

        # Excluir el mismo usuario (self.instance) del chequeo
        qs = User.objects.filter(username__iexact=username)
        if self.instance and self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError("Ese usuario ya existe.")
        return username


