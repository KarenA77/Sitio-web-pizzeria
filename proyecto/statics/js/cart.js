var updateBtns = document.getElementsByClassName('update-cart');

for (var i = 0; i < updateBtns.length; i++) {
    updateBtns[i].addEventListener('click', function () {
        var productId = this.dataset.product;
        var action = this.dataset.action;
        console.log('productID:', productId, 'action:', action);

        console.log('USER:', user);
        if (user === 'AnonymousUser') {
            addCookieItem(productId, action);
        } else {
            updateUserOrder(productId, action);
        }
    });
}

function addCookieItem(productId, action) {
    console.log('Usuario no logeado');
    console.log('Cart antes de modificar:', cart);

    if (action == 'add') {
        if (cart[productId] == undefined) {
            cart[productId] = { 'quantity': 1 };
        } else {
            cart[productId]['quantity'] += 1;
        }
    }
    if (action == 'remove') {
        cart[productId]['quantity'] -= 1;   

        if (cart[productId]['quantity'] <= 0) {
            console.log('Producto eliminado');
            delete cart[productId];
        }
    }
    console.log('Cart después de modificar:', cart);
    console.log('Cart:', cart);
    document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/";
    console.log('Cookie actualizada:', document.cookie);
    // Puedes evitar recargar la página y actualizar dinámicamente el carrito
    location.reload() 
    //updateCartUI(); 
    
    
}

function updateUserOrder(productId, action) {
    console.log('Usuario autenticado, enviando datos...');

    var url = '/update_item/';

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken,
        },
        body: JSON.stringify({ 'productId': productId, 'action': action })
    })
    .then((response) => response.json())
    .then((data) => {
        console.log('data:', data);
        history.go(0); // O considera usar updateCartUI() para evitar recargar
    });
}

function updateCartUI() {
    // Actualiza dinámicamente la interfaz del carrito
    let cartTotal = document.getElementById('cart-total');
    let totalItems = Object.values(cart).reduce((acc, item) => acc + item.quantity, 0);
    cartTotal.textContent = totalItems;
}
