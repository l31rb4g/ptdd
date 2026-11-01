---
name: organizar-specs
description: Reorganiza a estrutura das specs — renomeia, cria, remove e reordena seções e subseções, e move bullets entre elas — sem NUNCA alterar o texto de um bullet. Use quando o usuário pedir para "organizar as specs", "arrumar as seções", "reorganizar/normalizar as specs", "padronizar as specs", ou invocar /organizar-specs.
---

# Organizar specs

Arruma a **estrutura** das specs: vocabulário de seções, nível de heading,
ordem, indentação e em qual seção cada bullet mora. O **texto** dos bullets é
intocável.

> Atenção: esta skill **edita `specs/`** — é a exceção ao fluxo do
> `implementar-specs`, que nunca toca na spec. Aqui a spec é o objeto, mas só a
> moldura dela.

## Regra de ouro

**Um bullet nunca é criado, apagado ou reescrito. Nem uma vírgula. Nem para
consertar um erro de digitação.**

Bullets só **mudam de lugar**. Se você achar um typo, uma regra contraditória ou
uma linha ambígua, **reporte ao usuário** — não conserte.

A unidade de movimento é o **bloco**: um bullet mais tudo que está aninhado
abaixo dele. O bloco anda inteiro ou não anda. **Nunca desaninha um filho do
pai** — isso destrói o significado (`- Cores dos labels:` sem os filhos não quer
dizer nada).

Cuidado: bullets quebram em várias linhas. As linhas de continuação (as que não
começam com `- ` e não são heading) fazem parte do bullet:

```markdown
- Como funciona o FakeMail: quando o backend quiser disparar um e-mail, vai enviar um sinal para o front-end
  via websocket; ao receber, o front-end vai abrir uma popup no canto inferior direito
```

Isso é **um** bullet, não três linhas.

## Livre × congelado

| | |
|---|---|
| **Livre** | Nome de seção; nível de heading (`#`, `##`, `###`); ordem das seções; indentação; em qual seção/subseção cada bloco mora |
| **Congelado** | O texto de todo bullet, e a estrutura de aninhamento dentro do bloco |

Prosa e tabelas fora de bullets também não são verificadas: não as mova nem as
edite como efeito colateral. Se um bloco depende de um parágrafo de contexto,
mova o parágrafo junto ou pergunte.

## Taxonomia

A **fonte única** da taxonomia é o próprio verificador
(`.claude/skills/organizar-specs/verificar.py`, constante `CANONICAS`). Não
duplique a lista aqui.

Seções `##` canônicas, na ordem em que devem aparecer — **todas opcionais**, a
spec só tem as que precisa:

`Objetivo` → `Fora do escopo` → `Comportamento` → `Regras` → `Interface` →
`Status` → (seções próprias) → `Dados / API` → `Implementação`

Regras:

- **Seções próprias** (`## <Assunto>`, ex.: `## Equipe`, `## API Keys`,
  `## Login`, `## Testes`) são bem-vindas, desde que venham **depois** de todas
  as canônicas de conteúdo e **antes** de `Dados / API`. Não são "erro de
  taxonomia".
- Só o nível `##` é canônico. Subseções `###` são livres — crie, renomeie e
  agrupe como fizer sentido (ex.: `### Front-end`, `### Labels`).
- O H1 (`# Nome`) é o título, sempre o primeiro heading, e deve bater com o nome
  do arquivo.
- Seção não-canônica que na verdade é uma canônica com outro nome: renomeie. Se
  não for, posicione na faixa das seções próprias.
- Seção canônica vazia fica onde está.

Todo arquivo de spec usa a extensão **`.pt`**.

## Passos

### 1. Baseline

Antes de tocar em qualquer coisa:

```bash
python3 .claude/skills/organizar-specs/verificar.py
```

Isso compara o disco com `HEAD` e lista o que está fora do padrão. O script
**recusa rodar** (exit 2) se o repositório não tiver nenhum commit — sem baseline
não existe prova. Nesse caso, peça ao usuário para commitar o estado atual antes
de reorganizar.

Se acusar `bloco alterado/removido` ou arquivo fora da baseline, **pare** — a
árvore já estava suja antes de você começar. Resolva isso primeiro (pergunte ao
usuário) para não misturar a sua reorganização com uma alteração que não foi sua.

### 2. Um arquivo por vez

Para cada arquivo, leia **inteiro** e monte o plano antes de escrever:

- Quais headings existem hoje e qual o destino de cada um na taxonomia.
- Para cada bloco, em que seção/subseção ele deveria morar.
- Quais `###` agrupam melhor o conteúdo.

Quando estiver em dúvida se um bloco pertence a `## Comportamento` ou
`## Regras`, **não decida sozinho** — os dois parecem regra e a diferença importa.
Na dúvida, pergunte, ou deixe onde estava.

### 3. Escrever

Reconstrua o arquivo (Write) copiando cada bloco **verbatim**, só mudando
headings, ordem e indentação. Não é para "melhorar" o texto no caminho.

### 4. Verificar

```bash
python3 .claude/skills/organizar-specs/verificar.py
git diff specs
```

O script é a prova: ele reprova (`exit 1`) se um único bullet apareceu,
desapareceu ou mudou de texto, e aponta exatamente qual. Ele também acusa seção
fora do vocabulário/ordem, seção duplicada, seção própria fora do lugar, H1 a
mais, e avisa se o título não bate com o nome do arquivo. **Não reporte tarefa
concluída com o verificador vermelho.**

Opções úteis:

```bash
python3 .claude/skills/organizar-specs/verificar.py specs/componentes/Pagina.pt   # um arquivo
python3 .claude/skills/organizar-specs/verificar.py --base HEAD~1                   # outra baseline
python3 .claude/skills/organizar-specs/verificar.py --so-conteudo                   # ignora taxonomia
```

### 5. Reportar

Diga: quais arquivos mudaram, quantos blocos mudaram de seção, e quais decisões
de taxonomia você tomou por conta própria (para o usuário confirmar). Liste
também os typos/ambiguidades que você **não** consertou.

## Cuidado: isso polui o diff do `implementar-specs`

O `implementar-specs` descobre o que implementar lendo o diff de `specs/`. Uma
reorganização estrutural suja esse diff inteiro — e uma mudança semântica de
verdade fica invisível no meio de 300 linhas movidas.

**Sempre commite a reorganização sozinha, antes de qualquer edição semântica da
spec.** Se o usuário já tiver uma alteração de conteúdo não commitada em
`specs/`, avise antes de reorganizar por cima.

## Observações

- Não renomeie arquivos de spec por conta própria: o nome do arquivo é o nome do
  artefato e precisa bater com o H1. Renomear só se o usuário pedir, e junto com
  o H1.
- Não mexa em `specs/` de outro jeito que não seja estrutura: nada de reescrever
  regra, fundir bullets, corrigir contradição.
- Se o usuário pedir explicitamente para alterar o conteúdo de uma regra, isso
  **não** é esta skill — é uma edição de spec do usuário, seguida de
  `/implementar-specs`.
