"""Comportamento correto dos defeitos confirmados do legado.

Cada teste descreve o comportamento CORRETO e está marcado com
xfail(strict=True): ele falha enquanto o defeito existe, o que serve de
evidência do defeito. No commit fix: de cada defeito (Fases 4.7 a 4.9), a
marcação xfail é removida e o teste que fixava o comportamento defeituoso,
em test_comportamento_legado.py, é apagado.

Com strict=True, se o defeito for corrigido e a marcação não for removida,
o teste passa a falhar (XPASS), o que impede que ela fique esquecida.

Detalhes de cada defeito: docs/registro_de_defeitos.md.
"""
import pytest

from catalog import SupermarketCatalog
from model_objects import Product, ProductUnit, SpecialOfferType
from teller import Teller
from tests.auxiliares import fechar_compra, total_descontos

TRES_POR_DOIS = SpecialOfferType.THREE_FOR_TWO
DOIS_POR_VALOR = SpecialOfferType.TWO_FOR_AMOUNT
CINCO_POR_VALOR = SpecialOfferType.FIVE_FOR_AMOUNT


# DEF-01: "2 por valor" com quantidade ímpar

@pytest.mark.parametrize("quantidade, desconto_esperado, total_esperado", [
    (3, -5.0, 25.0),    # 1 par a R$ 15,00 + 1 unidade a R$ 10,00
    (5, -10.0, 40.0),   # 2 pares + 1 unidade
    (7, -15.0, 55.0),   # 3 pares + 1 unidade
])
def test_dois_por_valor_com_quantidade_impar_cobra_sobra_a_preco_cheio(
        teller, escova, quantidade, desconto_esperado, total_esperado):
    teller.add_special_offer(DOIS_POR_VALOR, escova, 15.0)

    recibo = fechar_compra(teller, (escova, quantidade))

    assert total_descontos(recibo) == pytest.approx(desconto_esperado)
    assert recibo.total_price() == pytest.approx(total_esperado)


# DEF-02: fração gratuita nas ofertas por grupo

@pytest.mark.parametrize("oferta, argumento, quantidade, desconto_esperado, total_esperado", [
    (TRES_POR_DOIS, None, 2.9, 0.0, 5.80),      # parte inteira 2: a oferta não ativa
    (TRES_POR_DOIS, None, 3.5, -2.0, 5.00),     # 3 kg por 2 kg + 0,5 kg a preço cheio
    (DOIS_POR_VALOR, 3.0, 2.5, -1.0, 4.00),     # 2 kg por R$ 3,00 + 0,5 kg a preço cheio
    (CINCO_POR_VALOR, 8.0, 5.5, -2.0, 9.00),    # 5 kg por R$ 8,00 + 0,5 kg a preço cheio
])
def test_promocao_por_grupo_cobra_a_fracao_restante(
        teller, maca, oferta, argumento, quantidade, desconto_esperado, total_esperado):
    teller.add_special_offer(oferta, maca, argumento)

    recibo = fechar_compra(teller, (maca, quantidade))

    assert total_descontos(recibo) == pytest.approx(desconto_esperado)
    assert recibo.total_price() == pytest.approx(total_esperado)


# DEF-03: product_with_name fora do contrato do catálogo

class CatalogoDoContrato(SupermarketCatalog):
    """Catálogo que implementa só o contrato, sem o atributo `products` do FakeCatalog."""

    def __init__(self):
        self._produtos = {}
        self._precos = {}

    def add_product(self, product, price):
        self._produtos[product.name] = product
        self._precos[product.name] = price

    def unit_price(self, product):
        return self._precos[product.name]

    def product_with_name(self, name):
        return self._produtos.get(name)


@pytest.mark.xfail(strict=True, raises=AttributeError,
                   reason="DEF-03: Teller acessa catalog.products, fora do contrato")
def test_product_with_name_funciona_com_qualquer_catalogo_do_contrato():
    catalogo = CatalogoDoContrato()
    escova = Product("escova", ProductUnit.EACH)
    catalogo.add_product(escova, 10.00)
    teller = Teller(catalogo)

    assert teller.product_with_name("escova") is escova
    assert teller.product_with_name("inexistente") is None
