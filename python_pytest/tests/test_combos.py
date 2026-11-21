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


# Convivência entre combos e ofertas individuais (decisão D1, RF16)
# O carrinho é calculado nas duas ordens (ofertas primeiro e combos primeiro)
# e fica o menor total, comparado em centavos; em empate, vencem as ofertas.

TRES_POR_DOIS = SpecialOfferType.THREE_FOR_TWO
PERCENTUAL = SpecialOfferType.TEN_PERCENT_DISCOUNT
DOIS_POR_VALOR = SpecialOfferType.TWO_FOR_AMOUNT
CINCO_POR_VALOR = SpecialOfferType.FIVE_FOR_AMOUNT


@pytest.mark.parametrize("oferta, argumento, escovas, cremes, total_esperado, descricoes_esperadas", [
    pytest.param(TRES_POR_DOIS, None, 3, 1, 35.00, ["3 for 2"],
                 id="oferta_vence_3_por_2"),
    pytest.param(PERCENTUAL, 20.0, 1, 1, 22.50, ["combo 10% off", "combo 10% off"],
                 id="combo_vence_percentual_de_20"),
    pytest.param(CINCO_POR_VALOR, 40.0, 5, 5, 112.50, ["combo 10% off", "combo 10% off"],
                 id="combo_vence_5_por_valor"),
    pytest.param(DOIS_POR_VALOR, 15.0, 2, 2, 45.00, ["2 for 15.0"],
                 id="empate_mantem_a_oferta"),
])
def test_escolhe_a_ordem_de_menor_total(
        teller, escova, creme_dental, oferta, argumento, escovas, cremes, total_esperado, descricoes_esperadas):
    teller.add_special_offer(oferta, escova, argumento)
    teller.add_bundle_offer([escova, creme_dental])

    recibo = fechar_compra(teller, (escova, escovas), (creme_dental, cremes))

    assert recibo.total_price() == pytest.approx(total_esperado)
    assert [d.description for d in recibo.discounts] == descricoes_esperadas


def test_oferta_de_produto_fora_do_combo_nao_e_afetada(teller, escova, creme_dental, fio_dental):
    teller.add_special_offer(TRES_POR_DOIS, fio_dental, None)
    teller.add_bundle_offer([escova, creme_dental])

    recibo = fechar_compra(teller, (escova, 1), (creme_dental, 1), (fio_dental, 3))

    assert [(d.product, d.description) for d in recibo.discounts] == [
        (fio_dental, "3 for 2"), (escova, "combo 10% off"), (creme_dental, "combo 10% off")]
    assert recibo.total_price() == pytest.approx(40.00 - 5.00 - 2.50)


def test_combo_vencedor_nao_deixa_linha_vazia_da_oferta_substituida(teller, escova, creme_dental, fio_dental):
    teller.add_special_offer(PERCENTUAL, escova, 20.0)
    teller.add_special_offer(TRES_POR_DOIS, fio_dental, None)
    teller.add_bundle_offer([escova, creme_dental])

    recibo = fechar_compra(teller, (escova, 1), (creme_dental, 1), (fio_dental, 3))

    # Combos primeiro é mais barato (R$ 32,50 contra R$ 33,00). O combo consome
    # a única escova, então a oferta de 20% não gera linha de desconto 0,00.
    # No recibo, os descontos individuais vêm antes dos de combo.
    assert [(d.product, d.description) for d in recibo.discounts] == [
        (fio_dental, "3 for 2"), (escova, "combo 10% off"), (creme_dental, "combo 10% off")]
    assert recibo.total_price() == pytest.approx(32.50)


def test_combo_usa_as_unidades_que_sobram_da_oferta(teller, escova, creme_dental):
    teller.add_special_offer(TRES_POR_DOIS, escova, None)
    teller.add_bundle_offer([escova, creme_dental])

    recibo = fechar_compra(teller, (escova, 4), (creme_dental, 1))

    # "3 por 2" nas 3 primeiras escovas (-10,00); a 4ª forma combo com o creme (-2,50)
    assert [d.description for d in recibo.discounts] == ["3 for 2", "combo 10% off", "combo 10% off"]
    assert recibo.total_price() == pytest.approx(55.00 - 12.50)


OFERTAS_NA_ESCOVA = [
    (None, None),
    (TRES_POR_DOIS, None),
    (PERCENTUAL, 20.0),
    (DOIS_POR_VALOR, 15.0),
    (CINCO_POR_VALOR, 40.0),
]


@pytest.mark.parametrize("oferta, argumento", OFERTAS_NA_ESCOVA)
def test_cadastrar_um_combo_nunca_encarece_o_carrinho(catalogo, escova, creme_dental, oferta, argumento):
    from teller import Teller

    for escovas in range(0, 8):
        for cremes in range(0, 4):
            sem_combo, com_combo = Teller(catalogo), Teller(catalogo)
            for teller in (sem_combo, com_combo):
                if oferta:
                    teller.add_special_offer(oferta, escova, argumento)
            com_combo.add_bundle_offer([escova, creme_dental])
            itens = ((escova, escovas), (creme_dental, cremes))

            recibo_sem = fechar_compra(sem_combo, *itens)
            recibo_com = fechar_compra(com_combo, *itens)

            assert round(recibo_com.total_price(), 2) <= round(recibo_sem.total_price(), 2)
            if not (escovas and cremes):
                # sem combo completo, o recibo é idêntico ao do carrinho sem combos
                assert imprimir(recibo_com) == imprimir(recibo_sem)
