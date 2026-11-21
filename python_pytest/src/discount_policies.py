"""Discount policies: one strategy per kind of special offer."""
from abc import ABC, abstractmethod

from model_objects import Discount


class DiscountPolicy(ABC):
    """Strategy for calculating the discounts of a special offer."""

    @abstractmethod
    def apply(self, available, catalog):
        """Return the discounts granted for the quantities in ``available``.

        ``available`` maps each product to the quantity still available
        for discounts. ``catalog`` provides the unit prices.
        """


class PercentageOffer(DiscountPolicy):
    """Percentage discount applied to the whole quantity of a product."""

    def __init__(self, product, percentage):
        self.product = product
        self.percentage = percentage

    def apply(self, available, catalog):
        quantity = available[self.product]
        unit_price = catalog.unit_price(self.product)
        amount = -quantity * unit_price * self.percentage / 100.0
        return [Discount(self.product, str(self.percentage) + "% off", amount)]


class GroupPriceOffer(DiscountPolicy):
    """Template Method for offers that sell a group of units for a special price.

    The algorithm is the same for every group offer; subclasses only
    provide the group size, the price of a group and the description.
    """

    def __init__(self, product):
        self.product = product

    def apply(self, available, catalog):
        quantity = available[self.product]
        quantity_as_int = int(quantity)
        if quantity_as_int < self.group_size():
            return []
        unit_price = catalog.unit_price(self.product)
        number_of_groups = self.number_of_groups(quantity_as_int)
        # DEF-02 (legacy): the remainder ignores the fraction of products sold by weight.
        remainder = quantity_as_int % self.group_size()
        price_with_offer = number_of_groups * self.group_price(unit_price) + remainder * unit_price
        discount_amount = quantity * unit_price - price_with_offer
        return [Discount(self.product, self.description(), -discount_amount)]

    def number_of_groups(self, quantity_as_int):
        """Number of complete groups in the quantity."""
        return quantity_as_int // self.group_size()

    @abstractmethod
    def group_size(self):
        """Number of units in a group."""

    @abstractmethod
    def group_price(self, unit_price):
        """Price charged for a complete group."""

    @abstractmethod
    def description(self):
        """Text of the discount line in the receipt."""


class ThreeForTwo(GroupPriceOffer):
    """Buy three units and pay for two."""

    def group_size(self):
        return 3

    def group_price(self, unit_price):
        return 2 * unit_price

    def description(self):
        return "3 for 2"


class TwoForAmount(GroupPriceOffer):
    """Two units for a fixed amount."""

    def __init__(self, product, amount):
        super().__init__(product)
        self.amount = amount

    def number_of_groups(self, quantity_as_int):
        # DEF-01 (legacy): real division ("/") instead of integer division ("//").
        return quantity_as_int / self.group_size()

    def group_size(self):
        return 2

    def group_price(self, unit_price):
        return self.amount

    def description(self):
        return "2 for " + str(self.amount)


class FiveForAmount(GroupPriceOffer):
    """Five units for a fixed amount."""

    def __init__(self, product, amount):
        super().__init__(product)
        self.amount = amount

    def group_size(self):
        return 5

    def group_price(self, unit_price):
        return self.amount

    def description(self):
        return "5 for " + str(self.amount)
