from .models import ItemsInventory


class Cart():
    """
    A base cart class, providing some default behaviors that
    can be inherited or overrided, as necessary.
    """

    def __init__(self, request):
        self.session = request.session
        cart = self.session.get('session_data')

        if 'session_data' not in request.session:
            cart = self.session['session_data'] = {}
        self.cart = cart

    def add(self, product, qty):
        """
        Adding and updating the users cart session data
        """
        product_id = str(product.SKU)

        if product_id in self.cart:
            self.cart[product_id]['qty'] = qty
        else:
            self.cart[product_id] = {'price': str(product.item_id.price), 'qty': qty}

        self.save()

    def __iter__(self):
        """
        Collect the product_id in the session data to query the database
        and return products
        """
        product_ids = self.cart.keys()

        products = ItemsInventory.objects.filter(SKU__in=product_ids)
        cart = self.cart.copy()

        for product in products:
            cart[str(product.SKU)]['product'] = product.SKU

        for item in cart.values():
            item['price'] = round(float(item['price']), 2)
            item['total_price'] = round(item['price'] * item['qty'],2)
            yield item

    def __len__(self):
        """
        Get the cart data and count the qty of items
        """
        return sum(item['qty'] for item in self.cart.values())

    def update(self, product, qty):
        """
        Update values in session data
        """
        product_id = str(product)
        
        if product_id in self.cart:
            self.cart[product_id]['qty'] = qty
        self.save()

    def get_total_price(self):
        return sum(float(item['price']) * item['qty'] for item in self.cart.values())

    def delete(self, product):
        """
        Delete item from session data
        """
        product_id = str(product)

        if product_id in self.cart:
            del self.cart[product_id]
            self.save()
    
    def clear(self):
        """
        Clear all item from session data
        """
        self.session['session_data'] = {}
        self.save()

    def save(self):
        self.session.modified = True