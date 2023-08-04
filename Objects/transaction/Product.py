class Product:
    def __init__(self, product_id, name, color_options, size_options, cost_price, list_price, stock, description, image, category):
        self.product_id = product_id
        self.name = name
        self.color_options = color_options if color_options else []
        self.size_options = size_options if size_options else []
        self.cost_price = cost_price
        self.list_price = list_price
        self.stock = stock
        self.description = description
        self.image = image
        self.category = category
    
    def to_dict(self):
        return {
            'product_id': self.product_id,
            'name': self.name,
            'color_options': self.color_options,
            'size_options': self.size_options,
            'cost_price': self.cost_price,
            'list_price': self.list_price,
            'stock': self.stock,
            'description': self.description,
            'image': self.image,
            'category': self.category
        }