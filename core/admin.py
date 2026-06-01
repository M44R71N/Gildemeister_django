from django.contrib import admin

from .models import Canje, DetallePedido, Pedido, Perfil, Producto, Recompensa


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'precio', 'stock', 'destacado', 'disponible')
    list_filter = ('categoria', 'destacado', 'disponible')
    search_fields = ('nombre', 'categoria', 'descripcion')
    list_editable = ('precio', 'stock', 'destacado', 'disponible')


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'puntos')
    search_fields = ('usuario__username',)


class DetallePedidoInline(admin.TabularInline):
    model = DetallePedido
    extra = 0
    readonly_fields = ('producto', 'cantidad', 'precio_unitario', 'subtotal')
    can_delete = False


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'total', 'puntos_ganados', 'estado', 'creado')
    list_filter = ('estado', 'creado')
    search_fields = ('usuario__username',)
    readonly_fields = ('usuario', 'total', 'puntos_ganados', 'estado', 'creado')
    inlines = (DetallePedidoInline,)


@admin.register(Recompensa)
class RecompensaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'costo_puntos', 'activo')
    list_filter = ('activo',)
    search_fields = ('producto__nombre',)
    list_editable = ('costo_puntos', 'activo')


@admin.register(Canje)
class CanjeAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'producto', 'costo_puntos', 'creado')
    list_filter = ('creado',)
    search_fields = ('usuario__username', 'producto__nombre')
    readonly_fields = ('usuario', 'recompensa', 'producto', 'costo_puntos', 'creado')
