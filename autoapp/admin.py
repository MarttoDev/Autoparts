from django.contrib import admin
from .models import Categoria, Producto

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'destacado', 'oferta')
    list_filter = ('categoria', 'destacado', 'oferta')
    search_fields = ('nombre', 'marca', 'codigo_producto')
    ordering = ('nombre',)
