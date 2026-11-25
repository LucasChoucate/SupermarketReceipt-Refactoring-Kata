# Supermarket Receipt: Modernização de Sistema Legado

Trabalho prático da disciplina **Alta Qualidade de Software**, ministrada pelo professor Leonardo Cardia.

## Sumário

1. [Objetivo](#1-objetivo)
2. [Integrantes](#2-integrantes)
3. [Requisitos de ambiente](#3-requisitos-de-ambiente)
4. [Instalação](#4-instalação)
5. [Testes e cobertura](#5-testes-e-cobertura)
6. [Exemplo de uso](#6-exemplo-de-uso)
7. [Créditos e licença](#créditos-e-licença)

---

## 1. Objetivo

O Supermarket Receipt é um sistema legado que registra as compras de um supermercado, calcula preços e ofertas e emite o recibo. A equipe atuou como uma consultoria técnica contratada para modernizá-lo de forma incremental, sem alterar indevidamente o comportamento existente, e para implementar uma nova regra de negócio: **combos promocionais**, com 10% de desconto sobre os itens que formam combos completos.

O trabalho partiu da versão `python_pytest` do kata original, marcada neste repositório pela tag `legado-baseline`, e seguiu estas etapas:

1. **Diagnóstico técnico:** code smells, violações de SOLID e defeitos do legado, com os trechos de código correspondentes.
2. **Requisitos e plano de contingência:** requisitos funcionais e não funcionais com critérios de aceitação, riscos, invariantes de negócio e estratégia de reversão.
3. **Testes de caracterização:** uma suíte que fixou o comportamento existente antes de qualquer alteração no código.
4. **Refatoração com padrões de projeto:** Strategy, Template Method e Simple Factory, preservando as interfaces públicas.
5. **Correção de defeitos:** três defeitos do legado, corrigidos em commits isolados e documentados.
6. **Combos promocionais:** a nova modalidade de desconto, que convive com as ofertas existentes sem desconto duplicado.
7. **Análise de segurança:** Bandit, pip-audit e Safety, executados antes e depois da modernização.

---

## 2. Integrantes

- Felipe Nogueira
- Lucas Choucate
- Júlia Gaglianone
- Ramon Papes
- Suianne Martins

---

## 3. Requisitos de ambiente

| Item | Requisito |
|---|---|
| Python | **3.10 ou superior**, a versão mínima exigida pelo `pytest` 9.2.0 |
| Sistema operacional | Qualquer um que rode o Python 3.10 ou superior: Linux, macOS ou Windows |
| Git | Necessário para clonar o repositório |

O código de produção (`python_pytest/src/`) usa só a biblioteca padrão do Python. O `requirements.txt` declara apenas as ferramentas de teste, com as versões fixadas: `pytest` 9.2.0 e `coverage` 7.6.12.

Ambientes em que a suíte foi executada:

| Sistema operacional | Python | Resultado | Evidência |
|---|---|---|---|
| Linux | 3.14.6 | Todas as fases, da execução original aos combos | Logs [`01`](docs/evidencias/testes/01_pytest_inicial.log) a [`05`](docs/evidencias/testes/05_pytest_apos_combos.log) |
| Windows | 3.12.5 | 118 aprovados | [`06_pytest_final.log`](docs/evidencias/testes/06_pytest_final.log) |

---

## 4. Instalação

Depois de clonar o repositório, todos os comandos desta seção são executados na pasta `python_pytest/`.

### 4.1 Obter o código

```bash
git clone https://github.com/LucasChoucate/SupermarketReceipt-Refactoring-Kata.git
cd SupermarketReceipt-Refactoring-Kata/python_pytest
```

### 4.2 Criar o ambiente virtual e instalar as dependências

Linux e macOS:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
```

Windows (PowerShell ou Prompt de Comando):

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Observações:

- **Nome do interpretador.** Use o comando que chama o Python 3.10 ou superior na sua máquina: em geral, `python3` no Linux e no macOS, e `python` ou o inicializador `py` no Windows. Confira a versão com `python3 --version` ou `python --version`. No macOS, o `python3` instalado com as Command Line Tools pode ser anterior ao 3.10; nesse caso, instale uma versão mais nova pelo [python.org](https://www.python.org/downloads/) ou pelo Homebrew.
- **Atualização do `pip`.** Versões do `pip` anteriores à 26.2.2 têm vulnerabilidades conhecidas (alertas A-02 e A-03 da [análise de segurança](docs/seguranca_antes_depois.md#6-classificação-dos-alertas)). Por isso o `pip` do ambiente é atualizado antes da instalação.
- **Sem ativar o ambiente.** Os comandos chamam o Python do ambiente virtual pelo caminho (`.venv/bin/python` ou `.venv\Scripts\python.exe`). Assim eles funcionam em qualquer terminal, inclusive no PowerShell com a política de execução padrão do Windows, que bloqueia o script de ativação. Quem preferir pode ativar o ambiente (`source .venv/bin/activate` ou `.venv\Scripts\Activate.ps1`) e usar só `python`.

### 4.3 Conferir a instalação

Linux e macOS:

```bash
.venv/bin/python -m pytest -q
```

Windows:

```powershell
.venv\Scripts\python.exe -m pytest -q
```

O resultado esperado é `118 passed`.

---

## 5. Testes e cobertura

Os comandos são executados na pasta `python_pytest/`, com o ambiente da [seção 4](#4-instalação) instalado.

Linux e macOS:

```bash
.venv/bin/python -m pytest -v
.venv/bin/python -m coverage run --branch --source=src -m pytest -q
.venv/bin/python -m coverage report -m
```

Windows:

```powershell
.venv\Scripts\python.exe -m pytest -v
.venv\Scripts\python.exe -m coverage run --branch --source=src -m pytest -q
.venv\Scripts\python.exe -m coverage report -m
```

O resultado esperado é **118 testes aprovados** e **99% de cobertura** de linhas e ramos em `src/`. As 3 linhas não cobertas ficam em `catalog.py`: são os métodos de `SupermarketCatalog`, que representam o acesso a um banco de dados fora do kata e só lançam uma exceção. Nos testes, eles são substituídos por um catálogo em memória. Para ver a cobertura linha a linha no navegador, gere o relatório em HTML (`.venv/bin/python -m coverage html` ou `.venv\Scripts\python.exe -m coverage html`) e abra o arquivo `htmlcov/index.html`.

| Arquivo em `tests/` | Testes | O que verifica |
|---|---|---|
| `test_supermarket.py` | 1 | O teste original do kata |
| `test_comportamento_legado.py` | 53 | Caracterização do legado: carrinho, cada oferta e seus limites, ofertas combinadas, recibo impresso e contratos das interfaces públicas |
| `test_recibos_de_referencia.py` | 14 | Texto completo do recibo de 7 carrinhos de referência, sem combos e com um combo de outros produtos cadastrado, que não pode alterar o recibo |
| `test_defeitos_corrigidos.py` | 8 | Comportamento corrigido dos defeitos DEF-01, DEF-02 e DEF-03 |
| `test_politicas_de_desconto.py` | 11 | Testes unitários das estratégias de desconto, do Template Method e da fábrica |
| `test_combos.py` | 31 | Regra dos combos: cenários do enunciado, excedentes, múltiplos combos, convivência com as ofertas e recibo |

Os demais arquivos da pasta dão suporte aos testes: `conftest.py` (produtos e preços usados nos cenários), `fake_catalog.py` (catálogo em memória), `receipt_printer.py` (impressão do recibo) e `auxiliares.py` (montagem de carrinhos).

A evolução da suíte em cada fase do trabalho, com os logs e os relatórios de cobertura, está em [`docs/evidencias_testes.md`](docs/evidencias_testes.md).

---

## 6. Exemplo de uso

O sistema não tem uma interface própria: ele é usado por outro código, como fazem os testes. O script [`exemplo_de_uso.py`](python_pytest/exemplo_de_uso.py) mostra esse uso fora do pytest. Ele cadastra três produtos, uma oferta de 20% na maçã e um combo de escova com creme dental, monta um carrinho e imprime o recibo.

Na pasta `python_pytest/`:

Linux e macOS:

```bash
.venv/bin/python exemplo_de_uso.py
```

Windows:

```powershell
.venv\Scripts\python.exe exemplo_de_uso.py
```

Saída esperada:

```text
escova                             20.00
  10.00 * 2
creme dental                       15.00
maca                                3.00
  2.00 * 1.500
20.0% off (maca)                   -0.60
combo 10% off (escova)             -1.00
combo 10% off (creme dental)       -1.50

Total:                             34.90
```

Como o recibo é calculado:

- **Combo:** o carrinho tem 2 escovas e 1 creme dental, o que forma 1 combo completo. O desconto é de 10% sobre R$ 25,00 (R$ 10,00 + R$ 15,00), dividido em uma linha por produto: −1,00 na escova e −1,50 no creme dental. A segunda escova não completa outro combo e é cobrada a preço cheio.
- **Oferta individual:** 1,5 kg de maçã a R$ 2,00/kg com 20% de desconto: −0,60.
- **Total:** 20,00 + 15,00 + 3,00 − 0,60 − 2,50 = 34,90.

O exemplo usa o catálogo em memória e a impressora de recibos de `tests/`, porque o catálogo real acessa um banco de dados que não faz parte do kata. O próprio script inclui `src/` e `tests/` no caminho de importação, então funciona da mesma forma em qualquer sistema operacional.

---

## Créditos e licença

Este trabalho parte do [Supermarket Receipt Refactoring Kata](https://github.com/emilybache/SupermarketReceipt-Refactoring-Kata), criado por Emily Bache e distribuído sob a licença MIT, cujo texto está em [`license.txt`](license.txt). O enunciado original do kata está no repositório de origem, e a descrição da versão Python, em [`python_pytest/README.md`](python_pytest/README.md).
