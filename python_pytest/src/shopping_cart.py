from discount_policies import FiveForAmount, PercentageOffer, ThreeForTwo, TwoForAmount
from model_objects import ProductQuantity, SpecialOfferType


class ShoppingCart:

    def __init__(self):
        self._items = []
        self._product_quantities = {}

    @property
    def items(self):
        return self._items

    def add_item(self, product):
        self.add_item_quantity(product, 1.0)

    @property
    def product_quantities(self):
        return self._product_quantities

    def add_item_quantity(self, product, quantity):
        self._items.append(ProductQuantity(product, quantity))
        if product in self._product_quantities.keys():
            self._product_quantities[product] = self._product_quantities[product] + quantity
        else:
            self._product_quantities[product] = quantity

    def handle_offers(self, receipt, offers, catalog):
        for product in self._product_quantities:
            if product not in offers:
                continue
            policy = self._policy_for(offers[product])
            for discount in policy.apply(self._product_quantities, catalog):
                receipt.add_discount(discount)

    @staticmethod
    def _policy_for(offer):
        if offer.offer_type == SpecialOfferType.THREE_FOR_TWO:
            return ThreeForTwo(offer.product)
        if offer.offer_type == SpecialOfferType.TWO_FOR_AMOUNT:
            return TwoForAmount(offer.product, offer.argument)
        if offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT:
            return FiveForAmount(offer.product, offer.argument)
        return PercentageOffer(offer.product, offer.argument)
