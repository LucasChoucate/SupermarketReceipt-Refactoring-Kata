"""Checkout of purchases."""
from discount_engine import DiscountEngine
from discount_policies import BundleOffer
from model_objects import Offer
from receipt import Receipt


class Teller:
    """Registers special offers and checks out shopping carts."""

    def __init__(self, catalog):
        self.catalog = catalog
        self.offers = {}
        self.bundles = []
        self._discount_engine = DiscountEngine()

    def add_special_offer(self, offer_type, product, argument):
        """Register an offer for ``product``, replacing any previous one."""
        self.offers[product] = Offer(offer_type, product, argument)

    def add_bundle_offer(self, products, percent=10):
        """Register a bundle (combo) of ``products`` with ``percent`` off.

        A product repeated in ``products`` must appear that many times in
        the cart to complete the bundle. Bundles are kept apart from the
        special offers and are applied in the order they were registered.
        """
        if not products:
            raise ValueError("a bundle needs at least one product")
        required = {}
        for product in products:
            required[product] = required.get(product, 0) + 1
        self.bundles.append(BundleOffer(required, percent))

    def checks_out_articles_from(self, the_cart):
        """Return the receipt of ``the_cart`` with prices and discounts."""
        receipt = Receipt()
        for item in the_cart.items:
            unit_price = self.catalog.unit_price(item.product)
            total_price = item.quantity * unit_price
            receipt.add_product(item.product, item.quantity, unit_price, total_price)

        self._discount_engine.apply(
            receipt, the_cart.product_quantities, self.offers, self.catalog, self.bundles)

        return receipt

    def product_with_name(self, name):
        """Return the product called ``name``, or None if it does not exist."""
        return self.catalog.product_with_name(name)
