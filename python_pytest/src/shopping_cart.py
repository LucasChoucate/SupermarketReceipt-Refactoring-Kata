import math

from model_objects import ProductQuantity, SpecialOfferType, Discount


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
        for product, quantity in self._product_quantities.items():
            if product not in offers:
                continue
            offer = offers[product]
            unit_price = catalog.unit_price(product)
            discount = self._discount_for(offer, product, quantity, unit_price)
            if discount:
                receipt.add_discount(discount)

    def _discount_for(self, offer, product, quantity, unit_price):
        if offer.offer_type == SpecialOfferType.THREE_FOR_TWO:
            return self._three_for_two(product, quantity, unit_price)
        if offer.offer_type == SpecialOfferType.TWO_FOR_AMOUNT:
            return self._two_for_amount(offer, product, quantity, unit_price)
        if offer.offer_type == SpecialOfferType.FIVE_FOR_AMOUNT:
            return self._five_for_amount(offer, product, quantity, unit_price)
        if offer.offer_type == SpecialOfferType.TEN_PERCENT_DISCOUNT:
            return self._percentage(offer, product, quantity, unit_price)
        return None

    @staticmethod
    def _three_for_two(product, quantity, unit_price):
        group_size = 3
        quantity_as_int = int(quantity)
        if quantity_as_int < group_size:
            return None
        number_of_groups = math.floor(quantity_as_int / group_size)
        discount_amount = quantity * unit_price - (
            (number_of_groups * 2 * unit_price) + quantity_as_int % group_size * unit_price)
        return Discount(product, "3 for 2", -discount_amount)

    @staticmethod
    def _two_for_amount(offer, product, quantity, unit_price):
        group_size = 2
        quantity_as_int = int(quantity)
        if quantity_as_int < group_size:
            return None
        # DEF-01 (legacy): real division ("/") instead of integer division ("//").
        price_with_offer = offer.argument * (quantity_as_int / group_size) + quantity_as_int % group_size * unit_price
        discount_amount = unit_price * quantity - price_with_offer
        return Discount(product, "2 for " + str(offer.argument), -discount_amount)

    @staticmethod
    def _five_for_amount(offer, product, quantity, unit_price):
        group_size = 5
        quantity_as_int = int(quantity)
        if quantity_as_int < group_size:
            return None
        number_of_groups = math.floor(quantity_as_int / group_size)
        discount_amount = unit_price * quantity - (
            offer.argument * number_of_groups + quantity_as_int % group_size * unit_price)
        return Discount(product, str(group_size) + " for " + str(offer.argument), -discount_amount)

    @staticmethod
    def _percentage(offer, product, quantity, unit_price):
        return Discount(product, str(offer.argument) + "% off",
                        -quantity * unit_price * offer.argument / 100.0)
