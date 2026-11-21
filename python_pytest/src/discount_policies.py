"""Discount policies: one strategy per kind of special offer."""
from abc import ABC, abstractmethod
from typing import NamedTuple

from model_objects import Discount, SpecialOfferType


class PolicyResult(NamedTuple):
    """Discounts granted by a policy and the units it consumed."""

    discounts: list
    consumed: dict


class DiscountPolicy(ABC):
    """Strategy for calculating the discounts of a special offer."""

    @abstractmethod
    def apply(self, available, catalog):
        """Return a PolicyResult for the quantities in ``available``.

        ``available`` maps each product to the quantity still available
        for discounts. ``catalog`` provides the unit prices. The units
        listed in ``PolicyResult.consumed`` cannot receive another discount.
        """

    @abstractmethod
    def products(self):
        """Products this policy can discount."""


class PercentageOffer(DiscountPolicy):
    """Percentage discount applied to the whole quantity of a product."""

    def __init__(self, product, percentage):
        self.product = product
        self.percentage = percentage

    def products(self):
        return (self.product,)

    def apply(self, available, catalog):
        """Discount the percentage over all available units, consuming them all."""
        quantity = available[self.product]
        unit_price = catalog.unit_price(self.product)
        amount = -quantity * unit_price * self.percentage / 100.0
        discount = Discount(self.product, str(self.percentage) + "% off", amount)
        return PolicyResult([discount], {self.product: quantity})


class GroupPriceOffer(DiscountPolicy):
    """Template Method for offers that sell a group of units for a special price.

    The algorithm is the same for every group offer; subclasses only
    provide the group size, the price of a group and the description.
    """

    def __init__(self, product):
        self.product = product

    def products(self):
        return (self.product,)

    def apply(self, available, catalog):
        """Template method: charge each complete group at the group price and the rest at full price.

        Subclasses customize the calculation only through the hooks
        ``group_size``, ``group_price`` and ``description``.
        """
        quantity = available[self.product]
        quantity_as_int = int(quantity)
        if quantity_as_int < self.group_size():
            return PolicyResult([], {})
        unit_price = catalog.unit_price(self.product)
        number_of_groups = self.number_of_groups(quantity_as_int)
        remainder = quantity - number_of_groups * self.group_size()
        price_with_offer = number_of_groups * self.group_price(unit_price) + remainder * unit_price
        discount_amount = quantity * unit_price - price_with_offer
        discount = Discount(self.product, self.description(), -discount_amount)
        return PolicyResult([discount], {self.product: number_of_groups * self.group_size()})

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



class BundleOffer(DiscountPolicy):
    """Discount on each complete bundle of products (combo).

    A bundle is complete when the cart has every product of the bundle in
    the required quantity. The percentage applies only to the units that
    form complete bundles; the remaining units keep their price.
    """

    def __init__(self, required, percent=10):
        """``required`` maps each product of the bundle to the units it needs."""
        self.required = dict(required)
        self.percent = percent

    def products(self):
        return tuple(self.required)

    def apply(self, available, catalog):
        """Discount the complete bundles, consuming the units they use."""
        number_of_bundles = min(
            int(available.get(product, 0)) // quantity for product, quantity in self.required.items())
        if number_of_bundles <= 0:
            return PolicyResult([], {})
        discounts = []
        consumed = {}
        for product, quantity in self.required.items():
            units = number_of_bundles * quantity
            amount = -units * catalog.unit_price(product) * self.percent / 100.0
            discounts.append(Discount(product, self.description(), amount))
            consumed[product] = units
        return PolicyResult(discounts, consumed)

    def description(self):
        """Text of the discount lines in the receipt."""
        return "combo " + str(self.percent) + "% off"

# Simple Factory: translates the public SpecialOfferType into a strategy.
# A new kind of offer only needs a new policy class and one entry here.
_POLICY_BY_OFFER_TYPE = {
    SpecialOfferType.THREE_FOR_TWO: lambda offer: ThreeForTwo(offer.product),
    SpecialOfferType.TEN_PERCENT_DISCOUNT: lambda offer: PercentageOffer(offer.product, offer.argument),
    SpecialOfferType.TWO_FOR_AMOUNT: lambda offer: TwoForAmount(offer.product, offer.argument),
    SpecialOfferType.FIVE_FOR_AMOUNT: lambda offer: FiveForAmount(offer.product, offer.argument),
}


def create_policy(offer):
    """Create the discount policy that implements ``offer``."""
    return _POLICY_BY_OFFER_TYPE[offer.offer_type](offer)
