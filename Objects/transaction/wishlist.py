class Wishlist:
    def __init__(self):
        self.wishlist_items = []

    def add_to_wishlist(self, item):
        self.wishlist_items.append(item)
        
class WishlistItem:
    def __init__(self, user_id, product_id, name, price, image):
        self.user_id = user_id
        self.product_id = product_id
        self.name = name
        self.price = price
        self.image = image