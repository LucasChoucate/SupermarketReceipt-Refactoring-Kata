from model_objects import Offer
from receipt import Receipt


class Teller:

    def __init__(self, catalog):
        self.catalog = catalog
        self.offers = {}

    def add_special_offer(self, offer_type, product, argument):
        self.offers[product] = Offer(offer_type, product, argument)

    def checks_out_articles_from(self, the_cart):
        receipt = Receipt()
        for item in the_cart.items:
            unit_price = self.catalog.unit_price(item.product)
            total_price = item.quantity * unit_price
            receipt.add_product(item.product, item.quantity, unit_price, total_price)

        the_cart.handle_offers(receipt, self.offers, self.catalog)

        return receipt

    def product_with_name(self, name):
        return self.catalog.products.get(name, None)