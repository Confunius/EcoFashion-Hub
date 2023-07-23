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

    def to_dict(self):
        # Convert the cart items to a list of dictionaries
        cart_items_dict = [item.__dict__ for item in self.cart_items]
        return {"cart_items": cart_items_dict}

class CartItem:
    def __init__(self, product_id, name, price, quantity, size):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.quantity = quantity
        self.size = size