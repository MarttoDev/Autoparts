from django import forms
from .models import Producto
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = ['nombre', 'descripcion', 'precio', 'imagen', 'stock']

class RegistroUsuarioForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        help_texts = {
            'username': None,
            'password1': None,
            'password2': None,
        }

