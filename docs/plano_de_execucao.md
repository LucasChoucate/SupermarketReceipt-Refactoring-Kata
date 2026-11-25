# Plano de Execução: Modernização do Supermarket Receipt

Este documento organiza o trabalho que falta para cumprir o edital. Ele está dividido em 10 fases, em ordem. Cada fase indica o passo do edital que cumpre, o que fazer, quais arquivos mudam e como saber que terminou.

> **Situação atual.** As Fases 0 a 4 estão integradas na `develop`: documentos de análise, linha de base de segurança, testes de caracterização, refatoração com padrões de projeto e correção dos três defeitos. Os combos (Fase 5) estão concluídos na branch `feat/combos`, com 109 testes passando. Ainda faltam a regressão com combos (Fase 6), a segurança "depois", o README e a apresentação.

---

## Sumário

- [Regras gerais](#regras-gerais)
- [Política de convivência entre combos e ofertas](#política-de-convivência-entre-combos-e-ofertas)
- [Decisões registradas (D1 a D7)](#decisões-registradas-d1-a-d7)
- [Fase 0: Organização do repositório](#fase-0-organização-do-repositório)
- [Fase 1: Corrigir os documentos de análise](#fase-1-corrigir-os-documentos-de-análise)
- [Fase 2: Refazer a linha de base de segurança](#fase-2-refazer-a-linha-de-base-de-segurança)
- [Fase 3: Complementar os testes de caracterização](#fase-3-complementar-os-testes-de-caracterização)
- [Fase 4: Refatoração com padrões de projeto](#fase-4-refatoração-com-padrões-de-projeto)
- [Fase 5: Implementar os combos](#fase-5-implementar-os-combos)
- [Fase 6: Testes de regressão](#fase-6-testes-de-regressão)
- [Fase 7: Reavaliação de segurança](#fase-7-reavaliação-de-segurança)
- [Fase 8: Documento de padrões de projeto](#fase-8-documento-de-padrões-de-projeto)
- [Fase 9: README e evidências finais](#fase-9-readme-e-evidências-finais)
- [Fase 10: Apresentação e entrega](#fase-10-apresentação-e-entrega)
- [Checklist anti-penalidade](#checklist-anti-penalidade)
- [O que pode andar em paralelo](#o-que-pode-andar-em-paralelo)

---

## Regras gerais

- **Uma branch por fase**, saindo da `develop`, com PR de volta para a `develop`.
- **Commits pequenos**, no padrão Conventional Commits (`feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`).
- **A suíte inteira precisa passar a cada commit.** Um teste só pode mudar de valor esperado em uma correção de defeito intencional e documentada (ver D2, D3 e o [registro de defeitos](registro_de_defeitos.md)).
- **O código novo do `src/` fica em inglês**, para manter a consistência com o legado (RNF06). Os testes e a documentação continuam em português.

---

## Política de convivência entre combos e ofertas

### A regra dos combos

Quando o carrinho tem todos os produtos de um combo, aplica-se 10% de desconto **só sobre as unidades que formam combos completos**.

```
nº de combos = menor valor de ⌊disponível[p] / exigido[p]⌋ entre os produtos do combo
desconto     = 10% × nº de combos × (soma dos preços dos produtos do combo)
```

Exemplos com escova a R$ 10,00 e creme dental a R$ 15,00:

| Carrinho | Combos | Desconto | Total |
|---|---|---|---|
| 1 escova + 1 creme | 1 | R$ 2,50 | R$ 22,50 |
| 2 escovas + 1 creme | 1 | R$ 2,50 | R$ 32,50 (uma escova a preço cheio) |
| 2 escovas + 2 cremes | 2 | R$ 5,00 | R$ 45,00 |
| Só 1 escova | 0 | — | R$ 10,00 |

### O problema

Um produto pode ter uma oferta individual (por exemplo, "3 por 2") e também fazer parte de um combo. O edital proíbe desconto duplicado na mesma unidade e exige manter o comportamento anterior nos carrinhos com promoções preexistentes.

Dar sempre prioridade ao combo **encarece** alguns carrinhos. Exemplo, com a escova em "3 por 2":

- **Carrinho:** 3 escovas + 1 creme.
- **Legado:** R$ 35,00.
- **Combo primeiro:** o combo leva 1 escova e 1 creme (R$ 22,50) e as 2 escovas restantes não ativam o "3 por 2" (R$ 20,00). Total: **R$ 42,50**.

Comparar só os percentuais também engana. O combo dá 10% nos **dois** produtos, inclusive no parceiro que não tinha desconto. Por isso ele pode vencer até ofertas de 20% ou 33%, dependendo dos preços.

### A política adotada: o melhor dos dois, com empate para as ofertas

1. Cada oferta individual informa quantas unidades **consumiu**:

   | Oferta | Unidades consumidas |
   |---|---|
   | 3 por 2 | `(qtd_inteira // 3) × 3`, se ativou |
   | 2 por valor | `(qtd_inteira // 2) × 2`, se ativou |
   | 5 por valor | `(qtd_inteira // 5) × 5`, se ativou |
   | Percentual | **Todas** as unidades |
   | Oferta que não ativou | 0 |

2. O carrinho é calculado **das duas formas**:
   - **Ordem C (ofertas → combos):** as ofertas individuais são aplicadas primeiro, exatamente como seriam sem combos, e os combos usam só as unidades que sobraram.
   - **Ordem B (combos → ofertas):** os combos são aplicados primeiro e as ofertas individuais usam só as unidades que sobraram.

3. Fica a ordem de **menor total**. **Em empate, vence a ordem C** (as ofertas individuais são mantidas). O combo só substitui uma oferta quando é **estritamente melhor** para o cliente.
4. A comparação dos totais é feita **em centavos** (arredondando para 2 casas), para que diferenças de ponto flutuante não decidam o desempate.

### O que essa política garante

| Propriedade | Por quê |
|---|---|
| Cadastrar um combo nunca encarece o carrinho | O resultado é ≤ ordem C, e a ordem C é ≤ o mesmo carrinho sem combos, porque só acrescenta descontos |
| O recibo só muda quando o combo traz ganho real | Em empate, mantém-se a ordem C, que preserva as linhas de desconto das ofertas preexistentes |
| Não há desconto duplicado | Cada unidade é consumida por uma única política |
| Carrinho sem combo completo fica idêntico ao cálculo sem combos | Nas duas ordens nenhum combo se forma |

> A comparação é sempre com **o mesmo carrinho sem combos, no sistema já corrigido** (ver D2). Nos cenários dos defeitos DEF-01 e DEF-02, o total muda em relação ao legado por causa das correções, não por causa dos combos.
| É determinística e testável | São sempre exatamente dois cálculos |

**Limitação documentada:** a escolha é feita para o carrinho inteiro. Distribuições mistas não são testadas, como "este combo primeiro, aquela oferta primeiro". Isso exigiria testar todas as combinações, o que aumentaria a complexidade e não é exigido pelo edital.

### Quem vence: exemplos

| Cenário | Ordem C | Ordem B | Escolhida |
|---|---|---|---|
| Escova R$ 10 com "3 por 2" + creme R$ 15; carrinho 3 + 1 | **R$ 35,00** | R$ 42,50 | C (oferta) |
| Escova R$ 10 com 20% + creme R$ 15; carrinho 1 + 1 | R$ 23,00 | **R$ 22,50** | B (combo) |
| Escova R$ 10 com "5 por 40" + creme R$ 15; carrinho 5 + 5 | R$ 115,00 | **R$ 112,50** | B (combo) |
| Escova R$ 10 com "2 por 15" + creme R$ 15; carrinho 2 + 2 | R$ 45,00 | R$ 45,00 | C (empate → ofertas) |

---

## Decisões registradas (D1 a D7)

Estas decisões devem constar no plano de contingência e no README.

| ID | Decisão | Escolha | Justificativa |
|---|---|---|---|
| D1 | Convivência entre combo e oferta | O melhor dos dois, com empate para as ofertas (ordem C), comparando em centavos | Nunca encarece, sem duplicidade, e mantém as ofertas preexistentes quando o combo não traz ganho, em linha com o "manter o comportamento anterior" do edital |
| D2 | Defeitos confirmados do legado: **DEF-01** ("2 por valor" com quantidade ímpar cobra a mais), **DEF-02** (fração gratuita nas ofertas por grupo) e **DEF-03** (`product_with_name` fora do contrato do catálogo) | **Corrigir todos** | DEF-01 cobra do cliente mais do que sem a oferta; DEF-02 concede desconto maior que o anunciado; DEF-03 quebra com qualquer catálogo real. Detalhes no [registro de defeitos](registro_de_defeitos.md) |
| D3 | Momento e forma das correções | **Depois da refatoração estrutural**, em uma branch própria (`fix/defeitos-legado`) criada após o merge da refatoração, com um commit `fix:` por defeito, cada um precedido de um teste `xfail(strict=True)` do comportamento correto | Separa mudança de estrutura de mudança de comportamento. Com o Template Method, DEF-01 e DEF-02 são corrigidos em um único lugar, e cada correção pode ser revertida isoladamente |
| D4 | Representação do combo no recibo | Um `Discount` por produto do combo, com a descrição `"combo 10% off"` | Não muda a classe `Discount` nem o `ReceiptPrinter` |
| D5 | API do combo | Nova e aditiva: `teller.add_bundle_offer(products, percent=10)` | Não altera o enum `SpecialOfferType`, o `teller.offers` nem o `add_special_offer`, que são protegidos por testes de contrato |
| D6 | Dois combos disputando o mesmo produto | Vence a ordem de cadastro | Simples, determinístico e testável |
| D7 | Uso do `approvaltests` | Não usar e remover na Fase 7, junto com o `pytest-approvaltests` e o `tests/approvaltests_config.json` | Nenhum teste usa a biblioteca. A suíte de caracterização já demonstra a preservação de comportamento com 99% de cobertura de ramos e recibos de referência fixados no próprio teste. A remoção reduz a superfície de dependências (seção 8 do roteiro: evitar dependências desnecessárias) |

**Sobre os 10%:** o edital define a regra dos 10% como obrigatória, e combos incorretos custam −2,0. O percentual pode ser um parâmetro com padrão de 10%, o que demonstra extensibilidade, mas todos os requisitos e testes usam 10%. A validação de "proporcionalidade mínima" (RF18) não deve ser implementada, porque faria o `add_special_offer` rejeitar ofertas que o legado aceita.

---

## Fase 0: Organização do repositório

> **Edital:** base da estratégia de reversão e de "Evidências / README" | **Branch:** `chore/organizacao`

- [ ] **Criar e publicar a tag da linha de base**, que é a versão estável citada na estratégia de reversão:
  ```bash
  git tag legado-baseline 58df732
  git push origin legado-baseline
  ```
- [ ] **Incluir `*:Zone.Identifier` no `.gitignore` da raiz.** São arquivos que o Windows cria ao baixar documentos.
- [ ] **Criar a estrutura de pastas:**
  ```
  docs/
  ├── diagnostico_tecnico.md
  ├── registro_de_defeitos.md
  ├── requisitos.md
  ├── plano_contingencia.md
  ├── padroes_projeto.md
  ├── seguranca_antes_depois.md
  ├── evidencias_testes.md
  └── evidencias/
      ├── testes/
      └── seguranca/
          ├── antes/
          └── depois/
  apresentacao/
  ```
  A sugestão é escrever em Markdown (versionável, com diffs visíveis nos PRs) e exportar para PDF no final. Quem preferir o Word deve exportar o PDF para essas mesmas pastas.
- [ ] **Definir um ambiente de referência** (por exemplo, Python 3.12 em Ubuntu ou WSL) e registrá-lo no README. Hoje há três ambientes diferentes nos registros: 3.13.11 no Windows, 3.12.5 no Windows e 3.12.3 no Ubuntu.
- [ ] **Regenerar as evidências do Passo 2:**
  - [ ] Log da execução **original** (1 teste). Ele é gerado em um *worktree* temporário, uma cópia do commit original em outra pasta, para não mexer na branch atual:
    ```bash
    REPO=$(pwd)
    git worktree add ../kata-inicial 095e831
    cd ../kata-inicial/python_pytest
    "$REPO/python_pytest/.venv/bin/python" -m pytest -v -p no:cacheprovider \
        > "$REPO/docs/evidencias/testes/01_pytest_inicial.log" 2>&1
    cd "$REPO"
    git worktree remove ../kata-inicial
    ```
  - [ ] Log após a caracterização (57 testes): o `docs/evidencias/pytest_antes_ubuntu.log` já está em UTF-8 e com os nomes atuais dos testes, então serve como evidência. Remover o `pytest_antes_windows.log`, que está em UTF-16 e com um nome de teste desatualizado, ou regenerá-lo em UTF-8 no Windows (`python -m pytest -v | Out-File -Encoding utf8 <arquivo>`).

**Pronto quando:** a tag está no remoto, a pasta `docs/` está estruturada e os logs estão em UTF-8.

---

## Fase 1: Corrigir os documentos de análise

> **Edital:** Passos 3, 4 e 5 | **Barema:** 1,0 + 1,0 + 0,5 | Evita as penalidades de −3,0 por diagnóstico ou plano ausentes | **Branch:** `docs/analise`

### 1.1 Diagnóstico técnico

- [x] **Incluir uma seção de Duplicação:** as três fórmulas de oferta por grupo em `shopping_cart.py` (linhas 45, 54–55 e 63–64) seguem o mesmo padrão. Mostrar o **trecho de código**, não só o número das linhas.
- [x] **Incluir uma seção de Defeitos encontrados**, resumindo e apontando para o [registro de defeitos](registro_de_defeitos.md):
  - DEF-01: "2 por valor" com quantidade ímpar (`/` em vez de `//`, linha 45);
  - DEF-02: fração gratuita nas ofertas por grupo (linhas 45, 54–55 e 63–64);
  - DEF-03: `Teller.product_with_name` acessa `catalog.products`, que não faz parte do contrato (linhas 28–29 de `teller.py`).
- [x] **Incluir os smells que faltam:**
  - [x] lógica do "3 por 2" partida em dois blocos (linhas 39–40 e 53–56);
  - [x] nomes pouco expressivos (`x`, `p`, `discount_n`, `number_of_x`);
  - [x] números mágicos (2, 3, 5, 100);
  - [x] Feature Envy no `handle_offers`, que usa mais dados do catálogo, da oferta e do recibo do que do próprio carrinho;
  - [x] `float` para valores monetários;
  - [x] `ShoppingCart.items` expondo a lista interna. A síntese cita esse ponto, mas o corpo do texto não o analisa.
- [x] **Corrigir a numeração** (há duas seções 7) e os erros de digitação ("catélogo", "susbtituição", "foram identificados foram registrados").

### 1.2 Requisitos

> **Feito em [`requisitos.md`](requisitos.md).** Para não criar requisitos desnecessários, os itens marcados como "novo RF/RNF" e a quebra do RF04/RF05 foram atendidos como **critérios de aceitação** dos requisitos existentes: o percentual no RF04, os critérios das ofertas por grupo e de DEF-01/DEF-02 no RF05, D6 no RF11 e DEF-03 no RNF01. A rastreabilidade já tem os testes de caracterização e segue sendo preenchida nas Fases 4 a 6.

- [x] **RF01:** corrigir a descrição. O preço vem do catálogo no momento do checkout e não é registrado no carrinho.
- [x] **Quebrar RF04 e RF05 em um requisito por oferta**, com critérios numéricos:
  - [x] 3 por 2 (por exemplo, 7 unidades a R$ 10 custam R$ 50);
  - [x] desconto percentual (por exemplo, 3 unidades a R$ 10 com 20% dão R$ 6 de desconto);
  - [x] 2 por valor (por exemplo, 4 unidades a R$ 10 em "2 por 15" custam R$ 30);
  - [x] 5 por valor (por exemplo, 12 unidades a R$ 10 em "5 por 40" custam R$ 100).
- [x] **RF07:** manter os 10% sobre os combos completos. O percentual pode ser parâmetro, desde que o padrão seja 10%.
- [x] **RF16:** reescrever como "Se combo e oferta individual disputarem as mesmas unidades, aplicar a ordem (combos primeiro ou ofertas primeiro) que resultar no menor total, comparado em centavos; em empate, prevalecem as ofertas individuais."
- [x] **Novo RF:** combos que disputam o mesmo produto são resolvidos pela ordem de cadastro (D6).
- [x] **Novo RF (DEF-01):** o "2 por valor" com quantidade ímpar cobra a unidade restante a preço cheio. Critério: 3 unidades a R$ 10 em "2 por 15" custam R$ 25.
- [x] **Novo RF (DEF-02):** nas ofertas por grupo, toda a sobra (unidades e fração) é cobrada a preço cheio. Critério: 3,5 kg a R$ 2,00 em "3 por 2" custam R$ 5,00.
- [x] **Novo RNF (DEF-03):** o `Teller` funciona com qualquer catálogo que cumpra o contrato de `SupermarketCatalog`, incluindo a busca de produto por nome.
- [x] **Remover RF15, RF17 e RF18:**
  - RF15 e RF18 vão para uma seção "Fora de escopo", com justificativa.
  - RF17 já é comportamento do legado e vira critério de aceitação do RF14.
- [x] **Incluir a coluna de rastreabilidade:** RF → arquivo ou classe → nome do teste → evidência. Preencher ao longo das Fases 4 a 6.

### 1.3 Plano de contingência

> **Feito em [`plano_contingencia.md`](plano_contingencia.md).** Além dos itens abaixo, a seção 2.1 perdeu a referência à proporcionalidade mínima, os riscos ligados aos requisitos removidos foram ajustados (o R10 passou a tratar das correções de defeitos, e foi incluído o R13, de quebra de comportamento ou de interface na refatoração), e a estratégia de reversão incorporou o fluxo de branches e PRs para a `develop` sugerido nos comentários do documento.

- [x] **Tabela de interfaces:**
  - [x] corrigir `Teller.checkout_articles_from_cart` para **`Teller.checks_out_articles_from`**;
  - [x] incluir `Teller.product_with_name`, `Teller.offers`, `ShoppingCart.items`, `ShoppingCart.product_quantities` e `Receipt.add_product`.
- [x] **Invariantes:**
  - [x] trocar "no máximo um desconto por produto" por **"no máximo um desconto por unidade"**;
  - [x] marcar as invariantes do "2 por valor" e da fração como **comportamento corrigido** (DEF-01 e DEF-02), explicando que até a Fase 4.6 vale o comportamento legado e a partir das Fases 4.7 e 4.8 vale o corrigido;
  - [x] incluir **"cadastrar um combo nunca encarece um carrinho"**.
- [x] **Seção 2.2:** substituir o "algoritmo de otimização" e a "proporcionalidade mínima" pela política descrita neste documento.
- [x] **Preencher a tabela "Ordem das alterações"**, que hoje tem a linha 3 escrita "pensar" e as linhas 4 a 7 vazias, com as Fases 3 a 7 deste plano.
- [x] **Consertar a tabela de critérios de aceitação**, que está com células deslocadas. A "Preservação das funcionalidades" deve apontar para o RNF03.
- [x] **Risco (1):** retirar a mitigação "implementar validações na inclusão de produtos". Ela mudaria o comportamento do legado e não é pedida.
- [x] **Incluir a seção "Decisões registradas"** com D1 a D6.
- [x] **Estratégia de reversão:** citar a tag `legado-baseline` e o fluxo de branches e PRs para a `develop`.

**Pronto quando:** os três documentos estão revisados pelo grupo e estão em `docs/`.

---

## Fase 2: Refazer a linha de base de segurança

> **Edital:** Passo 7 | **Barema:** parte de 1,0 (Bandit, pip-audit e Safety) e parte das Evidências | **Branch:** `chore/seguranca-antes`

**Por que refazer:** o `filelock` vulnerável que aparece na auditoria atual **não é dependência do projeto**. Ao instalar o `requirements.txt` em um ambiente limpo, ele não aparece. Ele veio das ferramentas de auditoria instaladas no mesmo `.venv` do projeto, o que é confirmado pelo motivo `environment-dependency` reportado pelo Safety. Por isso as ferramentas devem rodar em um ambiente separado.

Rodar tudo **sobre a tag `legado-baseline`**, a partir da raiz do repositório:

```bash
git switch --detach legado-baseline

# ambiente das ferramentas FORA de python_pytest
python -m venv ../.venv-audit
../.venv-audit/bin/pip install bandit pip-audit safety

# versões (registrar no documento)
../.venv-audit/bin/bandit --version
../.venv-audit/bin/pip-audit --version
../.venv-audit/bin/safety --version
python --version

D=docs/evidencias/seguranca/antes
mkdir -p $D
../.venv-audit/bin/bandit -r python_pytest/src -f json -o $D/bandit.json
../.venv-audit/bin/bandit -r python_pytest/src -f txt  -o $D/bandit.txt
../.venv-audit/bin/pip-audit -r python_pytest/requirements.txt -f json -o $D/pip-audit.json
../.venv-audit/bin/safety auth login        # registrar se exigiu conta (limitação de acesso)
../.venv-audit/bin/safety scan --target python_pytest --output json > $D/safety.json

git switch develop
```

No Windows, troque `../.venv-audit/bin/` por `..\.venv-audit\Scripts\`.

Registrar em `docs/seguranca_antes_depois.md`:

- [ ] **Ambiente:** versões das ferramentas, sistema operacional, versão do Python e os comandos exatos.
- [ ] **Limitação de acesso:** se o Safety exigiu login ou conta.
- [ ] **Escopo:** por que o Bandit cobriu só o `src/`. Os testes usam `assert`, que gera alertas B101 esperados.
- [ ] **Triagem do `filelock`:** a origem dele e a comparação entre o ambiente contaminado e o ambiente isolado.
- [ ] **Divergência de contagem:** a diferença entre 14 e 13 ocorrências do Safety, ou a constatação de que ela some no ambiente limpo.
- [ ] **Tabela de classificação:**

  | ID | Ferramenta | Pacote ou arquivo | Severidade | Relevância no contexto | Ação | Justificativa |
  |---|---|---|---|---|---|---|

---

## Fase 3: Complementar os testes de caracterização

> **Edital:** Passo 6 | **Branch:** `test/caracterizacao-complemento`

> **Concluída.** A suíte passou de 57 para **64 testes passando e 7 `xfail`**, com 99% de cobertura de ramos no `src/`. Evidências: [`02_pytest_antes_da_refatoracao.log`](evidencias/testes/02_pytest_antes_da_refatoracao.log) e [`02_cobertura_antes.txt`](evidencias/testes/02_cobertura_antes.txt).

- [x] **Teste "carrinho sem combos = legado":** fixar o recibo impresso de alguns carrinhos variados (sem ofertas, com cada tipo de oferta, com produto por peso). Esse teste será repetido depois com combos cadastrados para outros produtos. **Não usem** nesses carrinhos os cenários dos defeitos ("2 por valor" com quantidade ímpar e oferta por grupo ativada com quantidade fracionária). Esses cenários já têm testes próprios, e assim o teste continua válido depois das correções.
  - Feito em [`test_recibos_de_referencia.py`](../python_pytest/tests/test_recibos_de_referencia.py), com 7 cenários. Os carrinhos não usam `shampoo` nem `condicionador`, para que na Fase 6 o teste seja repetido com um combo desses dois produtos cadastrado (cenário 15).
- [x] **Revisar o teste de contrato do enum** [`test_tipos_de_oferta_existentes_e_seus_valores`](../python_pytest/tests/test_comportamento_legado.py). Ele compara com `==` e exige exatamente 4 membros. Se a decisão D5 for seguida, pode ficar como está. Para ter margem de segurança, troquem a comparação por "os 4 membros existentes continuam com os mesmos valores".
  - A comparação passou a ser de subconjunto (`<=`): membros novos são aceitos, mas remover ou renumerar um membro existente continua quebrando o teste.
- [x] **Decidir sobre o `approvaltests`:**
  - **Opção 1:** usá-lo para um *golden master*, com dezenas de carrinhos gerados e os recibos aprovados antes da refatoração. É uma evidência forte de "antes e depois".
  - **Opção 2:** removê-lo na Fase 7, porque hoje nenhum teste o usa.
  - **Decisão: opção 2** (registrada como D7 no [plano de contingência](plano_contingencia.md#8-decisões-registradas)). A suíte já demonstra a preservação de comportamento com 99% de cobertura de ramos e os recibos de referência fixados no próprio teste, legíveis no diff dos PRs. O `approvaltests` não é usado por nenhum teste e traz a maior parte das dependências transitivas do projeto. A remoção é a ação nº 2 do [`seguranca_antes_depois.md`](seguranca_antes_depois.md#7-ações-planejadas) e é executada na Fase 7.
- [x] **Criar os testes do comportamento correto para cada defeito**, marcados com `@pytest.mark.xfail(strict=True, reason="DEF-0X")`. Eles falham enquanto o defeito existe, o que serve de evidência do defeito, e são liberados nos commits `fix:` da Fase 4. Os valores esperados estão na seção 4 do [registro de defeitos](registro_de_defeitos.md).
  - Feito em [`test_defeitos_corrigidos.py`](../python_pytest/tests/test_defeitos_corrigidos.py): 3 casos do DEF-01, 3 do DEF-02 e 1 do DEF-03, este com `raises=AttributeError`. Os valores foram conferidos aplicando as correções em uma cópia descartável do código: os 7 testes passam, os recibos de referência não mudam e só os 7 casos legados previstos no registro de defeitos quebram.
  - Em cada commit `fix:` da Fase 4: remover o `xfail` do teste do defeito e apagar o teste legado correspondente em `test_comportamento_legado.py`.
- [x] **Gerar a cobertura de baseline:**
  ```bash
  cd python_pytest
  python -m coverage run --branch --source=src -m pytest
  python -m coverage report -m > ../docs/evidencias/testes/02_cobertura_antes.txt
  ```
  Referência atual: 99% de cobertura de ramos. As únicas linhas não cobertas são as do stub de banco em `catalog.py`.

**Pronto quando:** a suíte passa e a cobertura de baseline está salva.

---

## Fase 4: Refatoração com padrões de projeto

> **Edital:** Passo 8 | **Barema:** 2,0 (código refatorado) + 2,0 (padrões, SOLID e Clean Code)

A fase é dividida em **duas branches**, para separar mudança de estrutura de mudança de comportamento (decisão D3):

| Parte | Branch | Conteúdo | Comportamento |
|---|---|---|---|
| **4A** | `refactor/politicas-desconto` | Refatoração com padrões de projeto, testes unitários dos padrões e docstrings | Idêntico ao legado |
| **4B** | `fix/defeitos-legado` | Correção de DEF-01, DEF-02 e DEF-03, um commit por defeito | Mudança intencional, documentada no [registro de defeitos](registro_de_defeitos.md) |

A branch 4B só é criada depois do merge da 4A na `develop`. Assim, o PR de refatoração prova sozinho que nada mudou, e o PR de correções mostra só as mudanças de valor previstas.

### Padrões adotados

Cada padrão resolve um problema apontado no diagnóstico, o que atende ao critério do edital de que "padrões artificiais não serão valorizados".

| Padrão | Classe ou função | Problema do diagnóstico que resolve |
|---|---|---|
| **Strategy** | `DiscountPolicy` (interface), com `PercentageOffer` e `GroupPriceOffer`; `BundleOffer` entra na Fase 5 | Switch Statements, violação do OCP, Feature Envy e excesso de responsabilidades no `ShoppingCart` (SRP) |
| **Template Method** | `GroupPriceOffer.apply`, com os ganchos `group_size`, `group_price` e `description` implementados por `ThreeForTwo`, `TwoForAmount` e `FiveForAmount` | **Duplicação** das três fórmulas de grupo e números mágicos |
| **Simple Factory** | `create_policy(offer)`, um dicionário de `SpecialOfferType` para a estratégia | Traduzir o `SpecialOfferType` da API pública em estratégia, preservando o `add_special_offer` |

Os dois padrões exigidos pelo edital são o **Strategy** e o **Template Method**. A fábrica é chamada de *Simple Factory*, e não de *Factory Method* do GoF, porque é uma função com dicionário, e não uma hierarquia de criadores.

### Estrutura implementada

```
src/
├── discount_policies.py   PolicyResult, DiscountPolicy (Strategy), PercentageOffer,
│                          GroupPriceOffer (Template Method), ThreeForTwo, TwoForAmount,
│                          FiveForAmount e create_policy (Simple Factory)
├── discount_engine.py     DiscountEngine: aplica as políticas em sequência e desconta
│                          as unidades consumidas por cada uma
├── shopping_cart.py       só produtos e quantidades; handle_offers vira fachada do engine
└── teller.py              checkout usa o DiscountEngine diretamente
```

```python
class PolicyResult(NamedTuple):
    discounts: list          # descontos concedidos
    consumed: dict           # produto -> unidades usadas pela política


class DiscountPolicy(ABC):                      # Strategy
    @abstractmethod
    def apply(self, available, catalog): ...    # devolve um PolicyResult


class GroupPriceOffer(DiscountPolicy):          # Template Method
    def apply(self, available, catalog):        # algoritmo comum: grupos, sobra, desconto e consumo
        ...

    def number_of_groups(self, quantity_as_int): ...   # gancho com implementação padrão (//)

    @abstractmethod
    def group_size(self): ...

    @abstractmethod
    def group_price(self, unit_price): ...

    @abstractmethod
    def description(self): ...


def create_policy(offer):                       # Simple Factory
    return _POLICY_BY_OFFER_TYPE[offer.offer_type](offer)
```

### 4A: commits da branch `refactor/politicas-desconto`

Em todos os commits desta branch, a suíte passa, os 7 testes `xfail` continuam falhando (os defeitos seguem intactos) e nenhum teste existente é alterado.

| # | Commit | O que muda | Testes |
|---|---|---|---|
| 4.0 | `test: fixa comportamento do legado com quantidade zero` | Teste de caracterização complementar, encontrado durante a refatoração: com quantidade 0, o percentual gera uma linha de 0,00 e as ofertas por grupo não geram desconto. Nenhum teste cobria esse caso | 68 passed, 7 xfailed |
| 4.1 | `refactor: renomeia variáveis e extrai um método por tipo de oferta` | `x` → `group_size`, `p` → `product`, `number_of_x` → `number_of_groups`, `discount_n` → `discount_amount`; um método privado por oferta. No `Teller`, `pq` e `p` viram `item` | 68 / 7 |
| 4.2 | `refactor: introduz DiscountPolicy (Strategy) e PercentageOffer` | Cria `src/discount_policies.py` com a interface e a primeira estratégia | 68 / 7 |
| 4.3 | `refactor: extrai GroupPriceOffer (Template Method) para as ofertas por grupo` | As três fórmulas viram um único algoritmo. **DEF-01 preservado** numa sobrescrita de `number_of_groups` em `TwoForAmount`; **DEF-02 preservado** no cálculo da sobra, marcado com comentário | 68 / 7 |
| 4.4 | `refactor: cria as políticas a partir de SpecialOfferType com uma Simple Factory` | `create_policy(offer)`. Sai o último `if` por tipo de oferta | 68 / 7 |
| 4.5 | `refactor: move a aplicação dos descontos para DiscountEngine` | Cria `src/discount_engine.py`. `ShoppingCart.handle_offers(receipt, offers, catalog)` vira uma **fachada** que mantém o contrato. O `Teller` usa o engine diretamente | 68 / 7 |
| 4.6 | `refactor: políticas informam as unidades consumidas` | `PolicyResult(discounts, consumed)`. O engine trabalha sobre uma cópia das quantidades e desconta o consumo de cada política. Preparação para os combos | 68 / 7 |
| 4.6b | `test: adiciona testes unitários das políticas de desconto e da fábrica` | `tests/test_politicas_de_desconto.py`: fábrica, consumo de cada estratégia e uma oferta fictícia "4 por 3" criada só com os ganchos do Template Method | 79 / 7 |
| 4.10 | `docs: adiciona docstrings PEP 257 ao código de produção` | Docstrings em todos os módulos, classes e métodos públicos do `src/`, incluindo o significado de `Offer.argument` por tipo de oferta | 79 / 7 |

- [x] Commits 4.0 a 4.6b e 4.10 aplicados, com a suíte verificada em cada um.
- [x] Evidências: [`03_pytest_apos_refatoracao.log`](evidencias/testes/03_pytest_apos_refatoracao.log) (79 passed, 7 xfailed) e [`03_cobertura_apos_refatoracao.txt`](evidencias/testes/03_cobertura_apos_refatoracao.txt) (99% de ramos; 100% em `discount_engine.py`, `discount_policies.py` e `shopping_cart.py`).

**4A pronta quando:**
- [x] nenhum teste existente foi alterado: desde a `develop`, a branch só **acrescenta** testes;
- [x] os 7 `xfail` continuam falhando;
- [x] o `handle_offers` não tem mais nenhum `if` por tipo de oferta, e o `shopping_cart.py` não importa mais o `SpecialOfferType`.

### 4B: commits da branch `fix/defeitos-legado`

| # | Commit | O que muda | Testes |
|---|---|---|---|
| 4.7 | `fix(DEF-01): cobra a sobra do 2 por valor a preço cheio` | Remove a sobrescrita de `number_of_groups` em `TwoForAmount`: o "2 por valor" passa a usar a divisão inteira padrão do `GroupPriceOffer`. Remove o `xfail` do teste correto e apaga `test_dois_por_valor_com_quantidade_impar_defeito_legado`: 3 un. → R$ 25,00; 5 un. → R$ 40,00; 7 un. → R$ 55,00 | 79 passed, 4 xfailed |
| 4.8 | `fix(DEF-02): cobra a fração restante nas ofertas por grupo` | Sobra calculada com a quantidade real (`quantity - number_of_groups * group_size`). Remove o `xfail`, move o caso de 2,9 kg para o teste correto, apaga `test_promocao_por_grupo_com_quantidade_fracionaria_legado` e atualiza o recibo impresso: `5 for 7.5 (maca) -2.45` e `Total: 20.96` | 79 / 1 |
| 4.9 | `fix(DEF-03): busca de produto por nome via contrato do catálogo` | Declara `product_with_name` em `SupermarketCatalog`, implementa no `FakeCatalog` e faz o `Teller` delegar ao catálogo. Remove o último `xfail` | 80 passed |

Cada commit `fix:` deve citar na mensagem o ID do defeito e o link para o [registro de defeitos](registro_de_defeitos.md).

**4B pronta quando:**
- [x] só os 7 casos listados no registro de defeitos mudaram de valor esperado;
- [x] não resta nenhum `xfail`;
- [x] o log da suíte depois das correções está salvo em [`04_pytest_apos_correcoes.log`](evidencias/testes/04_pytest_apos_correcoes.log) (80 passed), com a cobertura em [`04_cobertura_apos_correcoes.txt`](evidencias/testes/04_cobertura_apos_correcoes.txt) (99% de ramos).

Commits: `a16de14` (DEF-01), `d06abcc` (DEF-02) e `11c4b76` (DEF-03).

---

## Fase 5: Implementar os combos

> **Edital:** Passo 9 | **Barema:** 0,5 | Evita a penalidade de −2,0 | **Branch:** `feat/combos`

Cada commit traz o código e os testes do que entrega: um PR de funcionalidade sem testes não demonstraria a regra que implementa. Por isso, os cenários de combo previstos para a Fase 6 entraram aqui, e a Fase 6 ficou com a regressão.

| # | Commit | O que muda | Testes |
|---|---|---|---|
| 5.1 | `feat: adiciona BundleOffer, a estratégia de desconto dos combos` | Nova estratégia em `discount_policies.py`. Número de combos = menor `⌊disponível / exigido⌋` entre os produtos do combo (só a parte inteira, para produtos por peso). Gera **um `Discount` por produto**, com a descrição `combo 10% off` (D4), e consome `n × exigido` de cada produto | 87 passed |
| 5.2 | `feat: adiciona Teller.add_bundle_offer e aplica os combos no checkout` | `add_bundle_offer(products, percent=10)`: um produto repetido na lista significa quantidade maior que 1; lista vazia lança `ValueError`. Os combos ficam em `self.bundles`, **sem tocar** em `self.offers` nem no enum (D5). O `DiscountEngine.apply` ganha o parâmetro opcional `bundles` e aplica os combos depois das ofertas | 97 passed |
| 5.3 | `feat: escolhe a ordem de menor total entre ofertas e combos` | O engine calcula a ordem C (ofertas → combos) e a ordem B (combos → ofertas) e fica com o menor total, comparado em centavos; em empate, a C (D1). Uma política cujas unidades já foram todas consumidas é pulada, para não gerar linhas de `0.00`; o caso legado de quantidade zero continua gerando a linha. No recibo, os descontos individuais vêm antes dos de combo. `DiscountPolicy` ganha o método `products()`, usado nessa verificação | 109 passed |

**Decisões tomadas na implementação:**
- **`percent=10`, e não `10.0`.** Com `10.0`, a descrição sairia `combo 10.0% off`, contrariando a D4.
- **Validação só na API nova.** `add_bundle_offer([])` lança `ValueError`. Como a API é nova, a validação não altera nenhum comportamento existente.

### Cenários cobertos (`tests/test_combos.py`)

| # | Cenário | Esperado | Teste |
|---|---|---|---|
| 1 | Combo escova + creme; carrinho 1 + 1 | desconto −2,50; total 22,50 | `test_cenarios_do_roteiro[1_escova_1_creme]` |
| 2 | 2 escovas + 1 creme | −2,50; total 32,50 (escova excedente a preço cheio) | `test_cenarios_do_roteiro[2_escovas_1_creme_excedente_a_preco_cheio]` |
| 3 | 2 escovas + 2 cremes | −5,00; total 45,00 | `test_cenarios_do_roteiro[2_escovas_2_cremes_dois_combos]` |
| 4 | Só 1 escova | sem desconto e sem linha de combo | `test_cenarios_do_roteiro[so_1_escova_combo_incompleto]`, `test_combo_incompleto_nao_gera_linha_de_desconto` |
| 5 | Combo de 2 escovas + 1 creme; carrinho 5 + 3 | 2 combos; desconto −7,00 | `test_combo_que_exige_duas_unidades_do_mesmo_produto` |
| 6 | Escova com "3 por 2"; carrinho 3 + 1 | total 35,00, sem linha de combo | `test_escolhe_a_ordem_de_menor_total[oferta_vence_3_por_2]` |
| 7 | Escova com 20%; carrinho 1 + 1 | total 22,50 | `test_escolhe_a_ordem_de_menor_total[combo_vence_percentual_de_20]` |
| 8 | Escova com "5 por 40"; carrinho 5 + 5 | total 112,50 | `test_escolhe_a_ordem_de_menor_total[combo_vence_5_por_valor]` |
| 9 | Escova com "2 por 15"; carrinho 2 + 2 | total 45,00, com a linha `2 for 15.0` e **sem** linhas de combo | `test_escolhe_a_ordem_de_menor_total[empate_mantem_a_oferta]` |
| 10 | Combos escova + creme e escova + fio; carrinho 1 + 1 + 1 | só o primeiro combo | `test_dois_combos_disputando_o_mesmo_produto_vence_a_ordem_de_cadastro` |
| 11 | Fio dental com "3 por 2" fora do combo | oferta do fio inalterada | `test_oferta_de_produto_fora_do_combo_nao_e_afetada` |
| 12 | Vários carrinhos, com cada tipo de oferta na escova | total com combos ≤ total sem combos; sem combo completo, recibo idêntico | `test_cadastrar_um_combo_nunca_encarece_o_carrinho` |
| 13 | Recibo impresso com combo | texto exato | `test_recibo_impresso_com_combo` |
| 14 | `add_bundle_offer` | `teller.offers` e o enum inalterados | `test_add_bundle_offer_nao_altera_as_ofertas_nem_o_enum` |

Também cobertos: combo vencedor sem linha vazia da oferta substituída, combo usando as unidades que sobram da oferta, produto por peso (parte inteira), percentual informado no cadastro e lista vazia em `add_bundle_offer`.

- [x] Commits 5.1 a 5.3 aplicados, com a suíte verificada em cada um.
- [x] Evidências: [`05_pytest_apos_combos.log`](evidencias/testes/05_pytest_apos_combos.log) (109 passed, 29 deles de combos) e [`05_cobertura_apos_combos.txt`](evidencias/testes/05_cobertura_apos_combos.txt) (99% de ramos; 100% em `discount_engine.py`, `discount_policies.py` e `teller.py`).

**Pronto quando:**
- [x] nenhum teste existente foi alterado: a branch só acrescenta `test_combos.py`;
- [x] os 14 cenários acima passam;
- [x] carrinhos sem combos cadastrados mantêm exatamente o resultado anterior.

---


## Fase 6: Testes de regressão

> **Edital:** Passo 10 | **Barema:** 1,0 | Evita a penalidade de −3,0 | **Branch:** `test/regressao-combos`

Os cenários de combo (1 a 14) entraram na Fase 5, junto com o código. Esta fase cobre a regressão e as evidências finais de testes.

- [x] **Cenário 15: caracterização com combos cadastrados para outros produtos.** Repetir os recibos de referência ([`test_recibos_de_referencia.py`](../python_pytest/tests/test_recibos_de_referencia.py)) com um combo de `shampoo` + `condicionador` cadastrado. Esses produtos não aparecem nos carrinhos de referência, então os recibos devem continuar idênticos.
- [x] **Evidências em `docs/evidencias/testes/`:**
  - [x] `06_pytest_final.log`
  - [x] `06_cobertura_final.txt`
- [x] **Tabela comparativa em `docs/evidencias_testes.md`:**

  | Métrica | Legado (início) | Depois |
  |---|---|---|
  | Testes | 1 (original) / 57 (caracterização) | 118 |
  | Aprovados | 57 | 118 |
  | Cobertura de ramos (`src/`) | 99% | 99% |
  | Casos alterados de propósito | — | 7 (DEF-01: 3; DEF-02: 4) |
  | Testes novos de defeitos | — | 1 (DEF-03) |
  | Defeitos corrigidos | 0 de 3 | 3 de 3 |

---

## Fase 7: Reavaliação de segurança

> **Edital:** Passo 11 | **Barema:** restante de 1,0 | **Branch:** `chore/seguranca-depois`

- [x] **Fixar as versões no `requirements.txt`** (por exemplo, `pytest==9.2.0`, `coverage==7.17.3`), para a instalação ser reproduzível (RNF08).
- [x] **Rodar os mesmos comandos da Fase 2** sobre a `develop`, com saída em `docs/evidencias/seguranca/depois/`.
- [x] **Montar o comparativo de antes e depois** em `docs/seguranca_antes_depois.md`:
  - achados que sumiram e o motivo;
  - achados novos, se houver;
  - **riscos remanescentes**: o uso de `float` para dinheiro e as limitações da análise estática e das bases de vulnerabilidades.
- [x] **Incluir as ressalvas exigidas pelo edital:**
  - a ausência de alertas não prova que o sistema é seguro;
  - nenhuma dependência foi adicionada só para gerar resultado nas ferramentas.

---

## Fase 8: Documento de padrões de projeto

> **Edital:** entregável 5.5 | **Barema:** parte dos 2,0 de padrões | **Arquivo:** `docs/padroes_projeto.md`

- [x] **Diagramas de classes de antes e depois**, em Mermaid, que o GitHub renderiza:
  ```mermaid
  classDiagram
      class DiscountPolicy {
          <<interface>>
          +apply(available, catalog) PolicyResult
      }
      DiscountPolicy <|.. PercentageOffer
      DiscountPolicy <|.. GroupPriceOffer
      DiscountPolicy <|.. BundleOffer
      GroupPriceOffer <|-- ThreeForTwo
      GroupPriceOffer <|-- TwoForAmount
      GroupPriceOffer <|-- FiveForAmount
      DiscountEngine --> DiscountPolicy
      Teller --> DiscountEngine
      ShoppingCart ..> DiscountEngine : handle_offers (fachada)
  ```
- [x] **Para cada padrão (Strategy, Template Method e Factory):**
  - o problema que resolve, com referência ao diagnóstico;
  - o trecho de código antes e depois;
  - os testes que o exercitam.
- [x] **Seção de SOLID:**
  - **SRP:** o carrinho só guarda itens; o cálculo de descontos foi para as políticas e o engine.
  - **OCP:** os combos entraram sem alterar as estratégias existentes.
  - **LSP:** toda `DiscountPolicy` pode ser trocada por outra no engine.
  - **DIP:** o engine depende da abstração `DiscountPolicy`, não dos tipos concretos.
- [x] **Benefício do Template Method nas correções:** o DEF-02 estava replicado em três blocos do legado, e depois da refatoração foi corrigido em um único método.
- [x] **Demonstração de extensibilidade:** quantas linhas do código existente foi preciso alterar para adicionar os combos (`git diff --stat` da Fase 5).

---

## Fase 9: README e evidências finais

> **Edital:** entregável 5.9 | **Barema:** 0,5 (Evidências) + 0,5 (README) | **Branch:** `docs/readme`

A fase altera documentação e o `.gitignore` e acrescenta um script de exemplo, `python_pytest/exemplo_de_uso.py` (decisão 5). O `src/` e o `tests/` não mudam, e a suíte continua com 118 testes passando em todos os commits.

### Decisões da fase

| # | Decisão | Escolha |
|---|---|---|
| 1 | Integrantes | Felipe Nogueira, Lucas Choucate, Júlia Gaglianone, Ramon Papes e Suianne Martins |
| 2 | Ambiente | Não há um ambiente de referência único: o projeto deve rodar em **qualquer sistema operacional** com **Python 3.10 ou superior**, o mínimo exigido pelo `pytest==9.2.0`. O README traz os comandos para Linux, macOS e Windows e lista os ambientes em que a suíte já foi executada, com a evidência de cada um |
| 3 | Lições aprendidas, elemento da seção 6 do edital que ainda não existe | Seção curta no próprio README |
| 4 | `python_pytest/README.md`, que repete os comandos de instalação | Manter a descrição original do kata e trocar o conteúdo da seção *Setup* por um link para o README da raiz, para que haja uma única versão dos comandos. O título *Setup* fica, como no original do kata. A seção 8 do [`seguranca_antes_depois.md`](seguranca_antes_depois.md#8-resultados-depois-da-modernização), que apontava para `python_pytest/README.md#setup`, passa a apontar para a seção 4.2 do README da raiz, onde está o passo de atualização do `pip` |
| 5 | Como executar o exemplo de uso em qualquer sistema operacional | Um script, `python_pytest/exemplo_de_uso.py`, que inclui `src/` e `tests/` no caminho de importação a partir da própria localização. Assim ele roda com um único comando, sem a variável `PYTHONPATH`, cujo separador muda entre Linux (`:`) e Windows (`;`). O pytest não o coleta, porque o nome não segue o padrão `test_*.py` |

### Commits

Preparação:

```bash
git switch develop
git pull --ff-only
git switch -c docs/readme
```

| # | Commit | O que muda |
|---|---|---|
| 9.0 | `docs: detalha o passo a passo da Fase 9 no plano de execução` | Esta seção |
| 9.1 | `chore: ignora os arquivos de cobertura` | `.coverage` e `htmlcov/` no `python_pytest/.gitignore`. Sem isso, quem segue o README e roda a cobertura fica com um `.coverage` não rastreado |
| 9.2 | `docs: reescreve o README da raiz com objetivo, ambiente e instalação` | Seções 1 a 4 do roteiro abaixo |
| 9.3 | `docs: inclui no README os testes, a cobertura e um exemplo de uso` | Seções 5 e 6, e o script `python_pytest/exemplo_de_uso.py` (decisão 5) |
| 9.4 | `docs: inclui no README a análise de segurança` | Seção 7 |
| 9.5 | `docs: inclui no README a estrutura de pastas e os documentos` | Seção 8 |
| 9.6 | `docs: inclui no README as decisões, os padrões e os defeitos corrigidos` | Seções 9 a 11 |
| 9.7 | `docs: inclui no README as lições aprendidas e as limitações` | Seção 12 |
| 9.8 | `docs: aponta o README do python_pytest para o README da raiz` | Decisão 4, incluindo o link da seção 8 do `seguranca_antes_depois.md` |
| 9.9 | `docs: registra a execução do README em ambiente limpo` | `docs/evidencias/testes/07_execucao_independente.log` e uma linha nova em `evidencias_testes.md` |
| 9.10 | `docs: completa a rastreabilidade dos requisitos` | Seção 5 de `requisitos.md` |
| 9.11 | `docs: marca a Fase 9 como concluída no plano de execução` | Checkboxes das Fases 0, 2 e 9 e o bloco "Situação atual" |

Depois do 9.11: push, PR para a `develop` e revisão por outro integrante, de preferência quem usa Windows, que também refaz o 9.9 no PowerShell.

### Roteiro do README (commits 9.2 a 9.7)

1. **Objetivo:** modernização do legado (caracterização, refatoração com padrões de projeto, combos e segurança), com a disciplina e o professor.
2. **Integrantes** (decisão 1).
3. **Créditos:** kata original de Emily Bache, licença MIT ([`license.txt`](../license.txt)). O README original sai, então a atribuição precisa ficar.
4. **Ambiente e instalação:** Python 3.10 ou superior em qualquer sistema operacional (decisão 2), com a tabela dos ambientes já verificados; `git clone`; `venv`; atualização do `pip` (alertas A-02 e A-03); `pip install -r requirements.txt`; conferência com `pytest -q`. Um bloco para Linux e macOS e outro para Windows, sem depender da ativação do ambiente virtual.
5. **Testes e cobertura:** `pytest -v`; `coverage run --branch --source=src -m pytest` e `coverage report -m`; o resultado esperado (118 aprovados e 99% de cobertura de ramos); uma tabela com os 6 arquivos de teste e o que cada um cobre.
6. **Exemplo de uso:** o código não tem ponto de entrada além dos testes, então o `exemplo_de_uso.py` mostra o sistema rodando fora do pytest: escova e creme dental em combo e maçã com 20%, total `34.90`. O script usa o `FakeCatalog` e o `ReceiptPrinter` de `tests/`, porque o `SupermarketCatalog` é um stub de banco, e roda com `.venv/bin/python exemplo_de_uso.py` ou `.venv\Scripts\python.exe exemplo_de_uso.py` (decisão 5).
7. **Análise de segurança:** ambiente separado em `../.venv-audit` e o motivo (o caso do `filelock`); os comandos das três ferramentas, instaladas nas versões da análise registrada (`bandit==1.9.4`, `pip-audit==2.10.1` e `safety==3.8.1`); o Safety exige conta (com `--headless` para terminais sem navegador), e a primeira execução é interativa; resumo de antes e depois, com link para [`seguranca_antes_depois.md`](seguranca_antes_depois.md); as ressalvas do edital. **Os comandos do README mostram o resultado no terminal e não escrevem em `docs/evidencias/seguranca/`**, para que ninguém sobrescreva a evidência oficial ao seguir o README.
8. **Estrutura de pastas:** a árvore do repositório (incluindo o `exemplo_de_uso.py`) e uma tabela de documento → entregável do edital: diagnóstico (5.1), requisitos (5.2), plano de contingência (5.3), padrões de projeto (5.5), segurança (5.8) e evidências de testes (5.9), além do registro de defeitos e deste plano.
9. **Arquitetura e padrões:** o problema do legado; Strategy, Template Method, Simple Factory, o `DiscountEngine` e a fachada `handle_offers`; uma versão simplificada do diagrama Mermaid "depois" de [`padroes_projeto.md`](padroes_projeto.md); um resumo do SOLID; e as interfaces públicas preservadas.
10. **Regra dos combos e decisões D1 a D7:** a fórmula, a tabela "Quem vence" e uma linha por decisão, com link para a [seção 8 do plano de contingência](plano_contingencia.md#8-decisões-registradas).
11. **Defeitos corrigidos:** tabela de DEF-01 a DEF-03 (cenário, valor no legado, valor corrigido e commit), com link para o [registro de defeitos](registro_de_defeitos.md).
12. **Lições aprendidas e limitações:** separar refatoração de correção (D3); isolar as ferramentas de auditoria (`filelock`); remover a dependência sem uso (D7: de 22 para 6 pacotes auditados); o `float` como risco remanescente; a escolha da ordem feita para o carrinho inteiro; o Safety dependente de conta; as evidências geradas em ambientes diferentes. No mesmo commit, acrescentar à seção 8 do README uma frase que relacione os documentos aos elementos da documentação inspirada no MPS.BR (seção 6 do edital), apontando as lições aprendidas para a nova seção.

### 9.9: testar o README do zero

Clonar a partir do repositório local, para que só o que foi commitado entre no teste. Um arquivo não rastreado que faz o projeto funcionar na máquina de quem desenvolve não aparece no clone.

```bash
git clone --branch docs/readme "$PWD" ../kata-limpo
cd ../kata-limpo
```

- Copiar os comandos **do próprio README**, e não de memória.
- Se algum passo falhar ou exigir algo que o README não diz, corrigir o README em um novo commit e recomeçar de um clone novo.
- Salvar em `docs/evidencias/testes/07_execucao_independente.log`, no repositório original: o commit testado (`git log -1 --oneline`), o sistema operacional, o `python --version`, a saída do `pytest -v` e o relatório de cobertura.
- Rodar também os comandos de segurança do README. O esperado é 0 ocorrências no Bandit e 0 vulnerabilidades no pip-audit. Não salvar esses resultados como evidência nova.
- No fim, o `git status --short` do clone deve sair vazio, o que prova que o `.gitignore` cobre `.venv`, `.coverage` e `.pytest_cache`. Depois, apagar o `../kata-limpo`.
- Repetir a instalação e os testes em cada versão do Python, da 3.10 à mais recente disponível, para comprovar o mínimo declarado no README. Uma forma de obter as versões é o `uv` (`uv python install 3.10`; `uv python find 3.10` mostra o caminho do interpretador, que substitui o `python3` no comando do `venv`). Registrar o resultado no mesmo log e acrescentar a linha correspondente na tabela de ambientes do README. Uma execução preliminar, em 25/11/2026 no Ubuntu 24.04, passou com 118 testes nas versões 3.10.21, 3.11.16, 3.12.3, 3.13.15 e 3.14.6.
- No Windows, outro integrante refaz a instalação e os testes pelo PowerShell (log opcional: `07_execucao_independente_windows.log`). Se alguém do grupo tiver macOS, repetir também nele.
- Incluir a execução na seção 3 de [`evidencias_testes.md`](evidencias_testes.md) e ajustar a seção 7, que fala dos ambientes.

### 9.10: completar a rastreabilidade

Hoje a tabela da seção 5 de [`requisitos.md`](requisitos.md) não tem RNF04 a RNF08. Proposta:

| ID | Arquivo / classe | Testes | Evidência |
|---|---|---|---|
| RNF04 | `discount_engine.py` | `test_ofertas_de_produtos_diferentes_coexistem_na_mesma_compra`, `test_escolhe_a_ordem_de_menor_total`, `test_cadastrar_um_combo_nunca_encarece_o_carrinho` | `06_pytest_final.log` |
| RNF05 | `python_pytest/tests/` (118 testes) | Suíte completa | Logs 01 a 06, coberturas 02 a 06 e `evidencias_testes.md` |
| RNF06 | `src/` em inglês com docstrings PEP 257; testes e documentos em português | Inspeção | Commit `703bc9d` e as [regras gerais](#regras-gerais) |
| RNF07 | Não se aplica | Inspeção | `seguranca_antes_depois.md` e `evidencias/seguranca/antes` e `depois` |
| RNF08 | `README.md` e `requirements.txt` com versões fixadas | Execução do README do zero | `07_execucao_independente.log` |

Além disso:

- incluir o `06_pytest_final.log` como evidência final em todas as linhas;
- citar o cenário 15 (`test_recibo_de_referencia_com_combo_de_outros_produtos`) no RF11 e no RNF03;
- reescrever a abertura da seção 5, que ainda diz que as colunas "são completadas ao longo das Fases 4 a 6".

Depois da edição, conferir que todo teste citado existe:

```bash
for t in $(grep -oE '`test_[a-z0-9_]+(\[|`)' docs/requisitos.md | tr -d '`[' | sort -u); do
  grep -rqE "def $t\b" python_pytest/tests || echo "não existe: $t"
done
```

O 9.10 não depende do README e pode ser feito em paralelo, exceto a linha do RNF08, que usa o log do 9.9.

### 9.11: atualizar o plano

- **Fases 0 e 2:** marcar os checkboxes. Os itens já estão feitos: a tag `legado-baseline` está no remoto, o `*:Zone.Identifier` está no `.gitignore`, a estrutura de pastas existe, o log do Windows em UTF-16 foi removido e o [`seguranca_antes_depois.md`](seguranca_antes_depois.md) tem os seis itens pedidos, incluindo o `filelock` e a divergência entre 14 e 13 ocorrências.
- **Fase 9:** marcar os itens abaixo e registrar os hashes dos commits.
- **"Situação atual"**, no início do documento: Fases 0 a 9 concluídas; falta a Fase 10.

**Pronto quando:**

- [ ] os commits 9.0 a 9.11 foram aplicados, com 118 testes passando em cada um;
- [ ] o `README.md` da raiz, que hoje é o original do kata, em inglês, foi reescrito e tem:
  - [ ] objetivo do trabalho e integrantes;
  - [ ] requisitos de ambiente: Python 3.10 ou superior, em qualquer sistema operacional;
  - [ ] instalação para Linux, macOS e Windows (`venv`, atualização do `pip`, `pip install -r requirements.txt`);
  - [ ] como rodar os testes e a cobertura, e um exemplo de uso;
  - [ ] como rodar o Bandit, o pip-audit e o Safety, com o ambiente separado;
  - [ ] estrutura de pastas;
  - [ ] decisões arquiteturais (D1 a D7) e padrões adotados, com links para a pasta `docs/`;
  - [ ] seção "Defeitos corrigidos", resumindo DEF-01 a DEF-03 e apontando para o registro de defeitos;
  - [ ] lições aprendidas e limitações;
- [ ] o README foi testado do zero em um clone limpo, que é o critério "execução independente" do barema: 118 aprovados, 99% de cobertura, `git status` vazio e log salvo;
- [ ] os links do README funcionam no GitHub (as âncoras com acento só podem ser conferidas lá), e o diagrama Mermaid aparece desenhado;
- [ ] a rastreabilidade cobre RF01 a RF14, RF16 e RNF01 a RNF09 (RF → implementação → teste → evidência), com os nomes de teste conferidos.

---

## Fase 10: Apresentação e entrega

> **Edital:** entregável 5.10 | **Arquivo:** `apresentacao/slides.pdf`

Roteiro sugerido para 10 a 15 minutos:

1. **O problema inicial:** um sistema legado com ofertas concentradas no `handle_offers`.
2. **O diagnóstico:** os principais smells e as violações de SOLID, com trechos de código.
3. **O plano e os riscos:** ordem das alterações e estratégia de reversão (tag e branches).
4. **Testes de caracterização e defeitos:** 57 testes, 99% de cobertura, os **3 defeitos encontrados** e como cada um foi corrigido (tabela de antes e depois do registro de defeitos).
5. **Os padrões e o SOLID:** Strategy, Template Method e Factory, com o diagrama de antes e depois.
6. **A regra dos combos e a política de convivência:** a tabela "Quem vence".
7. **Resultados dos testes:** o comparativo de antes e depois.
8. **Segurança:** as três ferramentas, a triagem e o **caso do `filelock`**.
9. **Lições aprendidas e limitações:** separar refatoração de correção, a escolha por carrinho inteiro na política de combos e o uso de `float` como risco remanescente.

Fechamento:

- [ ] Fazer o merge da `develop` na `main` por PR.
- [ ] Criar a tag `v1.0-entrega` e publicá-la no remoto.

---

## Checklist anti-penalidade

| Penalidade do edital | Valor | Coberta na fase |
|---|---|---|
| Diagnóstico técnico ausente | −3,0 | 1.1 |
| Plano de contingência ausente | −3,0 | 1.3 |
| Testes automatizados ausentes | −3,0 | 3 e 6 |
| Código final não executa | nota máxima 5,0 | Suíte passando em todo commit; README testado (9) |
| Quebra injustificada de regras ou interfaces | −2,0 | Testes de contrato preservados; D5; as únicas mudanças de regra são as correções DEF-01 a DEF-03, isoladas em commits próprios e justificadas no registro de defeitos |
| Regra de combos incorreta ou ausente | −2,0 | 5 e 6 |
| Faltar os dois padrões exigidos | zero no critério | 4 e 8 |
| Faltar a análise das três ferramentas | zero no critério | 2 e 7 |

---

## O que pode andar em paralelo

```
Fase 0 ──┬── Fase 1 (documentos) ─────────────┐
         ├── Fase 2 (segurança antes) ────────┤
         └── Fase 3 (testes complementares) ──┴── Fase 4 ── Fase 5 ── Fase 6 ──┬── Fase 7 ──┐
                                                                               └── Fase 8 ──┴── Fase 9 ── Fase 10
```

- **Fases 1, 2 e 3:** podem ser feitas por pessoas diferentes ao mesmo tempo, logo depois da Fase 0.
- **Fases 4 a 6:** são **sequenciais**, porque cada commit depende do anterior. O ideal é uma pessoa conduzindo e outra revisando os PRs.
- **Fases 7 e 8:** podem andar em paralelo assim que a Fase 6 terminar.
