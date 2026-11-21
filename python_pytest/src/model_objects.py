"""Domain objects: products, quantities, offers and discounts."""
from enum import Enum


class Product:
    """A product sold by unit or by weight."""

    def __init__(self, name, unit):
        self.name = name
        self.unit = unit


class ProductQuantity:
    """A quantity of a product added to the cart."""

    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity


class ProductUnit(Enum):
    """How a product is sold: by unit (EACH) or by weight (KILO)."""

    EACH = 1
    KILO = 2


class SpecialOfferType(Enum):
    """Kinds of special offer.

    TEN_PERCENT_DISCOUNT applies the percentage given as the offer argument,
    which is not necessarily 10%.
    """

    THREE_FOR_TWO = 1
    TEN_PERCENT_DISCOUNT = 2
    TWO_FOR_AMOUNT = 3
    FIVE_FOR_AMOUNT = 4


class Offer:
    """A special offer for a product.

    The meaning of ``argument`` depends on ``offer_type``: the percentage
    for TEN_PERCENT_DISCOUNT, the price of the group for TWO_FOR_AMOUNT and
    FIVE_FOR_AMOUNT, and nothing for THREE_FOR_TWO.
    """

    def __init__(self, offer_type, product, argument):
        self.offer_type = offer_type
        self.product = product
        self.argument = argument


class Discount:
    """A discount line of the receipt; ``discount_amount`` is negative."""

    def __init__(self, product, description, discount_amount):
        self.product = product
        self.description = description
        self.discount_amount = discount_amount
