class Cart:
    def __init__(self):
        self.cart_items = []

    def add_to_cart(self, item):
        self.cart_items.append(item)

    def remove_from_cart(self, item):
        self.cart_items.remove(item)

    def get_cart_items(self):
        return self.cart_items

    def get_cart_total(self):
        total = 0
        for item in self.cart_items:
            total += item.price * item.quantity
        return total

class CartItem:
    def __init__(self, product_id, name, price, quantity, size, color, stock, size_options=None, color_options=None):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.size = size
        self.color = color
        self.size_options = size_options if size_options else []
        self.color_options = color_options if color_options else []
        self.stock = stock

    def to_dict(self):
        return {
            'product_id': self.product_id,
            'name': self.name,
            'price': self.price,
            'quantity': self.quantity,
            'size': self.size,
            'color': self.color,
            'stock': self.stock
        }

