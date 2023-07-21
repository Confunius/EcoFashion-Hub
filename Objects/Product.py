class Product:
    def __init__(self, name, price, description, image):
        self.name = name
        self.price = price
        self.description = description
        self.image = image
    
    def getName(self):
        return self.name
    def getPrice(self):
        return self.price
    def getDescription(self):
        return self.description
    def getImage(self):
        return self.image
    def setName(self, name):
        self.name = name
    def setPrice(self, price):
        self.price = price
    def setDescription(self, description):
        self.description = description
    def setImage(self, image):
        self.image = image
        