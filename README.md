# Formato da pasta `specs/`

Mini guia do formato das specs: como a pasta se organiza, o que vai em cada
arquivo e como escrever os bullets. Nada aqui é específico de um produto.

## Papel da pasta

- `specs/` é a **fonte da verdade** do projeto: o código é a implementação dela.
- Quando código e spec divergem, o que muda é o **código**. Spec não se "ajusta"
  ao que foi implementado.
- A spec diz **o que** o sistema faz e **quais regras valem** — o *como* só
  aparece nas seções que existem justamente para isso (`Dados / API`,
  `Implementação`).
- Spec é versionada junto com o código: o diff das specs mostra a intenção antes
  da implementação.

## Organização dos arquivos

```
specs/
├── <Produto>.pt                   # spec mestra (na raiz de specs/)
├── paginas/<area>/<NomePagina>.pt
├── componentes/<NomeComponente>.pt
└── <area>/<Nome>.pt               # outros agrupamentos (ex. painel administrativo)
```

- **Um artefato, um arquivo.** Cada página, componente ou painel tem o seu.
- **Nome do arquivo = nome do artefato**, em PascalCase, sem espaços
  (`EditarPagina.pt`, `CardPaginas.pt`).
- **A pasta é o lugar do artefato na aplicação**: páginas agrupadas por área
  (pastas em minúsculas, um nível), componentes num diretório só.
- **A mestra** leva o nome do produto e concentra o que é global: objetivo,
  fora do escopo, comportamento e regras gerais, interface geral, dados/API, e
  os temas transversais (contas, assinatura, integrações, testes).
- Regra de negócio não mora em README, wiki nem comentário: mora em `.pt`.
- Nunca duplique regra. Se vale para todo o sistema, fica na mestra; o arquivo
  do artefato só repete o que é específico dele.

## Anatomia de um arquivo

- A **primeira linha** é `# <Nome do artefato>`, idêntico ao nome do arquivo.
- Depois, só seções `##` com títulos do vocabulário canônico:

| Seção | O que entra |
|---|---|
| `## Objetivo` | Uma frase: para que o artefato existe. |
| `## Fora do escopo` | O que ele **não** cobre (evita suposição de quem lê). |
| `## Comportamento` | Dinâmica: o que acontece quando, em que ordem, em reação a quê. |
| `## Regras` | Obrigações, proibições e invariantes. |
| `## Interface` | O que aparece na tela: layout, elementos, estados, variações. |
| `## Status` | Enumerações de estado do domínio e o que cada uma significa. |
| `## Dados / API` | Endpoints, payloads, persistência, formatos. |
| `## Implementação` | Restrições técnicas que a solução precisa respeitar. |

- **Ordem**: `Objetivo` → `Fora do escopo` → `Comportamento` → `Regras` →
  `Interface` → `Status` → seções próprias → `Dados / API` → `Implementação`.
- **Seções próprias** (`## <Assunto>`) são bem-vindas quando o artefato tem um
  assunto que não cabe em nenhuma das canônicas — ex. `## Equipe`, `## API Keys`,
  `## Aviso por Telegram`. Elas vêm depois das canônicas de conteúdo (até
  `Status`) e antes de `Dados / API`.
- **Só inclua a seção se ela tiver conteúdo**; um arquivo pode ter apenas
  `## Objetivo`. Uma seção vazia (só o título) funciona como placeholder de
  "ainda não especificado" — use com parcimônia.
- Subdivisões usam `###` dentro da seção (ex. `### Mobile` dentro de
  `## Interface`), não um arquivo novo.

## Como escrever os bullets

- **Um bullet = uma regra verificável.** Frase direta, declarativa ou
  imperativa: "Deve exibir...", "Não pode ser fechado", "A altura deve
  respeitar o grid".
- **Idioma único** no projeto inteiro, com o vocabulário do domínio.
- **Caixa alta para invariantes fortes**: SEMPRE, NUNCA, TODOS, TUDO, APENAS.
  Se tudo está em caixa alta, nada está.
- **Recuo de 2 espaços por nível**, sempre com `-`.
- Use sub-listas para alternativas e condições:
  ```
  - Se o plano for X:
    - Exibe o botão A
    - Oculta o botão B
  ```
- **Números explícitos**: prazos, limites, tamanhos e quantidades sempre com
  valor concreto. "Resposta rápida" não é regra; "em até 2 segundos" é.
- **Escreva o comportamento observável**, não a solução: nomes de classes,
  tabelas e funções internas ficam de fora — exceto em `Implementação` e
  `Dados / API`, onde a restrição técnica é o próprio requisito.
- Ao citar outro artefato, cite **pelo nome dele**, não pelo caminho do arquivo
  de código.
- Bullets curtos. Regra longa com "e" no meio costuma ser duas regras — separe.

## Exemplo mínimo

```
# Relatorio

## Objetivo
Oferecer uma página com o resumo de vendas do período.

## Regras
- Deve aceitar um período de no máximo 90 dias
- NUNCA exibir dados de outra conta

## Interface
- Deve exibir o total vendido e a quantidade de pedidos
- Se não houver venda no período, exibe estado vazio com o texto "Sem vendas"

## Dados / API
- GET /api/v1/relatorio?de=&ate=

## Implementação
- Deve ser somente leitura
```

## Ciclo de vida

1. A mudança **começa na spec**: edita-se o `.pt` (ou cria-se o arquivo do
   artefato novo, com o nome que ele terá no sistema).
2. O código é ajustado até bater com a spec — nunca o contrário.
3. Spec ambígua é dúvida a resolver com quem pediu, não requisito a inventar.
4. O "porquê" histórico e a discussão ficam no git; a spec guarda só o que vale.

## Erros comuns

- Descrever a solução (bibliotecas, SQL, nomes de classes) em vez da regra.
- Deixar regra implícita só no código.
- Criar uma seção guarda-chuva (`## Observações`) em vez de usar os títulos
  canônicos.
- Título do arquivo diferente do nome do artefato, ou nome do artefato diferente
  do que existe no sistema.
- Bullet com duas regras juntas: não dá para marcar como cumprida.
- Repetir na página uma regra que já está na mestra.

