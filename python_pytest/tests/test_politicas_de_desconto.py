"""Testes unitários das políticas de desconto (Strategy, Template Method e Simple Factory).

Os testes de caracterização garantem que o comportamento do legado foi
preservado. Estes testes mostram o que a nova estrutura oferece: cada
política pode ser testada isoladamente, informa as unidades que consumiu
e uma nova oferta por grupo pode ser criada só com os ganchos do
Template Method.
"""
import pytest

from discount_policies import (
    DiscountPolicy, FiveForAmount, GroupPriceOffer, PercentageOffer, ThreeForTwo, TwoForAmount,
    create_policy,
)
from model_objects import Offer, SpecialOfferType


# Simple Factory

@pytest.mark.parametrize("tipo, argumento, classe_esperada", [
    (SpecialOfferType.THREE_FOR_TWO, None, ThreeForTwo),
    (SpecialOfferType.TEN_PERCENT_DISCOUNT, 10.0, PercentageOffer),
    (SpecialOfferType.TWO_FOR_AMOUNT, 15.0, TwoForAmount),
    (SpecialOfferType.FIVE_FOR_AMOUNT, 40.0, FiveForAmount),
])
def test_fabrica_cria_a_politica_de_cada_tipo_de_oferta(escova, tipo, argumento, classe_esperada):
    politica = create_policy(Offer(tipo, escova, argumento))

    assert isinstance(politica, classe_esperada)
    assert politica.product is escova


def test_fabrica_atende_todos_os_tipos_de_oferta(escova):
    for tipo in SpecialOfferType:
        assert isinstance(create_policy(Offer(tipo, escova, 10.0)), DiscountPolicy)


# Strategy: cada política isolada, com as unidades consumidas

def test_desconto_percentual_consome_todas_as_unidades(catalogo, escova):
    resultado = PercentageOffer(escova, 20).apply({escova: 3}, catalogo)

    assert [d.discount_amount for d in resultado.discounts] == pytest.approx([-6.00])
    assert resultado.consumed == {escova: 3}


@pytest.mark.parametrize("politica, quantidade, desconto_esperado, consumo_esperado", [
    pytest.param(lambda produto: ThreeForTwo(produto), 7, -20.00, 6, id="tres_por_dois"),
    pytest.param(lambda produto: TwoForAmount(produto, 15.0), 4, -10.00, 4, id="dois_por_valor"),
    pytest.param(lambda produto: FiveForAmount(produto, 40.0), 11, -20.00, 10, id="cinco_por_valor"),
])
def test_oferta_por_grupo_consome_so_os_grupos_completos(
        catalogo, escova, politica, quantidade, desconto_esperado, consumo_esperado):
    resultado = politica(escova).apply({escova: quantidade}, catalogo)

    assert [d.discount_amount for d in resultado.discounts] == pytest.approx([desconto_esperado])
    assert resultado.consumed == {escova: consumo_esperado}


def test_oferta_por_grupo_nao_ativada_nao_gera_desconto_nem_consome(catalogo, escova):
    resultado = ThreeForTwo(escova).apply({escova: 2}, catalogo)

    assert resultado.discounts == []
    assert resultado.consumed == {}


# Template Method: uma nova oferta por grupo só implementa os ganchos

class QuatroPorTres(GroupPriceOffer):
    """Oferta fictícia, criada só para o teste: leve 4 e pague 3."""

    def group_size(self):
        return 4

    def group_price(self, unit_price):
        return 3 * unit_price

    def description(self):
        return "4 for 3"


def test_nova_oferta_por_grupo_reaproveita_o_algoritmo_comum(catalogo, escova):
    resultado = QuatroPorTres(escova).apply({escova: 9}, catalogo)

    # 2 grupos de 4 (R$ 60,00) + 1 unidade a preço cheio (R$ 10,00) = R$ 70,00 em vez de R$ 90,00
    assert [d.description for d in resultado.discounts] == ["4 for 3"]
    assert [d.discount_amount for d in resultado.discounts] == pytest.approx([-20.00])
    assert resultado.consumed == {escova: 8}
