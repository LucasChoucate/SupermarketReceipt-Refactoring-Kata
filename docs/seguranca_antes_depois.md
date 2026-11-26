# Análise de Segurança: Antes e Depois da Modernização

## Sumário

1. [Objetivo e ressalvas](#1-objetivo-e-ressalvas)
2. [Ambiente e reprodutibilidade](#2-ambiente-e-reprodutibilidade)
3. [Escopo de cada ferramenta](#3-escopo-de-cada-ferramenta)
4. [Resultados antes da modernização](#4-resultados-antes-da-modernização)
5. [Triagem da auditoria anterior (`filelock`)](#5-triagem-da-auditoria-anterior-filelock)
6. [Classificação dos alertas](#6-classificação-dos-alertas)
7. [Ações planejadas](#7-ações-planejadas)
8. [Resultados depois da modernização](#8-resultados-depois-da-modernização)
9. [Comparação antes e depois](#9-comparação-antes-e-depois)
10. [Riscos remanescentes e limitações](#10-riscos-remanescentes-e-limitações)

---

## 1. Objetivo e ressalvas

Este documento registra a análise de segurança do código e das dependências do projeto com três ferramentas, **antes** e **depois** da modernização:

| Ferramenta | O que analisa |
|---|---|
| **Bandit** | Código-fonte Python: padrões de implementação potencialmente inseguros (análise estática) |
| **pip-audit** | Dependências declaradas no `requirements.txt`, comparadas com a base de vulnerabilidades do PyPI/OSV |
| **Safety** | Dependências declaradas e ambiente virtual do projeto, comparados com a base de vulnerabilidades da Safety |

**Ressalvas:**
- **Um alerta não é, por si só, uma vulnerabilidade explorável.** Cada ocorrência foi investigada quanto à origem, à versão instalada e ao contexto de uso antes de ser classificada.
- **A ausência de alertas não prova que o sistema é seguro.** Cada ferramenta cobre só uma parte dos problemas possíveis (ver a [seção 10](#10-riscos-remanescentes-e-limitações)).
- **Nenhuma dependência foi adicionada para gerar resultados nas ferramentas.** As ferramentas de auditoria rodam em um ambiente separado do projeto, justamente para não contaminar o resultado (ver a [seção 5](#5-triagem-da-auditoria-anterior-filelock)).

---

## 2. Ambiente e reprodutibilidade

### 2.1 Versões

| Item | Antes | Depois |
|---|---|---|
| Data da execução | 21/11/2026 | 24/11/2026 |
| Código analisado | tag `legado-baseline` (commit `58df732`) | branch `chore/seguranca-depois`: `src/` idêntico ao da `develop` (commit `533dff7`), com as ações 1 a 3 da [seção 7](#7-ações-planejadas) aplicadas |
| Sistema operacional | Ubuntu 26.04 LTS no WSL2 (kernel 6.18.33.1-microsoft-standard-WSL2) | Windows 10 Pro 22H2 (build 19045) |
| Python do ambiente de auditoria (`../.venv-audit`) | 3.14.6 | 3.13.0 |
| Python do ambiente do projeto (`python_pytest/.venv`) | 3.14.6 | 3.13.0 |
| `pip` do ambiente do projeto | 26.1.2 | 26.3 |
| Bandit | 1.9.4 | 1.9.4 |
| pip-audit | 2.10.1 | 2.10.1 |
| Safety | 3.8.1 | 3.8.1 |

As versões das três ferramentas são as mesmas nas duas execuções. O sistema operacional e o Python mudaram porque a reavaliação foi feita em outra máquina. Isso não afeta o Bandit, que analisa o código-fonte, mas afeta a lista de pacotes resolvidos: no Windows, o `pytest` instala também o `colorama` (ver a [seção 8.2](#82-pip-audit)).

### 2.2 Ambiente de auditoria isolado

As ferramentas foram instaladas em um ambiente virtual **fora** da pasta do projeto (`../.venv-audit`). Assim, as dependências das próprias ferramentas não aparecem como se fossem dependências do sistema auditado.

```bash
python -m venv ../.venv-audit
../.venv-audit/bin/pip install bandit pip-audit safety
```

### 2.3 Comandos executados

A partir da raiz do repositório:

```bash
git switch --detach legado-baseline

D=docs/evidencias/seguranca/antes
mkdir -p $D
../.venv-audit/bin/bandit -r python_pytest/src -f json -o $D/bandit.json
../.venv-audit/bin/bandit -r python_pytest/src -f txt  -o $D/bandit.txt
../.venv-audit/bin/pip-audit -r python_pytest/requirements.txt -f json -o $D/pip-audit.json
../.venv-audit/bin/safety auth login
../.venv-audit/bin/safety scan --target python_pytest                       # 1ª execução: vincula o projeto (interativa)
../.venv-audit/bin/safety scan --target python_pytest --output json > $D/safety.json
```

**Depois (Windows, PowerShell).** No Windows os executáveis do ambiente virtual ficam em `Scripts\`, e não em `bin/`. O ambiente do projeto foi recriado do zero, com o `pip` atualizado, para que nenhum pacote removido do `requirements.txt` continuasse instalado:

```powershell
$D = "docs/evidencias/seguranca/depois"

# ambiente do projeto limpo, com o pip atualizado (ação 3)
python -m venv python_pytest\.venv
python_pytest\.venv\Scripts\python.exe -m pip install --upgrade pip
python_pytest\.venv\Scripts\pip.exe install -r python_pytest\requirements.txt

..\.venv-audit\Scripts\bandit.exe -r python_pytest/src -f json -o $D/bandit.json
..\.venv-audit\Scripts\bandit.exe -r python_pytest/src -f txt  -o $D/bandit.txt
..\.venv-audit\Scripts\pip-audit.exe -r python_pytest/requirements.txt -f json -o $D/pip-audit.json
..\.venv-audit\Scripts\safety.exe auth login
..\.venv-audit\Scripts\safety.exe scan --target python_pytest --save-as json $D/safety.json
```

O Safety usou `--save-as` em vez de redirecionar a saída com `>` (ver a [seção 8.3](#83-safety)). Depois disso, o `safety.json` foi reformatado com indentação e convertido para UTF-8, sem alterar o conteúdo:

```powershell
python -c "import json;p='docs/evidencias/seguranca/depois/safety.json';b=open(p,'rb').read();t=b.decode('utf-8','strict') if b.isascii() else b.decode('cp1252');open(p,'w',encoding='utf-8',newline='\n').write(json.dumps(json.loads(t),indent=2,ensure_ascii=False)+'\n')"
```

### 2.4 Evidências

| Arquivo | Conteúdo |
|---|---|
| [`evidencias/seguranca/antes/bandit.json`](evidencias/seguranca/antes/bandit.json) | Relatório do Bandit (JSON) |
| [`evidencias/seguranca/antes/bandit.txt`](evidencias/seguranca/antes/bandit.txt) | Relatório do Bandit (texto) |
| [`evidencias/seguranca/antes/pip-audit.json`](evidencias/seguranca/antes/pip-audit.json) | Relatório do pip-audit |
| [`evidencias/seguranca/antes/safety.json`](evidencias/seguranca/antes/safety.json) | Relatório do Safety |
| [`evidencias/seguranca/depois/bandit.json`](evidencias/seguranca/depois/bandit.json) | Relatório do Bandit (JSON), depois |
| [`evidencias/seguranca/depois/bandit.txt`](evidencias/seguranca/depois/bandit.txt) | Relatório do Bandit (texto), depois |
| [`evidencias/seguranca/depois/pip-audit.json`](evidencias/seguranca/depois/pip-audit.json) | Relatório do pip-audit, depois |
| [`evidencias/seguranca/depois/safety.json`](evidencias/seguranca/depois/safety.json) | Relatório do Safety, depois |

---

## 3. Escopo de cada ferramenta

| Ferramenta | Escopo | Justificativa |
|---|---|---|
| Bandit | `python_pytest/src/` (5 arquivos, 133 linhas) | É o código de produção. A pasta `tests/` ficou de fora: o Bandit gera nela **86 alertas B101** (uso de `assert`, severidade baixa), que são esperados, porque o `assert` é o mecanismo do próprio pytest e os testes não vão para produção |
| pip-audit | `python_pytest/requirements.txt` | O pip-audit resolve as dependências declaradas em um ambiente temporário e audita o resultado: 22 pacotes, incluindo os transitivos. Não audita ferramentas do ambiente, como o `pip` |
| Safety | `python_pytest/` | O Safety encontrou dois alvos: o `requirements.txt` (4 dependências declaradas) e o ambiente virtual `python_pytest/.venv` (24 pacotes instalados, incluindo `pip` e `packaging`) |

**Sobre as dependências do projeto:** o `requirements.txt` declara apenas ferramentas de teste (`pytest`, `approvaltests`, `pytest-approvaltests` e `coverage`), todas **sem versão fixada**. O código de produção (`src/`) usa só a biblioteca padrão do Python (`enum` e `math`). Portanto, **nenhuma dependência de terceiros é executada em produção**, e todas as ocorrências de dependências deste relatório se referem ao ambiente de desenvolvimento e de testes.

---

## 4. Resultados antes da modernização

### 4.1 Bandit

| Métrica | Resultado |
|---|---|
| Arquivos analisados | 5 (`catalog.py`, `model_objects.py`, `receipt.py`, `shopping_cart.py`, `teller.py`) |
| Linhas de código | 133 |
| Ocorrências (alta / média / baixa) | 0 / 0 / 0 |
| Linhas ignoradas com `# nosec` | 0 |
| Erros | 0 |

**Nenhum padrão inseguro foi identificado.** O resultado é coerente com o código: não há entrada externa, acesso a arquivos, rede, banco de dados, desserialização, execução de comandos nem uso de `eval`. O `SupermarketCatalog` apenas lança uma exceção no lugar do acesso ao banco.

### 4.2 pip-audit

| Métrica | Resultado |
|---|---|
| Pacotes auditados (declarados e transitivos) | 22 |
| Vulnerabilidades conhecidas | **0** |
| Correções sugeridas | nenhuma |

Versões resolvidas no momento da execução: `pytest` 9.2.0, `coverage` 7.17.4, `approvaltests` 20.0.1, `pytest-approvaltests` 0.2.4, mais 18 dependências transitivas (`requests`, `urllib3`, `certifi`, `beautifulsoup4`, `psutil` etc., quase todas trazidas pelo `approvaltests`).

### 4.3 Safety

| Métrica | Resultado |
|---|---|
| Autenticação | Exigida (conta na Safety Platform). Relatório gerado como `authenticated: true` |
| Política aplicada | Política padrão da conta, carregada da nuvem (`policy.source: cloud`) |
| Alvos encontrados | `requirements.txt` (4 dependências) e `.venv/pyvenv.cfg` (24 pacotes) |
| Ocorrências | **3**, todas marcadas como **ignoradas** pela política |

| Pacote | Origem | ID Safety | Faixa vulnerável | Versão em uso | Motivo de ter sido ignorada |
|---|---|---|---|---|---|
| `pytest` | `requirements.txt` | SFTY-20260122-20373 | `<9.0.3` | sem versão declarada (instalada: 9.2.0) | `unpinned-specification`: a dependência não tem versão fixada |
| `pip` | `.venv` | SFTY-20260729-70233 | `>=6.0,<26.2` | 26.1.2 | `environment-dependency`: pacote do ambiente, não do projeto |
| `pip` | `.venv` | SFTY-20261020-17374 | `>=19.1,<26.2.2` | 26.1.2 | `environment-dependency` |

"Ignorada" quer dizer que a política padrão não conta a ocorrência como falha. **Não** quer dizer que ela foi corrigida ou que não se aplica. Por isso as três foram triadas na [seção 6](#6-classificação-dos-alertas).

### 4.4 Limitação de acesso do Safety

- **Conta obrigatória.** O `safety scan` só roda depois do login (`safety auth login`), que exige uma conta na Safety Platform. Sem a conta, a ferramenta não produz relatório.
- **Vínculo interativo do projeto.** Na primeira execução, o Safety pergunta se o projeto deve ser vinculado à conta. Com a saída redirecionada para arquivo (`> safety.json`), a pergunta não aparece na tela e o comando parece travado. Foi preciso rodar uma vez sem redirecionar, responder a pergunta e só então gerar o JSON. O vínculo é gravado em `python_pytest/.safety-project.ini`.
- **Detalhes restritos à plataforma.** O JSON traz o ID Safety e a faixa vulnerável, mas não a descrição nem a severidade. A correspondência com CVEs da [seção 6](#6-classificação-dos-alertas) foi feita consultando a base pública do PyPI/OSV com o pip-audit.
- **Política na nuvem.** As regras que ignoram dependências de ambiente e dependências sem versão fixada vêm da configuração da conta, e não de um arquivo do repositório. Outra conta pode ter outra política e, portanto, outro resultado.

---

## 5. Triagem da auditoria anterior (`filelock`)

A primeira auditoria do grupo, de 19/11/2026, relatou **13 vulnerabilidades no pip-audit** e **14 no Safety**, todas no pacote `filelock` 3.32.7. A investigação mostrou que esse pacote **não é dependência do projeto**:

| Verificação | Resultado |
|---|---|
| `filelock` no `requirements.txt` ou nas suas dependências transitivas | Não aparece (os 22 pacotes resolvidos pelo pip-audit não incluem o `filelock`) |
| `filelock` no ambiente do projeto (`python_pytest/.venv`) | Não instalado |
| `filelock` no ambiente de auditoria (`../.venv-audit`) | Instalado, versão 3.32.7, **exigido pelo `safety`** (`Required-by: safety`) |
| Motivo informado pelo Safety na auditoria anterior | `environment-dependency` |

**Conclusão:** na auditoria anterior, as ferramentas foram instaladas no mesmo ambiente virtual do projeto. O `filelock`, que é dependência do próprio Safety, entrou nesse ambiente e foi auditado como se fosse do sistema. Com as ferramentas em um ambiente isolado, as 13 ocorrências desaparecem dos dois relatórios.

| | Ambiente contaminado (19/11) | Ambiente isolado (21/11) |
|---|---|---|
| pip-audit | 13 vulnerabilidades (`filelock`) | 0 |
| Safety | 14 ocorrências ignoradas | 3 ocorrências ignoradas (`pytest` e `pip`) |

**Divergência entre 14 e 13.** O pip-audit contou 13 ocorrências, e o Safety 14, embora o detalhamento do Safety listasse 13 registros do `filelock`. A explicação mais provável é a ocorrência do `pytest` sem versão fixada (SFTY-20260122-20373), que aparece na seção do `requirements.txt` do relatório, separada da seção do ambiente, onde estavam os registros do `filelock`. Ela continua presente no relatório atual. Não foi possível confirmar essa hipótese, porque o JSON da auditoria anterior não foi preservado. As ocorrências do `pip` não entram nessa conta, porque a versão do `pip` instalada na época não foi registrada.

---

## 6. Classificação dos alertas

| ID | Ferramenta | Pacote ou arquivo | Vulnerabilidade | Severidade | Relevância no contexto | Ação | Justificativa |
|---|---|---|---|---|---|---|---|
| A-01 | Safety | `pytest` (`requirements.txt`) | SFTY-20260122-20373 / CVE-2025-71176 / GHSA-6w46-j5rx-g56g: até a versão 9.0.2, o pytest usa diretórios com o padrão `/tmp/pytest-of-{user}`, o que permite a um usuário local causar negação de serviço ou possivelmente escalar privilégios | Não informada no relatório; impacto descrito como negação de serviço ou escalonamento **local** | **Baixa.** A versão instalada (9.2.0) **não** está na faixa vulnerável, e o pytest só roda em ambiente de desenvolvimento. O risco real é a falta de versão mínima: uma instalação com cache antigo ou um ambiente restrito poderia trazer uma versão vulnerável | **Corrigir na Fase 7:** fixar a versão no `requirements.txt` (por exemplo, `pytest==9.2.0`) | Fixar versões elimina o alerta e torna a instalação reproduzível (RNF08). Não altera o código de produção |
| A-02 | Safety | `pip` 26.1.2 (`python_pytest/.venv`) | SFTY-20260729-70233 (faixa `<26.2`). Pela faixa de versões, corresponde a CVE-2026-13346 / GHSA-qwm4-qh6w-59xr: o pip trata incorretamente URLs com codificação dupla vindas de um índice de pacotes, o que permite gravar arquivos em locais arbitrários | Não informada no relatório | **Baixa.** Só é explorável ao instalar pacotes de um **índice malicioso**. O projeto usa apenas o PyPI oficial, e o `pip` não faz parte do sistema, só do ambiente de desenvolvimento | **Corrigir no ambiente:** atualizar o `pip` do `.venv` para 26.2.2 ou superior (`python -m pip install --upgrade pip`) | É uma correção de ambiente, não do projeto: o `pip` não é declarado no `requirements.txt`. Deve constar no README como passo de preparação do ambiente |
| A-03 | Safety | `pip` 26.1.2 (`python_pytest/.venv`) | SFTY-20261020-17374 (faixa `>=19.1,<26.2.2`). Sem CVE correspondente na base pública consultada; a descrição só está disponível na Safety Platform | Não informada no relatório | **Baixa**, pelo mesmo motivo do A-02: ferramenta do ambiente, não do sistema | **Corrigir no ambiente**, com a mesma atualização do A-02 | A atualização para 26.2.2 ou superior resolve os dois alertas de uma vez |
| A-04 | pip-audit e Safety (auditoria de 19/11) | `filelock` 3.32.7 | 13 CVEs (CVE-2026-112907 a CVE-2026-112940) | Não classificada | **Não se aplica ao projeto.** O pacote é dependência do Safety e estava no ambiente por causa das ferramentas de auditoria (ver a [seção 5](#5-triagem-da-auditoria-anterior-filelock)) | **Nenhuma no projeto.** Ferramentas isoladas em `../.venv-audit` | O alerta era um falso positivo de escopo. O `filelock` vulnerável continua no ambiente de auditoria, que é externo ao repositório e não é entregue |
| A-05 | Bandit | `python_pytest/tests/` | 86 ocorrências de B101 (`assert` usado) | Baixa | **Não se aplica.** O `assert` é o mecanismo de verificação do pytest, e os testes não são executados em produção | **Nenhuma.** A pasta fica fora do escopo do Bandit | Corrigir exigiria reescrever os testes sem `assert`, o que pioraria a legibilidade sem ganho de segurança |

**Nenhum alerta afeta o código de produção.** O Bandit não encontrou ocorrências no `src/`, e todas as ocorrências de dependências estão em ferramentas de desenvolvimento ou de ambiente.

---

## 7. Ações planejadas

Ações a aplicar na Fase 7 do [plano de execução](plano_de_execucao.md), antes da reavaliação "depois":

| # | Ação | Alertas resolvidos | Onde |
|---|---|---|---|
| 1 | Fixar as versões das dependências no `requirements.txt` (por exemplo, `pytest==9.2.0` e `coverage==7.17.4`) | A-01 | `python_pytest/requirements.txt` |
| 2 | Remover `approvaltests` e `pytest-approvaltests` (decisão D7, tomada na Fase 3). Nenhum teste os usa, e eles trazem a maior parte das 18 dependências transitivas | Reduz a superfície de dependências | `python_pytest/requirements.txt`, `tests/approvaltests_config.json` |
| 3 | Atualizar o `pip` do ambiente do projeto para 26.2.2 ou superior e documentar o passo no README | A-02, A-03 | Ambiente local e README |
| 4 | Manter as ferramentas de auditoria no ambiente isolado `../.venv-audit` | A-04 | Procedimento |

---

## 8. Resultados depois da modernização

Execução de 24/11/2026, com os comandos da [seção 2.3](#23-comandos-executados) e as evidências em `docs/evidencias/seguranca/depois/`. Antes dela, foram aplicadas as ações 1 a 3 da [seção 7](#7-ações-planejadas):

| # | Ação | Como foi aplicada |
|---|---|---|
| 1 | Fixar as versões | `requirements.txt` com `pytest==9.2.0` e `coverage==7.6.12` |
| 2 | Remover o `approvaltests` (D7) | `approvaltests` e `pytest-approvaltests` saíram do `requirements.txt`. Foram removidos também o `tests/approvaltests_config.json` e a entrada `.approval_tests_temp` do `python_pytest/.gitignore`. Os 118 testes continuam passando, o que confirma que nenhum deles usava a biblioteca |
| 3 | Atualizar o `pip` do ambiente | `.venv` recriado do zero, com o `pip` 26.3. O passo de atualização foi incluído na seção "Setup" do `python_pytest/README.md` e, na Fase 9, passou para a [seção 4.2 do README da raiz](../README.md#42-criar-o-ambiente-virtual-e-instalar-as-dependências), que concentra as instruções de instalação |

**Sobre a versão do `pytest`.** Uma primeira tentativa fixou `pytest==8.3.5`. O Safety passou a apontar o A-01 como ocorrência **não ignorada**, porque a versão fixada estava dentro da faixa vulnerável (`<9.0.3`). Antes da fixação, a política o ignorava só por falta de versão. A versão foi corrigida para 9.2.0 antes da execução registrada aqui. O episódio mostra que fixar a versão só resolve o alerta quando a versão escolhida está fora da faixa vulnerável.

### 8.1 Bandit

| Métrica | Resultado |
|---|---|
| Arquivos analisados | 7 (`catalog.py`, `discount_engine.py`, `discount_policies.py`, `model_objects.py`, `receipt.py`, `shopping_cart.py`, `teller.py`) |
| Linhas de código | 349 |
| Ocorrências (alta / média / baixa) | 0 / 0 / 0 |
| Linhas ignoradas com `# nosec` | 0 |
| Erros | 0 |

**Nenhum padrão inseguro foi identificado no código modernizado.** Os módulos novos (`discount_policies.py` e `discount_engine.py`) seguem o padrão do legado: nenhuma entrada externa, nenhum acesso a arquivos, rede ou banco de dados, nenhuma execução de comandos e nenhum `eval`. Nenhuma linha foi silenciada com `# nosec`.

### 8.2 pip-audit

| Métrica | Resultado |
|---|---|
| Pacotes auditados (declarados e transitivos) | 6 |
| Vulnerabilidades conhecidas | **0** |
| Correções sugeridas | nenhuma |

Versões resolvidas: `pytest` 9.2.0, `coverage` 7.6.12, `pluggy` 1.7.0, `iniconfig` 2.3.1, `pygments` 2.21.0 e `colorama` 0.4.6. O `colorama` só é instalado pelo `pytest` no Windows. No Linux, a mesma auditoria resolveria 5 pacotes.

### 8.3 Safety

| Métrica | Resultado |
|---|---|
| Autenticação | Exigida. Relatório gerado como `authenticated: true` |
| Política aplicada | Política padrão da conta, carregada da nuvem (`policy.source: cloud`) |
| Alvos encontrados | `requirements.txt` (2 dependências) e `.venv/pyvenv.cfg` (8 pacotes, incluindo `pip` 26.3 e `packaging`) |
| Ocorrências (ignoradas / não ignoradas) | **0 / 0** |

**Limitações encontradas no Windows**, além das já descritas na [seção 4.4](#44-limitação-de-acesso-do-safety):

- **Redirecionamento com `>`.** No PowerShell 5.1, o `>` grava o arquivo em UTF-16, e não em UTF-8. Além disso, ele esconde a pergunta de vínculo do projeto, e o `safety.json` saiu vazio. A solução foi usar a opção `--save-as json <arquivo>`, que grava o relatório diretamente e mantém a saída normal na tela.
- **Codificação do `--save-as`.** O arquivo gerado vem sem quebras de linha, e o caminho da pasta, que tem acento ("MATÉRIAS"), vem na codificação Windows-1252, e não em UTF-8. O arquivo foi reformatado e convertido para UTF-8, sem alterar o conteúdo, com o comando da [seção 2.3](#23-comandos-executados).
- **Comando `safety check`.** Uma tentativa intermediária usou o comando antigo `safety check`, descontinuado desde 2024. Ele analisa só o `requirements.txt`, sem o ambiente virtual, e por isso não é comparável com a linha de base. O relatório foi descartado.

---

## 9. Comparação antes e depois

| Ferramenta | Métrica | Antes | Depois | Observação |
|---|---|---|---|---|
| Bandit | Arquivos / linhas em `src/` | 5 / 133 | 7 / 349 | A refatoração criou novos módulos (`discount_policies.py`, `discount_engine.py`) e implementou os combos |
| Bandit | Ocorrências | 0 | 0 | O código cresceu 2,6 vezes sem introduzir padrões inseguros |
| pip-audit | Pacotes auditados | 22 | 6 | Queda de 73%, causada pela remoção do `approvaltests` (D7), que trazia a maior parte das dependências transitivas |
| pip-audit | Vulnerabilidades | 0 | 0 | |
| Safety | Dependências declaradas no `requirements.txt` | 4 (sem versão) | 2 (versões fixadas) | |
| Safety | Pacotes no ambiente do projeto | 24 | 8 | |
| Safety | Ocorrências no `requirements.txt` | 1 (A-01, ignorada) | 0 | Zerou com a fixação do `pytest` em 9.2.0 |
| Safety | Ocorrências no ambiente | 2 (A-02 e A-03, ignoradas) | 0 | Zerou com o `pip` atualizado para 26.3 |

| Alerta | Situação depois | Motivo |
|---|---|---|
| A-01 | **Resolvido** | `pytest` fixado em 9.2.0, fora da faixa vulnerável (`<9.0.3`). A instalação deixou de depender da versão que o `pip` resolver no momento |
| A-02 | **Resolvido** | `pip` do ambiente do projeto atualizado de 26.1.2 para 26.3, fora da faixa `<26.2` |
| A-03 | **Resolvido** | Mesma atualização: 26.3 está fora da faixa `>=19.1,<26.2.2` |
| A-04 | Não se aplica | Ferramentas isoladas em `../.venv-audit` desde a linha de base. O `filelock` não aparece em nenhum relatório |
| A-05 | Não se aplica | A pasta `tests/` continua fora do escopo do Bandit |
| Novos alertas | **Nenhum** | Nenhuma das três ferramentas apontou ocorrência nova, nem nos módulos criados na refatoração |

**Síntese:** todos os alertas da linha de base que se aplicavam ao projeto foram resolvidos, e nenhum alerta novo surgiu. A superfície de dependências caiu de 22 para 6 pacotes. Isso reduz a exposição a vulnerabilidades futuras, porque cada pacote a menos é um pacote a menos para acompanhar. Como alerta a [seção 1](#1-objetivo-e-ressalvas), esse resultado **não prova** que o sistema é seguro: ele mostra apenas que as ferramentas não encontraram problemas conhecidos no escopo que cada uma cobre. Nenhuma dependência foi adicionada para gerar resultados.

---

## 10. Riscos remanescentes e limitações

### 10.1 Riscos remanescentes

- **`float` para valores monetários (RNF09).** Não é uma vulnerabilidade apontada pelas ferramentas, mas é um risco de integridade dos valores. O tipo foi mantido para não alterar os resultados observados pelos testes. A impressão arredonda para 2 casas, e a política de combos compara totais em centavos (ver o [diagnóstico técnico, seção 3.11](diagnostico_tecnico.md#311-float-para-valores-monetários)).
- **Ferramentas de auditoria com dependências vulneráveis.** O ambiente `../.venv-audit` contém o `filelock` 3.32.7. Ele está fora do repositório e não é entregue, mas deve ser atualizado se for reutilizado.

### 10.2 Limitações das ferramentas

| Ferramenta | Limitação |
|---|---|
| Bandit | Procura padrões conhecidos de código inseguro. Não detecta erros de lógica de negócio, como os defeitos DEF-01 e DEF-02, que afetam valores cobrados sem nenhum padrão "inseguro" no código |
| pip-audit | Depende das bases públicas do PyPI e do OSV. Vulnerabilidades ainda não publicadas não aparecem. Audita a resolução feita no momento da execução, e, sem versões fixadas, outra execução pode resolver versões diferentes |
| Safety | Exige conta, aplica uma política configurada na nuvem que ignora, por padrão, dependências de ambiente e sem versão fixada, e mostra os detalhes das vulnerabilidades só na plataforma |
| Todas | Não testam o sistema em execução (análise dinâmica), não avaliam a infraestrutura e não substituem uma revisão de segurança manual |
