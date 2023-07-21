class Product:
    def __init__(self, name, price, description, image, category):
        self.name = name
        self.price = price
        self.description = description
        self.image = image
        self.category = category
    
    def getName(self):
        return self.name
    def getPrice(self):
        return self.price
    def getDescription(self):
        return self.description
    def getImage(self):
        return self.image
    def getCategory(self):
        return self.category
    def setName(self, name):
        self.name = name
    def setPrice(self, price):
        self.price = price
    def setDescription(self, description):
        self.description = description
    def setImage(self, image):
        self.image = image
    def setCategory(self, category):
        self.category = category
        