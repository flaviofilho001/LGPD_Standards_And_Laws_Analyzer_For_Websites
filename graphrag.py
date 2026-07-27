"""Etapa 6 — GraphRAG completo (busca local por subgrafo).

Fecha o ciclo: a pergunta em linguagem natural passa a ser respondida com
contexto vindo do GRAFO, não de chunks soltos.

Pipeline de consulta (busca local, no espírito de Edge et al., 2024):
  1. LLM identifica as entidades mencionadas na pergunta
  2. Casamento das entidades com nós do grafo (matching fuzzy)
  3. Expansão da vizinhança em k saltos -> subgrafo relevante
  4. Serialização do subgrafo como texto (triplas legíveis + evidências)
  5. LLM responde usando o subgrafo como contexto

Compare a resposta com a do script 01 para as mesmas perguntas.

Uso:
    python scripts/06_graphrag.py ["pergunta livre"]
"""

import difflib
import json
import sys
from importlib import import_module

import networkx as nx

from util_comum import chamar_api, criar_cliente, MODELO_GERACAO

mod04 = import_module("04_construcao_grafo")

PERGUNTAS_PADRAO = [
    "Quais empresas foram fundadas por ex-funcionários da Cactus Data?",
    "Qual organização conecta o setor agrícola ao setor de energia no ecossistema?",
    "Que papel o Instituto Tambaú desempenha no ecossistema?",
]

K_SALTOS = 2  # raio de expansão da vizinhança


def extrair_entidades_da_pergunta(cliente, pergunta):
    prompt = (
        "Liste as entidades nomeadas (pessoas, organizações, tecnologias, "
        "locais, setores) mencionadas na pergunta abaixo. Responda APENAS "
        'com JSON: {"entidades": ["...", "..."]}\n\n'
        f"PERGUNTA: {pergunta}"
    )
    resposta = chamar_api(
        cliente.models.generate_content, model=MODELO_GERACAO, contents=prompt
    )
    limpo = (resposta.text.strip().removeprefix("```json")
             .removeprefix("```").removesuffix("```"))
    return json.loads(limpo)["entidades"]


def casar_com_nos(entidades, g):
    """Matching fuzzy entre entidades da pergunta e nós do grafo."""
    nos = list(g.nodes)
    ancoras = []
    for e in entidades:
        candidatos = difflib.get_close_matches(e, nos, n=1, cutoff=0.6)
        if candidatos:
            ancoras.append(candidatos[0])
    return ancoras


def expandir_subgrafo(g, ancoras, k=K_SALTOS):
    """União das vizinhanças de raio k em torno de cada nó-âncora."""
    g_nd = g.to_undirected()
    nos = set()
    for a in ancoras:
        nos |= set(nx.ego_graph(g_nd, a, radius=k).nodes)
    return g.subgraph(nos)


def serializar_subgrafo(sub):
    """Transforma o subgrafo em texto que o LLM consegue ler."""
    linhas = []
    for u, v, dados in sub.edges(data=True):
        linha = f"({u}) -[{dados['relacao']}]-> ({v})"
        if dados.get("evidencia"):
            linha += f'   [evidência: "{dados["evidencia"]}" — {dados.get("fonte", "?")}]'
        linhas.append(linha)
    return "\n".join(sorted(linhas))


def responder(cliente, pergunta, contexto_grafo):

    #print(f"Contexto do subgrafo:\n{contexto_grafo}")
    prompt = (
        "Você é um assistente que responde com base em um grafo de "
        "conhecimento. O contexto abaixo lista relações no formato "
        "(origem) -[RELACAO]-> (destino), com evidências textuais.\n"
        "Responda à pergunta usando APENAS essas relações. Cite, ao final, "
        "quais relações sustentam a resposta (a cadeia de raciocínio).\n\n"
        f"CONTEXTO (subgrafo):\n{contexto_grafo}\n\nPERGUNTA: {pergunta}"
    )
    return chamar_api(
        cliente.models.generate_content, model=MODELO_GERACAO, contents=prompt
    ).text


def main():
    cliente = criar_cliente()
    g = mod04.construir_grafo(mod04.carregar_triplas())

    perguntas = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else PERGUNTAS_PADRAO

    for i, pergunta in enumerate(perguntas):
        if i > 0:
            try:
                input("\n[Enter] para a próxima pergunta... ")
            except EOFError:
                pass
        print("\n" + "=" * 72)
        print(f"PERGUNTA: {pergunta}")

        entidades = extrair_entidades_da_pergunta(cliente, pergunta)
        ancoras = casar_com_nos(entidades, g)
        print(f"Entidades identificadas: {entidades} -> nós-âncora: {ancoras}")

        if not ancoras:
            print("Nenhuma âncora no grafo; caberia fallback para RAG vetorial.")
            continue

        sub = expandir_subgrafo(g, ancoras)
        print(f"Subgrafo recuperado: {sub.number_of_nodes()} nós, "
              f"{sub.number_of_edges()} arestas")

        contexto = serializar_subgrafo(sub)
        print(f"\nRESPOSTA (GraphRAG):\n{responder(cliente, pergunta, contexto)}")


if __name__ == "__main__":
    main()