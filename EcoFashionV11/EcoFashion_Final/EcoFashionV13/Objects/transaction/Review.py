class Review:
    def __init__(self, review_id, product_id, user_id, author, rating, description):
        self.review_id = review_id
        self.product_id = product_id
        self.user_id = user_id
        self.author = author
        self.rating = rating
        self.description = description