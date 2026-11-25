# Supermarket Receipt: Modernização de Sistema Legado

Trabalho prático da disciplina **Alta Qualidade de Software**, ministrada pelo professor Leonardo Cardia.

## Sumário

1. [Objetivo](#1-objetivo)
2. [Integrantes](#2-integrantes)
3. [Requisitos de ambiente](#3-requisitos-de-ambiente)
4. [Instalação](#4-instalação)
5. [Testes e cobertura](#5-testes-e-cobertura)
6. [Exemplo de uso](#6-exemplo-de-uso)
7. [Análise de segurança](#7-análise-de-segurança)
8. [Estrutura de pastas e documentos](#8-estrutura-de-pastas-e-documentos)
9. [Créditos e licença](#créditos-e-licença)

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

## 7. Análise de segurança

O código e as dependências foram analisados com três ferramentas, antes da modernização (tag `legado-baseline`) e depois dela:

| Ferramenta | O que analisa |
|---|---|
| **Bandit** | O código-fonte de `python_pytest/src/`, em busca de padrões de implementação inseguros |
| **pip-audit** | As dependências do `requirements.txt`, comparadas com a base pública de vulnerabilidades do PyPI e do OSV |
| **Safety** | As dependências do `requirements.txt` e o ambiente virtual do projeto, comparados com a base da Safety |

A análise completa, com a triagem de cada alerta, está em [`docs/seguranca_antes_depois.md`](docs/seguranca_antes_depois.md). Esta seção mostra como reproduzi-la e resume os resultados.

### 7.1 Ambiente separado para as ferramentas

As ferramentas ficam em um ambiente virtual próprio, **fora do repositório** (`../.venv-audit`), e não no `.venv` do projeto. Na primeira auditoria do grupo, elas foram instaladas no ambiente do projeto, e o `filelock`, que é dependência do próprio Safety, apareceu com 13 vulnerabilidades como se fosse do sistema auditado (alerta A-04). Com o ambiente separado, as ferramentas não contaminam o resultado e nenhuma dependência entra no projeto só por causa da auditoria.

Os comandos desta seção são executados na **raiz do repositório**, e não em `python_pytest/`. As versões são as mesmas da análise registrada.

Linux e macOS:

```bash
python3 -m venv ../.venv-audit
../.venv-audit/bin/python -m pip install bandit==1.9.4 pip-audit==2.10.1 safety==3.8.1
```

Windows:

```powershell
python -m venv ..\.venv-audit
..\.venv-audit\Scripts\python.exe -m pip install bandit==1.9.4 pip-audit==2.10.1 safety==3.8.1
```

### 7.2 Execução

Rode depois da instalação da [seção 4](#4-instalação), porque o Safety também analisa o ambiente `python_pytest/.venv`.

Linux e macOS:

```bash
../.venv-audit/bin/bandit -r python_pytest/src
../.venv-audit/bin/pip-audit -r python_pytest/requirements.txt
../.venv-audit/bin/safety auth login
../.venv-audit/bin/safety scan --target python_pytest
```

Windows:

```powershell
..\.venv-audit\Scripts\bandit.exe -r python_pytest/src
..\.venv-audit\Scripts\pip-audit.exe -r python_pytest/requirements.txt
..\.venv-audit\Scripts\safety.exe auth login
..\.venv-audit\Scripts\safety.exe scan --target python_pytest
```

Resultado esperado: o Bandit informa `No issues identified`, o pip-audit informa `No known vulnerabilities found` e o Safety não aponta nenhuma vulnerabilidade.

Observações:

- **Escopo do Bandit.** Só o código de produção (`src/`) é analisado. Em `tests/`, o Bandit aponta 86 usos de `assert` (B101), que são esperados, porque o `assert` é o mecanismo de verificação do pytest (alerta A-05).
- **pip-audit e internet.** O pip-audit instala as dependências do `requirements.txt` em um ambiente temporário para auditá-las, por isso precisa de acesso à internet.
- **O Safety exige conta.** Sem login, o `safety scan` só pergunta se você quer criar uma conta ou entrar em uma existente. O `safety auth login` abre o navegador para criar uma conta gratuita na Safety Platform ou entrar nela. Em terminais sem navegador, como o WSL ou uma sessão SSH, use `safety auth login --headless` e abra o endereço exibido em outro navegador. Na primeira execução, o `safety scan` pergunta se o projeto deve ser vinculado à conta e grava a resposta em `python_pytest/.safety-project.ini`, que o Git ignora. Ao iniciar, o Safety 3.8.1 exibe avisos de depreciação (`AuthlibDeprecationWarning`), que não afetam o resultado.
- **A política do Safety fica na conta.** As regras que ignoram certas ocorrências vêm da configuração da conta, e não de um arquivo do repositório. Outra conta pode ter outra política e, portanto, outro resultado.
- **Os resultados mudam com o tempo.** As bases de vulnerabilidades são atualizadas continuamente, então uma execução futura pode apontar vulnerabilidades novas nas mesmas versões.
- **Evidências oficiais.** Os comandos acima mostram o resultado no terminal. Os relatórios registrados ficam em [`docs/evidencias/seguranca/`](docs/evidencias/seguranca/) e foram gerados com os comandos da [seção 2.3 do documento de segurança](docs/seguranca_antes_depois.md#23-comandos-executados). Não grave a saída nessas pastas, para não sobrescrever as evidências.

### 7.3 Resultados antes e depois

| Ferramenta | Antes (`legado-baseline`) | Depois |
|---|---|---|
| Bandit | 0 ocorrências em 5 arquivos e 133 linhas | 0 ocorrências em 7 arquivos e 349 linhas |
| pip-audit | 0 vulnerabilidades em 22 pacotes | 0 vulnerabilidades em 6 pacotes |
| Safety | 3 ocorrências, ignoradas pela política da conta: `pytest` sem versão fixada (A-01) e duas no `pip` 26.1.2 do ambiente (A-02 e A-03) | 0 ocorrências |

| Ação | Efeito |
|---|---|
| Fixar as versões no `requirements.txt` (`pytest==9.2.0` e `coverage==7.6.12`) | Resolveu o A-01 e tornou a instalação reproduzível |
| Remover o `approvaltests` e o `pytest-approvaltests`, que nenhum teste usava (decisão D7) | Os pacotes auditados caíram de 22 para 6 |
| Atualizar o `pip` do ambiente do projeto (passo da [seção 4.2](#42-criar-o-ambiente-virtual-e-instalar-as-dependências)) | Resolveu o A-02 e o A-03 |
| Isolar as ferramentas em `../.venv-audit` | Eliminou o falso positivo do `filelock` (A-04) |

Ressalvas:

- **Um alerta não é, por si só, uma vulnerabilidade explorável.** Cada ocorrência foi investigada quanto à origem, à versão e ao contexto. Nenhuma afetava o código de produção: todas estavam em ferramentas de desenvolvimento ou no ambiente.
- **A ausência de alertas não prova que o sistema é seguro.** O Bandit procura padrões conhecidos de código inseguro e não detecta erros de lógica de negócio, como os defeitos DEF-01 e DEF-02. O pip-audit e o Safety só conhecem as vulnerabilidades já publicadas nas suas bases.
- **Nenhuma dependência foi adicionada para gerar resultados nas ferramentas.**
- **Risco remanescente:** os valores monetários continuam em `float`, mantido para não alterar os valores observados (RNF09). Os riscos e as limitações estão na [seção 10 do documento de segurança](docs/seguranca_antes_depois.md#10-riscos-remanescentes-e-limitações).

---

## 8. Estrutura de pastas e documentos

```text
.
├── README.md                        este documento
├── license.txt                      licença MIT do kata original
├── apresentacao/                    slides da apresentação
├── docs/
│   ├── diagnostico_tecnico.md       code smells, SOLID e defeitos do legado
│   ├── registro_de_defeitos.md      DEF-01 a DEF-03: causa, impacto e correção
│   ├── requisitos.md                RF, RNF, critérios de aceitação e rastreabilidade
│   ├── plano_contingencia.md        riscos, invariantes, interfaces e reversão
│   ├── plano_de_execucao.md         fases do trabalho, passo a passo
│   ├── padroes_projeto.md           padrões, diagramas antes e depois e SOLID
│   ├── seguranca_antes_depois.md    Bandit, pip-audit e Safety: triagem e comparação
│   ├── evidencias_testes.md         evolução da suíte e comparação antes e depois
│   └── evidencias/
│       ├── pytest_antes_ubuntu.log  os 57 testes de caracterização iniciais
│       ├── testes/                  logs do pytest e cobertura de cada fase
│       └── seguranca/
│           ├── antes/               relatórios na tag legado-baseline
│           └── depois/              relatórios após a modernização
└── python_pytest/                   estrutura original do kata, preservada
    ├── README.md                    descrição original da versão Python do kata
    ├── requirements.txt             pytest e coverage, com versões fixadas
    ├── pytest.ini                   inclui src/ e tests/ no caminho de importação
    ├── exemplo_de_uso.py            recibo de exemplo, fora do pytest (seção 6)
    ├── src/                         código de produção
    │   ├── catalog.py               contrato do catálogo de produtos
    │   ├── discount_engine.py       aplica ofertas e combos na ordem de menor total
    │   ├── discount_policies.py     estratégias de desconto, combos e fábrica
    │   ├── model_objects.py         produtos, ofertas e descontos
    │   ├── receipt.py               recibo: itens, descontos e total
    │   ├── shopping_cart.py         carrinho de compras
    │   └── teller.py                caixa: ofertas, combos e checkout
    └── tests/                       118 testes e arquivos de apoio (seção 5)
```

A estrutura sugerida na seção 7 do edital é ilustrativa. A pasta original do kata (`python_pytest/`) foi preservada, para manter a compatibilidade com a execução e os testes, e os arquivos de teste sugeridos (`test_comportamento_legado.py` e `test_combos.py`) existem com esses nomes. Os documentos estão em Markdown, que o GitHub exibe formatado e cujas mudanças ficam visíveis no histórico.

Onde está cada entregável do edital:

| Entregável | Onde está |
|---|---|
| 5.1 Relatório de diagnóstico técnico | [`docs/diagnostico_tecnico.md`](docs/diagnostico_tecnico.md). Os defeitos encontrados estão detalhados em [`docs/registro_de_defeitos.md`](docs/registro_de_defeitos.md) |
| 5.2 Documento de requisitos | [`docs/requisitos.md`](docs/requisitos.md) |
| 5.3 Plano de contingência e refatoração | [`docs/plano_contingencia.md`](docs/plano_contingencia.md). A execução, fase a fase, está em [`docs/plano_de_execucao.md`](docs/plano_de_execucao.md) |
| 5.4 Código refatorado | [`python_pytest/src/`](python_pytest/src/) |
| 5.5 Padrões de projeto | [`docs/padroes_projeto.md`](docs/padroes_projeto.md) |
| 5.6 Promoção de combos | `BundleOffer` em [`discount_policies.py`](python_pytest/src/discount_policies.py), `Teller.add_bundle_offer` em [`teller.py`](python_pytest/src/teller.py) e a convivência com as ofertas em [`discount_engine.py`](python_pytest/src/discount_engine.py). Testes em [`test_combos.py`](python_pytest/tests/test_combos.py) |
| 5.7 Testes automatizados | [`python_pytest/tests/`](python_pytest/tests/), descritos na [seção 5](#5-testes-e-cobertura) |
| 5.8 Análise de segurança | [`docs/seguranca_antes_depois.md`](docs/seguranca_antes_depois.md) e [`docs/evidencias/seguranca/`](docs/evidencias/seguranca/) |
| 5.9 Evidências, README e organização | Este README, [`docs/evidencias_testes.md`](docs/evidencias_testes.md) e [`docs/evidencias/`](docs/evidencias/) |
| 5.10 Apresentação | [`apresentacao/`](apresentacao/) |

---

## Créditos e licença

Este trabalho parte do [Supermarket Receipt Refactoring Kata](https://github.com/emilybache/SupermarketReceipt-Refactoring-Kata), criado por Emily Bache e distribuído sob a licença MIT, cujo texto está em [`license.txt`](license.txt). O enunciado original do kata está no repositório de origem, e a descrição da versão Python, em [`python_pytest/README.md`](python_pytest/README.md).
