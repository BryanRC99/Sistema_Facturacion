from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User, Group

class CrearUsuarioForm(UserCreationForm):
    grupo = forms.ModelChoiceField(
        queryset=Group.objects.all(),
        required=False,
        label="Rol / Grupo"
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'grupo']

    # 🟢 CONTRASEÑA OPCIONAL AL EDITAR
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Si es edición (tiene instancia con ID), la contraseña no es obligatoria
        if self.instance and self.instance.pk:
            self.fields['password1'].required = False
            self.fields['password2'].required = False

    # 🟢 GUARDAR CONTRASEÑA SOLO SI SE INGRESA UNA NUEVA
    def save(self, commit=True):
        user = super().save(commit=False)

        password1 = self.cleaned_data.get("password1")

        # Si el usuario escribió nueva contraseña → la actualizamos
        if password1:
            user.set_password(password1)

        if commit:
            user.save()

            # Guardar grupo si seleccionó uno
            grupo = self.cleaned_data.get("grupo")
            if grupo:
                user.groups.set([grupo])

        return user


