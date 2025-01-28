from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django import forms
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import PasswordResetConfirmView
from django.contrib import messages
from .utils import cookieCart, cartData, guestOrder
from .models import *
from django.http import JsonResponse,HttpResponseRedirect
from django.urls import reverse
import datetime
import json


def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems}
    return render(request, 'generales/store.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']
    order = data['order']
        
    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'generales/cart.html', context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    items = data['items']   
    order = data['order']

    context = {'items': items, 'order': order, 'cartItems': cartItems}
    return render(request, 'generales/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('productId:', productId)
    print('action:', action)

    if request.user.is_authenticated:
        # Verifica si el usuario tiene un objeto Customer asociado
        try:
            customer = request.user.customer
        except Customer.DoesNotExist:
            # Crea un objeto Customer si no existe
            customer = Customer.objects.create(user=request.user, name=request.user.username, email=request.user.email)
    else:
        # Maneja el caso de usuarios no autenticados usando cookies
        customer = None

    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('El producto fue agregado', safe=False)


from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def processOrder(request):
    try:
        transaction_id = datetime.datetime.now().timestamp()
        data = json.loads(request.body)

        if request.user.is_authenticated:
            customer = request.user.customer
            order, created = Order.objects.get_or_create(customer=customer, complete=False)
        else:
            customer, order = guestOrder(request, data)

        total = float(data['form']['total'])
        order.transaction_id = transaction_id

        if abs(total - order.get_cart_total) > 0.01:
            return JsonResponse({'error': 'Total no coincide con el carrito'}, status=400)

        order.complete = True
        order.save()

        if order.shipping:
            shipping_data = data.get('shipping', {})
            ShippingAddress.objects.create(
                customer=customer,
                order=order,
                direccion=shipping_data.get('direccion', ''),
                ciudad=shipping_data.get('ciudad', ''),
                departamento=shipping_data.get('departamento', ''),
                pais=shipping_data.get('pais', ''),
                zip=shipping_data.get('zip', ''),
            )
        return JsonResponse('El pago fue procesado', safe=False)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        if not username or not password:
            messages.error(request, 'Por favor, complete todos los campos.')
            return render(request, 'generales/login.html')
            
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, '¡Inicio de sesión exitoso!')
                return redirect('inicio')
            else:
                messages.error(request, 'Su cuenta está desactivada.')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
        
        return render(request, 'generales/login.html')
        
    return render(request, 'generales/login.html')


#def register_view(request):
#    if request.method == 'POST':
#        username = request.POST['username']
#        email = request.POST['email']
#        password = request.POST['password']
#        cpassword = request.POST['cpassword']
#        if password != cpassword:
#            return render(request, 'generales/registro.html', {'error': 'Las contraseñas no coinciden'})
#        user = authenticate(request, username=username, password=password)
#        if user is not None:
#            login(request, user)
#            return HttpResponseRedirect(reverse('home'))  # Redirige al inicio
#        else:
#            return render(request, 'generales/registro.html', {'error': 'Credenciales inválidas'})
#    return render(request, 'generales/registro.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['cpassword']

        if not all([username, email, password, cpassword]):
            messages.error(request, 'Por favor, completa todos los campos.')
            return redirect('register')

        # Validación de longitud de contraseña
        if len(password) < 12:
            messages.error(request, 'La contraseña debe tener al menos 12 caracteres.')
            return redirect('register')

        # Validación de mayúscula
        if not any(c.isupper() for c in password):
            messages.error(request, 'La contraseña debe contener al menos una letra mayúscula.')
            return redirect('register')

        # Validación de dígito
        if not any(c.isdigit() for c in password):
            messages.error(request, 'La contraseña debe contener al menos un número.')
            return redirect('register')

        # Validación de símbolo especial
        special_chars = ['*', '#', '@', '$', '&', '!', '?', '%']
        if not any(c in special_chars for c in password):
            messages.error(request, 'La contraseña debe contener al menos un símbolo especial (*, #, @, $, &, !, ?, %).')
            return redirect('register')

        if password != cpassword:
            messages.error(request, 'Las contraseñas no coinciden. Por favor, intente de nuevo.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe. Por favor, intente de nuevo o inicie sesión.')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, '¡Registro de usuario exitoso!')
        login(request, user)
        return redirect('inicio')

    return render(request, 'generales/registro.html')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'generales/password_reset_confirm.html'
    form_class = SetPasswordForm

    def form_valid(self, form):
        password = form.cleaned_data['new_password1']

        # Validaciones de la contraseña
        if len(password) < 12:
            messages.error(self.request, 'La contraseña debe tener al menos 12 caracteres.')
            return redirect('password_reset_confirm', uidb64=self.kwargs['uidb64'], token=self.kwargs['token'])

        if not any(c.isupper() for c in password):
            messages.error(self.request, 'La contraseña debe contener al menos una letra mayúscula.')
            return redirect('password_reset_confirm', uidb64=self.kwargs['uidb64'], token=self.kwargs['token'])

        if not any(c.isdigit() for c in password):
            messages.error(self.request, 'La contraseña debe contener al menos un número.')
            return redirect('password_reset_confirm', uidb64=self.kwargs['uidb64'], token=self.kwargs['token'])

        special_chars = ['*', '#', '@', '$', '&', '!', '?', '%']
        if not any(c in special_chars for c in password):
            messages.error(self.request, 'La contraseña debe contener al menos un símbolo especial (*, #, @, $, &, !, ?, %).')
            return redirect('password_reset_confirm', uidb64=self.kwargs['uidb64'], token=self.kwargs['token'])

        messages.success(self.request, '¡Contraseña actualizada con éxito!')
        return super().form_valid(form)
    

def inicio(request):
    return render(request, 'generales/inicio.html')

def logout(request):
    messages.success(request, '¡Cierre de sesión exitoso!')
    return render(request, 'generales/logout.html')
