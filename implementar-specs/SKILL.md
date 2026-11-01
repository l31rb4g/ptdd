---
name: implementar-specs
description: Vê o que mudou nas specs com o diff de `specs/` e implementa a mudança no código, sem nunca editar a spec. Use quando o usuário editar uma spec e pedir para "implementar a spec", "aplicar o diff das specs", "fazer o que a spec pede", ou invocar /implementar-specs.
---

# Implementar specs

Fluxo Spec-Driven: a spec é a **fonte da verdade**; o código é a implementação
dela. Esta skill lê o que mudou em `specs/` e materializa no código.

## Regra de ouro

**NUNCA edite nada em `specs/`.** Ela é a fonte da verdade (AGENTS.md). Se o
código e a spec divergirem, quem muda é o código — a spec não se "ajusta" pra
bater com a implementação. Se a spec estiver ambígua, **pergunte**, não invente.

## Passos

### 1. Ver o que mudou na spec

Comece pelo estado do diretório, porque `git diff` **não mostra spec nova que
ainda não foi rastreada**:

```bash
git status --short specs
git diff specs
```

Se houver arquivo novo não rastreado (`??`), use `git add -N specs` para que ele
apareça no diff, ou leia o arquivo direto.

Se o diff vier vazio, tente as variações (na ordem), pra pegar o que já foi pro
index ou já commitado:

```bash
git diff --cached specs      # mudanças já staged
git diff HEAD -- specs       # staged + working tree
git log -p -3 -- specs       # o que mudou nos últimos commits
```

Se **tudo** vier vazio, não há spec nova pra implementar: avise o usuário e
pergunte se a spec foi salva/commitada, em vez de sair mexendo no código.

### 2. Ler a spec inteira

Para cada arquivo que apareceu no diff, leia o **arquivo atual completo** (não só
o diff) — o diff diz *o que* mudou, o arquivo diz *o contexto*. Mapeie as seções:

- `Objetivo` / `Comportamento` → o que o sistema deve fazer
- `Regras` → invariantes (o que **não** pode acontecer)
- `Interface` / `Status` → UI, estados e o que cada estado significa
- `Dados / API` → contrato RESTful, payloads, Swagger
- `Implementação` → notas técnicas e restrições
- seções próprias (`## <Assunto>`) → regras específicas daquele assunto

No diff, as linhas `-` são o comportamento **antigo** (a remover) e as `+` são o
**novo requisito** (a implementar).

### 3. Achar o código governado

Não presuma caminho: descubra. A própria spec aponta o alvo.

- O nome do arquivo é o nome do artefato. Busque por esse nome no código.
- `## Implementação` e `## Dados / API` costumam nomear arquivos, endpoints,
  tabelas, rotas e componentes — use o que estiver lá.
- Se a spec for a mestra (`specs/*.pt` na raiz), o alvo é uma regra transversal:
  procure no código pela regra descrita e confirme com o usuário antes de mexer.
- Pergunte ao usuário quando o repositório não tiver código correspondente (só
  specs, ou o alvo não existir). Não invente estrutura nem crie arquivos por
  suposição.

Leia o código atual antes de mexer. A implementação deve respeitar as restrições
declaradas na spec e no `AGENTS.md` do repositório.

### 4. Implementar

Só o que a spec pede — nada além. Siga os padrões que já existem no arquivo e nos
vizinhos.

### 5. Verificar

Rode a verificação que o projeto oferece. Descubra o comando antes de rodar —
não invente. Procure o manifesto do projeto (`Makefile`, `package.json`,
`pyproject.toml`, `manage.py`…) e o que ele define como teste/build.

- Se houver suíte de testes, rode-a e reporte o resultado real.
- Se não houver suíte (ou ela não cobrir a mudança), verifique manualmente o
  caminho afetado e diga **o que** você verificou.
- Teste que falha = tarefa não concluída; conserte antes de reportar.

### 6. Reportar

Resuma, em poucas linhas: **spec mudou** (o quê) → **código mudou** (onde,
`arquivo:linha`) → **verificação** (o que passou/falhou). Aponte qualquer
ambiguidade da spec que você resolveu por conta própria, pra o usuário confirmar.

## Observações

- Nunca inverta a direção: se o código não bate com a spec, ajuste o **código**.
- Não invente requisito que não está no diff nem na spec.
- Se a mudança for em worker/backend e você não tiver certeza do alvo, pergunte
  antes de escrever.
- Spec nova ainda não commitada aparece no `git status`, não no `git diff` —
  lembre disso no passo 1.
