"""Applies the discount policies of a purchase and records the discounts."""
from discount_policies import create_policy


class DiscountEngine:
    """Applies the special offers and the bundles to the quantities of a purchase."""

    def apply(self, receipt, quantities, offers, catalog, bundles=()):
        """Add to ``receipt`` the discounts of ``offers`` and ``bundles`` over ``quantities``.

        When individual offers and bundles compete for the same units, the
        purchase is calculated in two orders and the cheaper one is kept:
        offers first (C) or bundles first (B). Totals are compared in cents
        and a tie keeps the offers (C), so a bundle never replaces an offer
        without a real gain and registering a bundle never makes a cart
        more expensive.

        In the receipt, individual discounts come first, in the order in
        which the products were first added, followed by the bundles in the
        order in which they were registered.
        """
        individual = [create_policy(offers[product]) for product in quantities if product in offers]
        bundles = list(bundles)
        chosen = self._apply_in_order(individual + bundles, quantities, catalog)
        if bundles and individual:
            bundles_first = self._apply_in_order(bundles + individual, quantities, catalog)
            if self._in_cents(bundles_first) < self._in_cents(chosen):
                chosen = bundles_first
        for policy in individual + bundles:
            for discount in chosen[policy]:
                receipt.add_discount(discount)

    @staticmethod
    def _apply_in_order(policies, quantities, catalog):
        """Apply the policies in sequence; each one only sees the units left by the previous ones.

        Return the discounts of each policy. A policy is skipped when the
        previous ones consumed all the units of its products, so that it
        does not add empty discount lines.
        """
        available = dict(quantities)
        discounts = {}
        for policy in policies:
            if all(quantities[product] and not available[product]
                   for product in policy.products() if product in quantities):
                discounts[policy] = []
                continue
            result = policy.apply(available, catalog)
            discounts[policy] = result.discounts
            for product, quantity in result.consumed.items():
                available[product] -= quantity
        return discounts

    @staticmethod
    def _in_cents(discounts_by_policy):
        return round(sum(d.discount_amount for ds in discounts_by_policy.values() for d in ds), 2)
