class Order:
    def __init__(self, order_id, user_id, product_id, order_date, delivery, promo_code):
        self.order_id = order_id
        self.user_id = user_id
        self.product_id = product_id
        self.order_date = order_date
        self.delivery = delivery
        self.promo_code = promo_code