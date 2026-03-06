from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import Cliente

class ClienteCambioPasswordForm(forms.Form):
    password_actual = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "mt-1 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-slate-800 px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
        }),
        label="Contraseña actual"
    )

    nueva_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "mt-1 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-slate-800 px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
        }),
        label="Nueva contraseña"
    )

    confirmar_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "mt-1 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-slate-800 px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
        }),
        label="Confirmar nueva contraseña"
    )

    def clean(self):
        data = super().clean()
        p1 = data.get("nueva_password")
        p2 = data.get("confirmar_password")

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden.")

        return data
    
class ClienteDatosForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ["telefono", "celular", "direccion", "correo"]

        widgets = {
            "telefono": forms.TextInput(attrs={
                "class": "mt-1 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-slate-800 px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
            }),
            "celular": forms.TextInput(attrs={
                "class": "mt-1 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-slate-800 px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
            }),
            "direccion": forms.Textarea(attrs={
                "rows": 3,
                "class": "mt-1 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-slate-800 px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
            }),
            "correo": forms.EmailInput(attrs={
                "class": "mt-1 w-full rounded-xl border border-gray-200 dark:border-white/10 bg-gray-50 dark:bg-slate-800 px-4 py-2 text-sm focus:ring-2 focus:ring-indigo-500 outline-none"
            }),
        }
