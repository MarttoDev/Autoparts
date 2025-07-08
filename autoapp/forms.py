from django import forms
from .models import Producto
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PerfilUsuario


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'imagen', 'stock']

class RegistroUsuarioForm(UserCreationForm):
    es_mayorista = forms.BooleanField(
        required=False,
        label='¿Eres mayorista?',
        widget=forms.CheckboxInput()
    )

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'es_mayorista']
        help_texts = {
            'username': None,
            'password1': None,
            'password2': None,
        }

    def save(self, commit=True):
        user = super().save(commit)
        es_mayorista = self.cleaned_data.get('es_mayorista', False)

        perfil, created = PerfilUsuario.objects.get_or_create(user=user)
        perfil.es_mayorista = es_mayorista
        perfil.save()

        return user
    
class DatosPersonalesForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    email = forms.EmailField()
    telefono = forms.CharField(max_length=20)
    direccion = forms.CharField(widget=forms.Textarea)

