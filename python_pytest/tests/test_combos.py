"""Testes da promoção de combos (Fase 5).

Regra: quando o carrinho tem todos os produtos de um combo, aplica-se 10%
de desconto só sobre as unidades que formam combos completos. Preços das
fixtures: escova R$ 10,00, creme dental R$ 15,00 e fio dental R$ 5,00.
"""
import pytest

from discount_policies import BundleOffer


# BundleOffer (estratégia isolada)

@pytest.mark.parametrize("escovas, cremes, combos", [
    pytest.param(1, 1, 1, id="combo_completo"),
    pytest.param(2, 1, 1, id="escova_excedente"),
    pytest.param(2, 2, 2, id="dois_combos"),
    pytest.param(1, 0, 0, id="combo_incompleto"),
])
def test_combo_desconta_10_por_cento_so_dos_combos_completos(catalogo, escova, creme_dental, escovas, cremes, combos):
    combo = BundleOffer({escova: 1, creme_dental: 1})

    resultado = combo.apply({escova: escovas, creme_dental: cremes}, catalogo)

    assert sum(d.discount_amount for d in resultado.discounts) == pytest.approx(-2.50 * combos)
    if combos:
        assert [(d.product, d.description) for d in resultado.discounts] == [
            (escova, "combo 10% off"), (creme_dental, "combo 10% off")]
        assert resultado.consumed == {escova: combos, creme_dental: combos}
    else:
        assert resultado.discounts == []
        assert resultado.consumed == {}


def test_combo_com_mais_de_uma_unidade_do_mesmo_produto(catalogo, escova, creme_dental):
    combo = BundleOffer({escova: 2, creme_dental: 1})

    resultado = combo.apply({escova: 5, creme_dental: 3}, catalogo)

    # 2 combos: limitados pelas escovas (5 // 2); desconto = 10% de 2 x (2 x 10 + 15)
    assert resultado.consumed == {escova: 4, creme_dental: 2}
    assert sum(d.discount_amount for d in resultado.discounts) == pytest.approx(-7.00)


def test_combo_usa_so_a_parte_inteira_de_produto_por_peso(catalogo, maca, escova):
    combo = BundleOffer({maca: 1, escova: 1})

    resultado = combo.apply({maca: 2.5, escova: 3}, catalogo)

    assert resultado.consumed == {maca: 2, escova: 2}


def test_percentual_do_combo_pode_ser_informado(catalogo, escova, creme_dental):
    combo = BundleOffer({escova: 1, creme_dental: 1}, percent=20)

    resultado = combo.apply({escova: 1, creme_dental: 1}, catalogo)

    assert sum(d.discount_amount for d in resultado.discounts) == pytest.approx(-5.00)
    assert {d.description for d in resultado.discounts} == {"combo 20% off"}
