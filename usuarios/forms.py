from django import forms
from django.contrib.auth.models import User, Group
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordChangeForm
import re

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
    
class CustomPasswordChangeForm(PasswordChangeForm):

    error_messages = {
        **PasswordChangeForm.error_messages,
        "password_incorrect": "La contraseña actual es incorrecta. Inténtalo de nuevo.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["old_password"].label = "Contraseña actual"
        self.fields["new_password1"].label = "Nueva contraseña"
        self.fields["new_password2"].label = "Confirmar nueva contraseña"

        self.fields["old_password"].widget.attrs.update({"placeholder": "Tu contraseña actual"})
        self.fields["new_password1"].widget.attrs.update({"placeholder": "Crea una nueva contraseña"})
        self.fields["new_password2"].widget.attrs.update({"placeholder": "Repite la nueva contraseña"})

    def clean_new_password1(self):
        pwd = self.cleaned_data.get("new_password1", "")

        errors = []
        if len(pwd) < 8:
            errors.append("Debe tener al menos 8 caracteres.")
        if not re.search(r"[A-Z]", pwd):
            errors.append("Debe contener al menos una letra mayúscula.")
        if not re.search(r"[a-z]", pwd):
            errors.append("Debe contener al menos una letra minúscula.")
        if not re.search(r"\d", pwd):
            errors.append("Debe contener al menos un número.")
        if not re.search(r"[^A-Za-z0-9]", pwd):
            errors.append("Debe contener al menos un símbolo (ej: !@#$%).")

        if errors:
            raise forms.ValidationError(errors)

        return pwd

    def clean_new_password2(self):
        p1 = self.cleaned_data.get("new_password1")
        p2 = self.cleaned_data.get("new_password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return p2


