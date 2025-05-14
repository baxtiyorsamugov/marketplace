def cart_count(request):
    cart = request.session.get('cart', {})
    total_qty = sum(cart.values())
    return {'cart_count': total_qty}
