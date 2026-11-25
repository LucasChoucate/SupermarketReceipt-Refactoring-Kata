# Supermarket Receipt: Modernização de Sistema Legado

Trabalho prático da disciplina **Alta Qualidade de Software**, ministrada pelo professor Leonardo Cardia.

## Sumário

1. [Objetivo](#1-objetivo)
2. [Integrantes](#2-integrantes)
3. [Requisitos de ambiente](#3-requisitos-de-ambiente)
4. [Instalação](#4-instalação)
5. [Créditos e licença](#créditos-e-licença)

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

## Créditos e licença

Este trabalho parte do [Supermarket Receipt Refactoring Kata](https://github.com/emilybache/SupermarketReceipt-Refactoring-Kata), criado por Emily Bache e distribuído sob a licença MIT, cujo texto está em [`license.txt`](license.txt). O enunciado original do kata está no repositório de origem, e a descrição da versão Python, em [`python_pytest/README.md`](python_pytest/README.md).
