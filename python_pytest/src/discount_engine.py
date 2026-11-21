"""Applies the discount policies of a purchase and records the discounts."""
from discount_policies import create_policy


class DiscountEngine:
    """Applies the special offers to the quantities of a purchase."""

    def apply(self, receipt, quantities, offers, catalog):
        """Add to ``receipt`` the discounts of ``offers`` over ``quantities``.

        Discounts follow the order in which the products were first added.
        """
        policies = [create_policy(offers[product]) for product in quantities if product in offers]
        for discount in self._apply_in_order(policies, quantities, catalog):
            receipt.add_discount(discount)

    @staticmethod
    def _apply_in_order(policies, quantities, catalog):
        """Apply the policies in sequence; each one only sees the units left by the previous ones."""
        available = dict(quantities)
        discounts = []
        for policy in policies:
            result = policy.apply(available, catalog)
            discounts.extend(result.discounts)
            for product, quantity in result.consumed.items():
                available[product] -= quantity
        return discounts
