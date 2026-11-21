"""Shopping cart of a purchase."""
from discount_engine import DiscountEngine
from model_objects import ProductQuantity


class ShoppingCart:
    """Products and quantities added to a purchase."""

    def __init__(self):
        self._items = []
        self._product_quantities = {}

    @property
    def items(self):
        """Each addition to the cart, in order, as ProductQuantity."""
        return self._items

    def add_item(self, product):
        """Add one unit of ``product``."""
        self.add_item_quantity(product, 1.0)

    @property
    def product_quantities(self):
        """Total quantity of each product, in the order of first addition."""
        return self._product_quantities

    def add_item_quantity(self, product, quantity):
        """Add ``quantity`` of ``product`` (a fraction for products sold by weight)."""
        self._items.append(ProductQuantity(product, quantity))
        if product in self._product_quantities.keys():
            self._product_quantities[product] = self._product_quantities[product] + quantity
        else:
            self._product_quantities[product] = quantity

    def handle_offers(self, receipt, offers, catalog):
        """Add to ``receipt`` the discounts of ``offers``.

        Kept for compatibility with the legacy interface; the calculation
        is done by DiscountEngine.
        """
        DiscountEngine().apply(receipt, self._product_quantities, offers, catalog)
