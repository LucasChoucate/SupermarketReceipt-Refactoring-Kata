# Evidências de Testes

## Sumário

1. [Objetivo](#1-objetivo)
2. [Como reproduzir](#2-como-reproduzir)
3. [Evolução da suíte por fase](#3-evolução-da-suíte-por-fase)
4. [Comparação antes e depois](#4-comparação-antes-e-depois)
5. [Regressão](#5-regressão)
6. [Casos alterados de propósito](#6-casos-alterados-de-propósito)
7. [Limitações](#7-limitações)

---

## 1. Objetivo

Este documento reúne as evidências de que a refatoração e a inclusão dos combos preservaram o comportamento do legado. A suíte de caracterização foi escrita antes de qualquer alteração em `src/` e continuou rodando a cada fase. Os únicos valores esperados que mudaram são os de DEF-01 e DEF-02, listados na [seção 6](#6-casos-alterados-de-propósito).

Os logs estão em [`evidencias/testes/`](evidencias/testes/). O ambiente de cada execução aparece nas primeiras linhas do próprio log (sistema, versão do Python e do pytest).

## 2. Como reproduzir

A partir da pasta `python_pytest`, com as dependências do `requirements.txt` instaladas:

```bash
python -m pytest -v -p no:cacheprovider
python -m coverage run --branch --source=src -m pytest -q -p no:cacheprovider
python -m coverage report -m
```

A instalação do ambiente e os comandos para cada sistema operacional estão nas seções [4](../README.md#4-instalação) e [5](../README.md#5-testes-e-cobertura) do README.

## 3. Evolução da suíte por fase

| Fase | Situação do código | Resultado | Cobertura (linhas e ramos) | Log |
|---|---|---|---|---|
| Original | Código do kata | 1 aprovado | n/d | [`01_pytest_inicial.log`](evidencias/testes/01_pytest_inicial.log) |
| Caracterização | Legado, antes de refatorar | 64 aprovados e 7 `xfail` (comportamento correto dos defeitos) | 99% | [`02_pytest_antes_da_refatoracao.log`](evidencias/testes/02_pytest_antes_da_refatoracao.log) |
| Refatoração | Padrões de projeto, legado preservado | 79 aprovados e 7 `xfail` | 99% | [`03_pytest_apos_refatoracao.log`](evidencias/testes/03_pytest_apos_refatoracao.log) |
| Correção dos defeitos | DEF-01, DEF-02 e DEF-03 corrigidos | 80 aprovados, 0 `xfail` | 99% | [`04_pytest_apos_correcoes.log`](evidencias/testes/04_pytest_apos_correcoes.log) |
| Combos | `add_bundle_offer` implementado | 109 aprovados | 99% | [`05_pytest_apos_combos.log`](evidencias/testes/05_pytest_apos_combos.log) |
| Regressão | Cenário 15 incluído | **118 aprovados** | **99%** | [`06_pytest_final.log`](evidencias/testes/06_pytest_final.log) |
| Execução independente | Mesmo código, em um clone limpo, seguindo só os comandos do README, com o Python 3.10, 3.11, 3.12, 3.13 e 3.14 | 118 aprovados em cada versão | 99% em cada versão | [`07_execucao_independente.log`](evidencias/testes/07_execucao_independente.log) |

O arquivo [`pytest_antes_ubuntu.log`](evidencias/pytest_antes_ubuntu.log) registra os 57 testes de caracterização no momento em que foram criados.

Cobertura final por módulo ([`06_cobertura_final.txt`](evidencias/testes/06_cobertura_final.txt)):

| Módulo | Cobertura |
|---|---|
| `discount_engine.py`, `discount_policies.py`, `model_objects.py`, `receipt.py`, `shopping_cart.py`, `teller.py` | 100% |
| `catalog.py` | 57% (3 linhas) |
| **Total** | **99%** |

As 3 linhas não cobertas de `catalog.py` são os corpos dos métodos abstratos de `SupermarketCatalog`. Eles não têm lógica e só são executados por quem implementa o contrato.

## 4. Comparação antes e depois

| Métrica | Legado (início) | Depois |
|---|---|---|
| Testes | 1 (original) / 57 (caracterização) | 118 |
| Aprovados | 57 | 118 |
| Cobertura de ramos (`src/`) | 99% | 99% |
| Casos alterados de propósito | n/d | 7 (DEF-01: 3; DEF-02: 4) |
| Testes novos de defeitos | n/d | 1 (DEF-03) |
| Defeitos corrigidos | 0 de 3 | 3 de 3 |

## 5. Regressão

A regressão responde a uma pergunta: o que o sistema fazia antes dos combos continua igual depois deles? Três grupos de testes respondem a ela.

| Grupo | Arquivo | O que verifica |
|---|---|---|
| Caracterização | `test_comportamento_legado.py` | Carrinhos sem ofertas, escopo e limites de cada oferta, várias ofertas no mesmo carrinho, recibo impresso e contratos públicos. Rodam sem alteração, exceto os casos da [seção 6](#6-casos-alterados-de-propósito) |
| Recibos de referência | `test_recibos_de_referencia.py` | O texto completo do recibo de 7 carrinhos, sem ofertas e com cada tipo de oferta |
| Combos | `test_combos.py` | Um combo cadastrado nunca encarece o carrinho, e um carrinho sem combo completo gera recibo idêntico ao de um sistema sem combos |

**Cenário 15.** Os 7 recibos de referência são repetidos com um combo de shampoo e condicionador cadastrado (`test_recibo_de_referencia_com_combo_de_outros_produtos`). Esses produtos não estão nos carrinhos, então o texto do recibo deve ser exatamente o mesmo. Os 7 casos passaram.

## 6. Casos alterados de propósito

Todos têm justificativa no [registro de defeitos](registro_de_defeitos.md#4-impacto-nos-testes-de-caracterização). Cada correção foi precedida de um teste `xfail(strict=True)` do comportamento correto.

| Defeito | Cenário | Legado | Corrigido | Casos |
|---|---|---|---|---|
| DEF-01 | "2 por 15,00" com 3, 5 e 7 unidades a R$ 10,00 | total 32,50; 47,50; 62,50 | total 25,00; 40,00; 55,00 | 3 |
| DEF-02 | Ofertas por grupo com fração de produto por peso (3 casos) e recibo impresso com maçã (1 caso) | descontos maiores que o anunciado | fração cobrada a preço cheio | 4 |
| DEF-03 | `Teller.product_with_name` com catálogo que só cumpre o contrato | falha | funciona | 1 teste novo |

## 7. Limitações

- A suíte exercita o comportamento dos exemplos escolhidos. A cobertura de 99% mostra que todo o código foi executado, não que todo caso possível foi testado.
- Os valores monetários continuam em `float`. Os testes usam `pytest.approx` e o texto do recibo com 2 casas decimais.
- Os logs 01 a 05 foram gerados em Linux (Ubuntu), o log 06 em Windows e o log 07 em Ubuntu 24.04, com cinco versões do Python. A comparação entre eles vale pelas contagens de testes e pela cobertura, não pelo tempo de execução.
- O número de comandos que o `coverage` conta em `src/` muda com a versão do Python: 236 no Python 3.14 e 238 nas versões 3.10 a 3.13. As linhas não cobertas são as mesmas 3 de `catalog.py`, e a cobertura é de 99% em todas as versões.
