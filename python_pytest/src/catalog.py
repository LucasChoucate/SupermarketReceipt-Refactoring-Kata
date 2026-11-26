"""Contract of the product catalog."""


class SupermarketCatalog:
    """Product catalog backed by a database.

    Tests use an in-memory implementation (tests/fake_catalog.py).
    """

    def add_product(self, product, price):
        """Register ``product`` with its unit ``price``."""
        raise Exception("cannot be called from a unit test - it accesses the database")

    def unit_price(self, product):
        """Return the current unit price of ``product``."""
        raise Exception("cannot be called from a unit test - it accesses the database")

    def product_with_name(self, name):
        """Return the product called ``name``, or None if it does not exist."""
        raise Exception("cannot be called from a unit test - it accesses the database")
