#!/usr/bin/env python3
"""Prova que uma reorganização de specs não tocou em nenhum bullet.

Compara o estado atual de `specs/` com uma baseline (por padrão, `HEAD`) e falha
se um único bullet foi criado, removido ou teve o texto alterado. Bullets PODEM
mudar de seção/subseção — isso sai como "movido", não como erro.

Um bullet só pode ser movido junto com tudo que está aninhado abaixo dele: o
bloco (bullet + subárvore) é a unidade atômica. Desaninhar um filho do pai conta
como alteração do bloco do pai, e portanto falha.

Uso:
    python verificar.py                        # baseline = HEAD
    python verificar.py --base HEAD~1
    python verificar.py specs/componentes/Pagina.pt
    python verificar.py --so-conteudo          # pula a checagem de taxonomia
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
EXTENSAO = '.pt'

RE_HEAD = re.compile(r'^(#{1,6})\s+(?P<texto>.*?)\s*$')
RE_BULLET = re.compile(r'^(?P<indent>[ \t]*)-[ \t]+(?P<texto>.*)$')
RE_FENCE = re.compile(r'^[ \t]*(```|~~~)')

# Vocabulário canônico de seções `##`, na ordem em que devem aparecer.
# Seções são opcionais (a spec só tem as que precisa), mas as que existirem
# precisam estar nesta lista e nesta ordem.
CANONICAS = [
    'Objetivo', 'Fora do escopo', 'Comportamento', 'Regras',
    'Interface', 'Status', 'Dados / API', 'Implementação',
]
# Seções próprias (`## Equipe`, `## API Keys`, `## Login`…) são permitidas, mas
# só neste intervalo: depois de todas as canônicas de conteúdo e antes de
# `Dados / API`. É a regra do README ("seções próprias").
CABECALHO = CANONICAS[:6]
CAUDA = CANONICAS[6:]


# ---------------------------------------------------------------- parsing

def itens(texto: str) -> list[tuple[str, int, str]]:
    """Achata o arquivo em ('head', nivel, texto) | ('bullet', indent, texto).

    Bullet = a linha do `- ` mais as linhas de continuação (as que não são
    brancas, não são bullet e não são heading), dobradas numa linha só.

    Linhas dentro de cercas de código (``` ou ~~~) não são interpretadas como
    heading nem como bullet — isso evita que um JSON/YAML em `Dados / API`
    vire estrutura falsa.
    """
    saida: list[tuple[str, int, str]] = []
    em_cerca = False
    no_atual: int | None = None

    for linha in texto.split('\n'):
        if RE_FENCE.match(linha):
            em_cerca = not em_cerca
            continue
        if em_cerca:
            continue
        if not linha.strip():
            no_atual = None
            continue
        m = RE_HEAD.match(linha)
        if m:
            no_atual = None
            saida.append(('head', len(m.group(1)), m.group('texto')))
            continue
        m = RE_BULLET.match(linha)
        if m:
            indent = len(m.group('indent').expandtabs(4))
            saida.append(('bullet', indent, m.group('texto').strip()))
            no_atual = len(saida) - 1
            continue
        if no_atual is not None:
            tipo, indent, texto_atual = saida[no_atual]
            saida[no_atual] = (tipo, indent, f'{texto_atual} {linha.strip()}')
        # fora de bullet: prosa/tabela — não participa da prova
    return saida


def serializa(no: dict, nivel: int = 0) -> str:
    """Bloco canônico: indentação absoluta normalizada, estrutura relativa intacta."""
    linhas = ['  ' * nivel + '- ' + no['texto']]
    for filho in no['filhos']:
        linhas.extend(serializa(filho, nivel + 1))
    return '\n'.join(linhas)


def blocos(texto: str) -> list[tuple[str, tuple[str, ...]]]:
    """[(bloco canônico, caminho de seções)] para cada bullet de topo."""
    caminho: list[str] = []
    pilha: list[tuple[int, dict]] = []
    tops: list[tuple[dict, tuple[str, ...]]] = []
    for tipo, valor, txt in itens(texto):
        if tipo == 'head':
            nivel = valor
            if nivel == 1:
                caminho = []          # o H1 é o título do arquivo, não uma seção
            else:
                caminho = caminho[:nivel - 2]
                while len(caminho) < nivel - 2:
                    caminho.append('')
                caminho.append(txt)
            pilha = []
            continue
        no = {'texto': txt, 'filhos': []}
        while pilha and valor <= pilha[-1][0]:
            pilha.pop()
        if pilha:
            pilha[-1][1]['filhos'].append(no)
        else:
            tops.append((no, tuple(caminho)))
        pilha.append((valor, no))
    return [(serializa(no), cam) for no, cam in tops]


def conta_bullets(texto: str) -> int:
    return sum(1 for tipo, _, _ in itens(texto) if tipo == 'bullet')


def checa_taxonomia(texto: str) -> list[str]:
    """Ordem das seções `##`, duplicatas e posição das seções próprias."""
    secoes = [txt for tipo, nivel, txt in itens(texto)
              if tipo == 'head' and nivel == 2]
    problemas: list[str] = []
    vistas = Counter()
    ultimo = -1
    propria_vista = False
    cauda_vista = False

    for nome in secoes:
        vistas[nome] += 1
        if nome in CANONICAS:
            if vistas[nome] > 1:
                problemas.append(f'seção duplicada: ## {nome}')
            if propria_vista and nome in CABECALHO:
                problemas.append(
                    f'seção canônica depois de seção própria: ## {nome}'
                )
            pos = CANONICAS.index(nome)
            if pos < ultimo:
                problemas.append(
                    f'seção fora de ordem: ## {nome} '
                    f'(deveria vir depois de ## {CANONICAS[ultimo]})'
                )
            else:
                ultimo = pos
            if nome in CAUDA:
                cauda_vista = True
        else:
            if cauda_vista:
                problemas.append(
                    f'seção própria depois de ## {CAUDA[0]}: ## {nome}'
                )
            propria_vista = True
    return problemas


def checa_titulo(texto: str, caminho: str) -> tuple[list[str], list[str]]:
    """Exige um único H1 (o título) e avisa se ele não bate com o nome do arquivo."""
    heads = [(nivel, txt) for tipo, nivel, txt in itens(texto) if tipo == 'head']
    h1 = [txt for nivel, txt in heads if nivel == 1]
    problemas = []
    if not h1:
        problemas.append('sem título: falta o H1 (# <Nome>)')
    elif len(h1) > 1:
        problemas.append(f'H1 sobrando (o arquivo deve ter um só): {", ".join(h1)}')
    elif len(heads) > 1 and heads[0][0] != 1:
        problemas.append(f'o H1 (# {h1[0]}) não é o primeiro heading do arquivo')

    avisos = []
    if h1:
        stem = Path(caminho).stem
        if sem_acento(h1[0]) != sem_acento(stem):
            avisos.append(
                f'título "# {h1[0]}" difere do nome do arquivo ({stem}{EXTENSAO})'
            )
    return problemas, avisos


# ---------------------------------------------------------------- comparacao

def tem_head() -> bool:
    r = subprocess.run(
        ['git', 'rev-parse', '--verify', '--quiet', 'HEAD'],
        capture_output=True, text=True, cwd=RAIZ,
    )
    return r.returncode == 0


def baseline(caminho: str, ref: str) -> str | None:
    r = subprocess.run(
        ['git', 'show', f'{ref}:{caminho}'],
        capture_output=True, text=True, cwd=RAIZ,
    )
    return r.stdout if r.returncode == 0 else None


def compara(antes_txt: str, depois_txt: str) -> dict:
    antes, depois = blocos(antes_txt), blocos(depois_txt)
    ca, cd = Counter(t for t, _ in antes), Counter(t for t, _ in depois)
    comum = ca & cd
    removidos = sum((ca - cd).values())
    criados = sum((cd - ca).values())

    movidos = 0
    for texto in ca.keys() & cd.keys():
        pa = Counter(c for t, c in antes if t == texto)
        pd = Counter(c for t, c in depois if t == texto)
        movidos += sum(pa.values()) - sum((pa & pd).values())

    return {
        'bullets_antes': conta_bullets(antes_txt),
        'bullets_depois': conta_bullets(depois_txt),
        'preservados': sum(comum.values()),
        'movidos': movidos,
        'alterados': removidos,
        'criados': criados,
        'sumiram': list((ca - cd).elements()),
        'surgiram': list((cd - ca).elements()),
    }


def sem_acento(texto: str) -> str:
    """'Página' -> 'pagina', para comparar título com nome de arquivo."""
    base = unicodedata.normalize('NFD', texto)
    return ''.join(c for c in base if not unicodedata.combining(c)).lower()


def plural(n: int, singular: str, plura: str) -> str:
    return f'{n} {singular if n == 1 else plura}'


def resumo_bloco(bloco: str, limite: int = 72) -> str:
    primeira = bloco.split('\n')[0]
    extra = ' (+ aninhados)' if '\n' in bloco else ''
    if len(primeira) > limite:
        primeira = primeira[:limite - 1] + '…'
    return primeira + extra


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description='Prova que nenhum bullet de spec foi alterado.')
    ap.add_argument('arquivos', nargs='*', help='specs específicas (padrão: todas)')
    ap.add_argument('--base', default='HEAD', help='ref git da baseline (padrão: HEAD)')
    ap.add_argument('--so-conteudo', action='store_true', help='pula a checagem de taxonomia')
    args = ap.parse_args()

    if args.base == 'HEAD' and not tem_head():
        print('ERRO: o repositório não tem nenhum commit em HEAD.')
        print('      Sem baseline não há prova possível. Faça o primeiro commit')
        print('      (ou passe --base <ref>) antes de reorganizar as specs.')
        return 2

    if args.arquivos:
        alvos = [Path(a) for a in args.arquivos]
    else:
        alvos = sorted(RAIZ.glob(f'specs/**/*{EXTENSAO}'))

    if not alvos:
        print(f'ERRO: nenhum arquivo *{EXTENSAO} encontrado em specs/.')
        print('      Nada foi verificado — não trate isto como aprovação.')
        return 2

    falhas: list[str] = []
    avisos: list[str] = []
    total = {'arquivos': 0, 'bullets': 0, 'preservados': 0, 'movidos': 0,
             'alterados': 0, 'criados': 0, 'estrutura': 0}
    sem_baseline = 0

    for alvo in alvos:
        try:
            rel = alvo.resolve().relative_to(RAIZ).as_posix()
        except ValueError:
            falhas.append(f'{alvo}: fora do diretório do projeto')
            continue
        if not alvo.exists():
            falhas.append(f'{rel}: não existe no disco')
            continue
        antes = baseline(rel, args.base)
        if antes is None:
            sem_baseline += 1
            falhas.append(f'{rel}:')
            falhas.append(
                f'       - não existe em {args.base} '
                f'(commite antes de reorganizar)'
            )
            print(f'FALHA {rel}  (fora da baseline)')
            continue

        depois = alvo.read_text(encoding='utf-8')
        r = compara(antes, depois)
        total['arquivos'] += 1
        for k in ('preservados', 'movidos', 'alterados', 'criados'):
            total[k] += r[k]
        total['bullets'] += r['bullets_depois']

        problemas = []
        if r['alterados'] or r['criados']:
            for b in r['sumiram']:
                problemas.append(f'DESAPARECEU (na baseline): {resumo_bloco(b)}')
            for b in r['surgiram']:
                problemas.append(f'APARECEU (não estava na baseline): {resumo_bloco(b)}')
        if not args.so_conteudo:
            estrutura = checa_taxonomia(depois)
            titulo_prob, titulo_avisos = checa_titulo(depois, rel)
            estrutura.extend(titulo_prob)
            problemas.extend(estrutura)
            total['estrutura'] += len(estrutura)
            avisos.extend(f'{rel}: {a}' for a in titulo_avisos)

        if problemas:
            falhas.append(f'{rel}:')
            falhas.extend(f'       - {p}' for p in problemas)
            marca = 'FALHA'
        else:
            marca = 'OK   '
        print(f'{marca} {rel}  '
              f"({r['preservados']} blocos, {r['movidos']} movidos)")

    print()
    if avisos:
        print('AVISOS (não bloqueiam)')
        for linha in avisos:
            print(f'  {linha}')
        print()
    if falhas:
        print('VIOLADO')
        for linha in falhas:
            print(f'  {linha}')
        print()
        print(f"  {plural(total['alterados'], 'bloco alterado/removido', 'blocos alterados/removidos')}"
              f"   {plural(total['criados'], 'bloco criado', 'blocos criados')}"
              f"   {plural(total['estrutura'], 'problema de estrutura', 'problemas de estrutura')}")
        if total['alterados'] or total['criados']:
            print('  Reverta: um bullet nunca muda de texto, só de lugar.')
        if sem_baseline:
            print('  Commite o estado atual antes de reorganizar (sem baseline não há prova).')
        return 1

    print(f"OK   {plural(total['arquivos'], 'arquivo', 'arquivos')}")
    print(f"     {plural(total['bullets'], 'bullet congelado', 'bullets congelados')}")
    print(f"     {plural(total['preservados'], 'bloco preservado', 'blocos preservados')}")
    print(f"     {plural(total['movidos'], 'bloco movido de seção', 'blocos movidos de seção')}")
    print('     0 alterados   0 removidos   0 criados')
    return 0


if __name__ == '__main__':
    sys.exit(main())
