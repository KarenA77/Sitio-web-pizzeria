import json
from django.http import JsonResponse
from .models import Product, Order, OrderItem, Customer

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES.get('cart', '{}'))  # Si no hay cookie, devuelve un diccionario vacío
    except json.JSONDecodeError:
        cart = {}

    # Inicializar las variables
    items = []
    order = {'get_cart_items': 0, 'get_cart_total': 0, 'shipping': False}
    cartItems = order['get_cart_items']

    # Procesar los productos en el carrito
    for i in cart:
        try:
            quantity = cart[i].get('quantity', 0)
            cartItems += quantity
            product = Product.objects.get(id=i)
            total = (product.price * quantity)
            order['get_cart_total'] += total
            order['get_cart_items'] += quantity

            item = {
                'product': {
                    'id': product.id,
                    'name': product.name,
                    'price': product.price,
                    'imageURL': product.imageURL,
                },
                'quantity': quantity,
                'get_total': total
            }
            items.append(item)
            if not product.digital:
                order['shipping'] = True
        except Product.DoesNotExist:
            print(f"Producto con ID {i} no encontrado. Ignorando.")

    return {'items': items, 'order': order, 'cartItems': cartItems}

def cartData(request):
    if request.user.is_authenticated:
        try:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
            items = order.orderitem_set.all()
            cartItems = order.get_cart_items
        except Customer.DoesNotExist:
            return {'items': [], 'order': {'get_cart_items': 0, 'get_cart_total': 0, 'shipping': False}, 'cartItems': 0}
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']

    return {'items': items, 'order': order, 'cartItems': cartItems}

def guestOrder(request, data):
    name = data['form'].get('name', '')
    email = data['form'].get('email', '')

    if not name or not email:
        raise ValueError("Faltan datos del formulario: nombre o correo electrónico")

    cookieData = cartData(request)
    items = cookieData['items']
    customer, created = Customer.objects.get_or_create(email=email)
    customer.name = name
    customer.save()

    order = Order.objects.create(customer=customer, complete=False)

    for item in items:
        try:
            product = Product.objects.get(id=item['product']['id'])
            OrderItem.objects.create(
                product=product,
                order=order,
                quantity=item['quantity'],
            )
        except Product.DoesNotExist:
            print(f"Producto con ID {item['product']['id']} no encontrado. Ignorando.")

    return customer, order


