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
