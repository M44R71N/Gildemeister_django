from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import redirect, render

from .models import Canje, DetallePedido, Pedido, Perfil, Producto, Recompensa


def login_view(request):
    if request.user.is_authenticated:
        return redirect('menu')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('menu')

        return render(request, 'core/login.html', {
            'error': 'Usuario o contraseña incorrectos.',
            'login_error': True,
            'error_message': 'Revisa tus datos e intenta nuevamente.',
        })

    return render(request, 'core/login.html')


def logout_view(request):
    if request.method == 'POST':
        logout(request)

    return redirect('login')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('menu')

    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        apellidos = request.POST.get('apellidos', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if User.objects.filter(username=username).exists():
            return render(request, 'core/register.html', {
                'error': 'Ese nombre de usuario ya existe.',
            })

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=nombre,
            last_name=apellidos,
        )
        Perfil.objects.create(usuario=user)

        return render(request, 'core/register.html', {
            'registro_exitoso': True,
        })

    return render(request, 'core/register.html')


@login_required
def menu_view(request):
    productos_destacados = Producto.objects.filter(
        disponible=True,
        destacado=True,
        stock__gt=0,
    )[:2]
    return render(request, 'core/menu.html', {
        'productos_destacados': productos_destacados,
    })


@login_required
def productos_view(request):
    productos = Producto.objects.filter(disponible=True)
    return render(request, 'core/productos.html', {'productos': productos})


@login_required
def agregar_carrito_view(request, producto_id):
    producto = Producto.objects.filter(
        id=producto_id,
        disponible=True,
        stock__gt=0,
    ).first()

    if request.method == 'POST' and producto:
        carrito = request.session.get('carrito', {})
        producto_key = str(producto_id)
        cantidad_actual = carrito.get(producto_key, 0)

        if cantidad_actual < producto.stock:
            carrito[producto_key] = cantidad_actual + 1

        request.session['carrito'] = carrito

    return redirect('carrito')


@login_required
def disminuir_carrito_view(request, producto_id):
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        producto_key = str(producto_id)

        if producto_key in carrito:
            carrito[producto_key] -= 1

            if carrito[producto_key] <= 0:
                del carrito[producto_key]

            request.session['carrito'] = carrito

    return redirect('carrito')


@login_required
def eliminar_carrito_view(request, producto_id):
    if request.method == 'POST':
        carrito = request.session.get('carrito', {})
        producto_key = str(producto_id)

        if producto_key in carrito:
            del carrito[producto_key]
            request.session['carrito'] = carrito

    return redirect('carrito')


def obtener_items_carrito(carrito):
    items = []
    total = 0

    for producto_id, cantidad in carrito.items():
        try:
            producto = Producto.objects.get(id=producto_id, disponible=True)
        except (Producto.DoesNotExist, ValueError):
            continue

        cantidad = min(cantidad, producto.stock)
        if cantidad <= 0:
            continue

        subtotal = producto.precio * cantidad
        total += subtotal
        items.append({
            'id': producto_id,
            'producto': producto,
            'cantidad': cantidad,
            'subtotal': subtotal,
        })

    return items, total


@login_required
def carrito_view(request):
    carrito = request.session.get('carrito', {})
    items, total = obtener_items_carrito(carrito)

    return render(request, 'core/carrito.html', {
        'items': items,
        'total': total,
    })


@login_required
def finalizar_compra_view(request):
    if request.method != 'POST':
        return redirect('carrito')

    carrito = request.session.get('carrito', {})
    items, total = obtener_items_carrito(carrito)

    if not items:
        messages.error(request, 'Tu carrito esta vacio.')
        return redirect('carrito')

    with transaction.atomic():
        puntos_ganados = max(total // 1000, 1)
        pedido = Pedido.objects.create(
            usuario=request.user,
            total=total,
            puntos_ganados=puntos_ganados,
        )

        for item in items:
            producto = Producto.objects.select_for_update().get(id=item['producto'].id)
            cantidad = min(item['cantidad'], producto.stock)

            if cantidad <= 0:
                continue

            subtotal = producto.precio * cantidad
            DetallePedido.objects.create(
                pedido=pedido,
                producto=producto,
                cantidad=cantidad,
                precio_unitario=producto.precio,
                subtotal=subtotal,
            )
            producto.stock -= cantidad
            producto.save(update_fields=['stock'])

        perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
        perfil.puntos += puntos_ganados
        perfil.save(update_fields=['puntos'])

    request.session['carrito'] = {}
    messages.success(
        request,
        f'Compra completada. Ganaste {puntos_ganados} puntos.',
    )
    return redirect('perfil')


@login_required
def perfil_view(request):
    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
    pedidos = Pedido.objects.filter(usuario=request.user).prefetch_related('detalles__producto')
    canjes = Canje.objects.filter(usuario=request.user).select_related('producto', 'recompensa')

    return render(request, 'core/perfil.html', {
        'perfil': perfil,
        'pedidos': pedidos,
        'canjes': canjes,
    })


@login_required
def canjeo_view(request):
    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
    recompensas = Recompensa.objects.filter(
        activo=True,
        producto__disponible=True,
    ).select_related('producto')

    return render(request, 'core/canjeo.html', {
        'perfil': perfil,
        'recompensas': recompensas,
    })


@login_required
def canjear_recompensa_view(request, recompensa_id):
    if request.method != 'POST':
        return redirect('perfil')

    perfil, _ = Perfil.objects.get_or_create(usuario=request.user)

    with transaction.atomic():
        recompensa = Recompensa.objects.select_related('producto').select_for_update().filter(
            id=recompensa_id,
            activo=True,
            producto__disponible=True,
        ).first()

        if not recompensa:
            messages.error(request, 'La recompensa no esta disponible.')
            return redirect('canjeo')

        producto = Producto.objects.select_for_update().get(id=recompensa.producto.id)

        if producto.stock <= 0:
            messages.error(request, 'No hay stock disponible para esta recompensa.')
            return redirect('canjeo')

        if perfil.puntos < recompensa.costo_puntos:
            messages.error(request, 'No tienes puntos suficientes para este canje.')
            return redirect('canjeo')

        perfil.puntos -= recompensa.costo_puntos
        perfil.save(update_fields=['puntos'])

        producto.stock -= 1
        producto.save(update_fields=['stock'])

        Canje.objects.create(
            usuario=request.user,
            recompensa=recompensa,
            producto=producto,
            costo_puntos=recompensa.costo_puntos,
        )

    messages.success(
        request,
        f'Canje completado: {producto.nombre} por {recompensa.costo_puntos} puntos.',
    )
    return redirect('canjeo')
