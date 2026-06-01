from django.db import models
from django.contrib.auth.models import User


class Producto(models.Model):
    nombre = models.CharField(max_length=120)
    categoria = models.CharField(max_length=80)
    descripcion = models.TextField()
    precio = models.PositiveIntegerField()
    imagen = models.CharField(max_length=200)
    stock = models.PositiveIntegerField(default=0)
    destacado = models.BooleanField(default=False)
    disponible = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    puntos = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'Perfil de {self.usuario.username}'


class Pedido(models.Model):
    ESTADO_COMPLETADO = 'completado'

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    total = models.PositiveIntegerField()
    puntos_ganados = models.PositiveIntegerField(default=0)
    estado = models.CharField(max_length=20, default=ESTADO_COMPLETADO)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return f'Pedido #{self.id} - {self.usuario.username}'


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.producto.nombre} x{self.cantidad}'


class Recompensa(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    costo_puntos = models.PositiveIntegerField()
    activo = models.BooleanField(default=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['costo_puntos', 'producto__nombre']

    def __str__(self):
        return f'{self.producto.nombre} - {self.costo_puntos} puntos'


class Canje(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    recompensa = models.ForeignKey(Recompensa, on_delete=models.PROTECT)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    costo_puntos = models.PositiveIntegerField()
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return f'{self.usuario.username} canjeo {self.producto.nombre}'
