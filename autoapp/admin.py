from django import forms
from django.contrib import admin
from .models import Categoria, Producto
from django.core.exceptions import ValidationError
from simple_history.admin import SimpleHistoryAdmin  
class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = '__all__'

    def clean_precio(self):
        precio = self.cleaned_data['precio']
        if precio != precio.quantize(1):
            raise ValidationError("El precio no puede tener decimales diferentes de cero.")
        if precio < 0:
            raise ValidationError("El precio no puede ser negativo.")
        return precio

    def clean_stock(self):
        stock = self.cleaned_data.get('stock')
        if stock is not None:
            if stock < 0:
                raise forms.ValidationError("El stock no puede ser negativo.")
            if not isinstance(stock, int):
                raise forms.ValidationError("El stock debe ser un número entero.")
        return stock

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(SimpleHistoryAdmin):  
    form = ProductoForm
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'destacado', 'oferta')
    list_filter = ('categoria', 'destacado', 'oferta')
    search_fields = ('nombre', 'marca', 'codigo_producto')
    ordering = ('nombre',)
