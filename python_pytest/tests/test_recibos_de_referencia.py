"""Recibos de referência de carrinhos variados, sem combos.

Fixam o texto completo do recibo impresso para carrinhos sem ofertas e com
cada tipo de oferta. Na Fase 6, os mesmos cenários são repetidos com combos
cadastrados para produtos que não estão nos carrinhos (shampoo e
condicionador), e o recibo deve continuar idêntico.

Os cenários evitam de propósito os defeitos DEF-01 ("2 por valor" com
quantidade ímpar) e DEF-02 (oferta por grupo ativada com quantidade
fracionária), que têm testes próprios. Assim, estes recibos continuam
válidos depois das correções.
"""
import pytest

from model_objects import SpecialOfferType
from tests.auxiliares import fechar_compra, imprimir

TRES_POR_DOIS = SpecialOfferType.THREE_FOR_TWO
DEZ_POR_CENTO = SpecialOfferType.TEN_PERCENT_DISCOUNT
DOIS_POR_VALOR = SpecialOfferType.TWO_FOR_AMOUNT
CINCO_POR_VALOR = SpecialOfferType.FIVE_FOR_AMOUNT

# Cada cenário: (ofertas, itens do carrinho, linhas do recibo impresso).
# Os produtos são indicados pelo nome da fixture (ver conftest.py).
CENARIOS = [
    pytest.param(
        [],
        [("escova", 2), ("creme_dental", 1), ("maca", 1.5)],
        [
            "escova                             20.00",
            "  10.00 * 2",
            "creme dental                       15.00",
            "maca                                3.00",
            "  2.00 * 1.500",
            "",
            "Total:                             38.00",
        ],
        id="sem_ofertas",
    ),
    pytest.param(
        [("escova", TRES_POR_DOIS, None)],
        [("escova", 7), ("creme_dental", 1)],
        [
            "escova                             70.00",
            "  10.00 * 7",
            "creme dental                       15.00",
            "3 for 2 (escova)                  -20.00",
            "",
            "Total:                             65.00",
        ],
        id="tres_por_dois",
    ),
    pytest.param(
        [("creme_dental", DEZ_POR_CENTO, 20.0)],
        [("creme_dental", 3), ("escova", 1)],
        [
            "creme dental                       45.00",
            "  15.00 * 3",
            "escova                             10.00",
            "20.0% off (creme dental)           -9.00",
            "",
            "Total:                             46.00",
        ],
        id="percentual",
    ),
    pytest.param(
        [("fio_dental", DOIS_POR_VALOR, 8.0)],
        [("fio_dental", 4), ("escova", 1)],
        [
            "fio dental                         20.00",
            "  5.00 * 4",
            "escova                             10.00",
            "2 for 8.0 (fio dental)             -4.00",
            "",
            "Total:                             26.00",
        ],
        id="dois_por_valor_com_quantidade_par",
    ),
    pytest.param(
        [("escova", CINCO_POR_VALOR, 40.0)],
        [("escova", 11), ("fio_dental", 2)],
        [
            "escova                            110.00",
            "  10.00 * 11",
            "fio dental                         10.00",
            "  5.00 * 2",
            "5 for 40.0 (escova)               -20.00",
            "",
            "Total:                            100.00",
        ],
        id="cinco_por_valor",
    ),
    pytest.param(
        [("maca", DEZ_POR_CENTO, 10.0)],
        [("maca", 2.5), ("escova", 1)],
        [
            "maca                                5.00",
            "  2.00 * 2.500",
            "escova                             10.00",
            "10.0% off (maca)                   -0.50",
            "",
            "Total:                             14.50",
        ],
        id="percentual_em_produto_por_peso",
    ),
    pytest.param(
        [
            ("escova", TRES_POR_DOIS, None),
            ("creme_dental", DEZ_POR_CENTO, 10.0),
            ("fio_dental", DOIS_POR_VALOR, 8.0),
        ],
        [("escova", 3), ("creme_dental", 2), ("fio_dental", 2), ("maca", 1.25)],
        [
            "escova                             30.00",
            "  10.00 * 3",
            "creme dental                       30.00",
            "  15.00 * 2",
            "fio dental                         10.00",
            "  5.00 * 2",
            "maca                                2.50",
            "  2.00 * 1.250",
            "3 for 2 (escova)                  -10.00",
            "10.0% off (creme dental)           -3.00",
            "2 for 8.0 (fio dental)             -2.00",
            "",
            "Total:                             57.50",
        ],
        id="varias_ofertas",
    ),
]


def fechar_compra_do_cenario(request, teller, ofertas, itens):
    """Cadastra as ofertas do cenário, monta o carrinho e devolve o recibo."""
    produto = request.getfixturevalue
    for nome, tipo, argumento in ofertas:
        teller.add_special_offer(tipo, produto(nome), argumento)
    return fechar_compra(teller, *[(produto(nome), quantidade) for nome, quantidade in itens])


@pytest.mark.parametrize("ofertas, itens, linhas_esperadas", CENARIOS)
def test_recibo_de_referencia_sem_combos(request, teller, ofertas, itens, linhas_esperadas):
    recibo = fechar_compra_do_cenario(request, teller, ofertas, itens)

    assert imprimir(recibo) == "\n".join(linhas_esperadas) + "\n"


@pytest.mark.parametrize("ofertas, itens, linhas_esperadas", CENARIOS)
def test_recibo_de_referencia_com_combo_de_outros_produtos(
        request, teller, shampoo, condicionador, ofertas, itens, linhas_esperadas):
    """Cenário 15: um combo cadastrado para produtos fora do carrinho não muda o recibo."""
    teller.add_bundle_offer([shampoo, condicionador])

    recibo = fechar_compra_do_cenario(request, teller, ofertas, itens)

    assert imprimir(recibo) == "\n".join(linhas_esperadas) + "\n"
