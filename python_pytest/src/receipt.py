"""Receipt of a purchase: items, discounts and total."""


class ReceiptItem:
    """A line of the receipt for one addition of a product to the cart."""

    def __init__(self, product, quantity, price, total_price):
        self.product = product
        self.quantity = quantity
        self.price = price
        self.total_price = total_price


class Receipt:
    """Items and discounts of a purchase."""

    def __init__(self):
        self._items = []
        self._discounts = []

    def total_price(self):
        """Sum of the items plus the (negative) discounts."""
        total = 0
        for item in self.items:
            total += item.total_price
        for discount in self.discounts:
            total += discount.discount_amount
        return total

    def add_product(self, product, quantity, price, total_price):
        """Add an item line to the receipt."""
        self._items.append(ReceiptItem(product, quantity, price, total_price))

    def add_discount(self, discount):
        """Add a discount line to the receipt."""
        self._discounts.append(discount)

    @property
    def items(self):
        """Copy of the item lines."""
        return self._items[:]

    @property
    def discounts(self):
        """Copy of the discount lines."""
        return self._discounts[:]
