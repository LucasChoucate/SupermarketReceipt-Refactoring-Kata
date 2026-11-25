"""Exemplo de uso do Supermarket Receipt: emite um recibo com oferta e combo.

Execute a partir da pasta python_pytest, com o Python do ambiente virtual:

    Linux e macOS:  .venv/bin/python exemplo_de_uso.py
    Windows:        .venv\\Scripts\\python.exe exemplo_de_uso.py

O catálogo real (SupermarketCatalog) acessa um banco de dados que não faz
parte do kata. Por isso o exemplo usa o catálogo em memória e a impressora
de recibos que acompanham os testes, na pasta tests/.
"""
import sys
from pathlib import Path

# Torna src/ e tests/ importáveis em qualquer sistema operacional, sem
# depender da variável PYTHONPATH, cujo separador muda entre Linux e Windows.
PASTA_DO_PROJETO = Path(__file__).resolve().parent
sys.path[:0] = [str(PASTA_DO_PROJETO / "src"), str(PASTA_DO_PROJETO / "tests")]

from fake_catalog import FakeCatalog
from model_objects import Product, ProductUnit, SpecialOfferType
from receipt_printer import ReceiptPrinter
from shopping_cart import ShoppingCart
from teller import Teller


def main():
    catalogo = FakeCatalog()
    escova = Product("escova", ProductUnit.EACH)
    creme_dental = Product("creme dental", ProductUnit.EACH)
    maca = Product("maca", ProductUnit.KILO)
    catalogo.add_product(escova, 10.00)
    catalogo.add_product(creme_dental, 15.00)
    catalogo.add_product(maca, 2.00)

    teller = Teller(catalogo)
    teller.add_special_offer(SpecialOfferType.TEN_PERCENT_DISCOUNT, maca, 20.0)  # 20% na maçã
    teller.add_bundle_offer([escova, creme_dental])  # combo com 10% de desconto

    carrinho = ShoppingCart()
    carrinho.add_item_quantity(escova, 2)  # a segunda escova não completa outro combo
    carrinho.add_item_quantity(creme_dental, 1)
    carrinho.add_item_quantity(maca, 1.5)  # produto vendido por peso, em kg

    recibo = teller.checks_out_articles_from(carrinho)
    print(ReceiptPrinter().print_receipt(recibo))


if __name__ == "__main__":
    main()
