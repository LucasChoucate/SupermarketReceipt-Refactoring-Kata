"""Testes da promoção de combos (Fase 5).

Regra: quando o carrinho tem todos os produtos de um combo, aplica-se 10%
de desconto só sobre as unidades que formam combos completos. Preços das
fixtures: escova R$ 10,00, creme dental R$ 15,00 e fio dental R$ 5,00.
"""
import pytest

from discount_policies import BundleOffer
from model_objects import SpecialOfferType
from tests.auxiliares import fechar_compra, imprimir, total_descontos


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


# Combos no checkout: cenários do roteiro (seção 3.2)

@pytest.mark.parametrize("escovas, cremes, desconto_esperado, total_esperado", [
    pytest.param(1, 1, -2.50, 22.50, id="1_escova_1_creme"),
    pytest.param(2, 1, -2.50, 32.50, id="2_escovas_1_creme_excedente_a_preco_cheio"),
    pytest.param(2, 2, -5.00, 45.00, id="2_escovas_2_cremes_dois_combos"),
    pytest.param(1, 0, 0.0, 10.00, id="so_1_escova_combo_incompleto"),
])
def test_cenarios_do_roteiro(teller, escova, creme_dental, escovas, cremes, desconto_esperado, total_esperado):
    teller.add_bundle_offer([escova, creme_dental])

    recibo = fechar_compra(teller, (escova, escovas), (creme_dental, cremes))

    assert total_descontos(recibo) == pytest.approx(desconto_esperado)
    assert recibo.total_price() == pytest.approx(total_esperado)


def test_combo_incompleto_nao_gera_linha_de_desconto(teller, escova, creme_dental):
    teller.add_bundle_offer([escova, creme_dental])

    recibo = fechar_compra(teller, (escova, 1))

    assert recibo.discounts == []


def test_combo_que_exige_duas_unidades_do_mesmo_produto(teller, escova, creme_dental):
    teller.add_bundle_offer([escova, escova, creme_dental])

    recibo = fechar_compra(teller, (escova, 5), (creme_dental, 3))

    # 2 combos (5 // 2 escovas); 1 escova e 1 creme a preço cheio
    assert total_descontos(recibo) == pytest.approx(-7.00)
    assert recibo.total_price() == pytest.approx(95.00 - 7.00)


def test_dois_combos_disputando_o_mesmo_produto_vence_a_ordem_de_cadastro(
        teller, escova, creme_dental, fio_dental):
    teller.add_bundle_offer([escova, creme_dental])
    teller.add_bundle_offer([escova, fio_dental])

    recibo = fechar_compra(teller, (escova, 1), (creme_dental, 1), (fio_dental, 1))

    assert [d.product for d in recibo.discounts] == [escova, creme_dental]
    assert recibo.total_price() == pytest.approx(30.00 - 2.50)


def test_recibo_impresso_com_combo(teller, escova, creme_dental):
    teller.add_bundle_offer([escova, creme_dental])

    recibo = fechar_compra(teller, (escova, 2), (creme_dental, 1))

    assert imprimir(recibo) == "\n".join([
        "escova                             20.00",
        "  10.00 * 2",
        "creme dental                       15.00",
        "combo 10% off (escova)             -1.00",
        "combo 10% off (creme dental)       -1.50",
        "",
        "Total:                             32.50",
        "",
    ])


# Contrato: a API de combos é aditiva (decisão D5)

def test_add_bundle_offer_nao_altera_as_ofertas_nem_o_enum(teller, escova, creme_dental):
    teller.add_special_offer(SpecialOfferType.THREE_FOR_TWO, escova, None)
    ofertas_antes = dict(teller.offers)

    teller.add_bundle_offer([escova, creme_dental])

    assert teller.offers == ofertas_antes
    assert len(teller.bundles) == 1
    assert len(SpecialOfferType) == 4


def test_add_bundle_offer_exige_pelo_menos_um_produto(teller):
    with pytest.raises(ValueError):
        teller.add_bundle_offer([])
