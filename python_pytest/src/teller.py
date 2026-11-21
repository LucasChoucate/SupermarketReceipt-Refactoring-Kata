"""Checkout of purchases."""
from discount_engine import DiscountEngine
from model_objects import Offer
from receipt import Receipt


class Teller:
    """Registers special offers and checks out shopping carts."""

    def __init__(self, catalog):
        self.catalog = catalog
        self.offers = {}
        self._discount_engine = DiscountEngine()

    def add_special_offer(self, offer_type, product, argument):
        """Register an offer for ``product``, replacing any previous one."""
        self.offers[product] = Offer(offer_type, product, argument)

    def checks_out_articles_from(self, the_cart):
        """Return the receipt of ``the_cart`` with prices and discounts."""
        receipt = Receipt()
        for item in the_cart.items:
            unit_price = self.catalog.unit_price(item.product)
            total_price = item.quantity * unit_price
            receipt.add_product(item.product, item.quantity, unit_price, total_price)

        self._discount_engine.apply(receipt, the_cart.product_quantities, self.offers, self.catalog)

        return receipt

    def product_with_name(self, name):
        """Return the product called ``name``, or None if it does not exist."""
        return self.catalog.product_with_name(name)
