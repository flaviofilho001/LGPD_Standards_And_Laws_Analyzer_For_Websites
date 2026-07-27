"""Etapa 7 (opcional) — O mesmo grafo em um banco de grafos: Memgraph + Cypher.

O NetworkX é ótimo para entender o mecanismo, mas em produção o grafo mora
em um banco de grafos. Este script:
  1. Carrega as triplas refinadas no Memgraph (protocolo Bolt, driver neo4j)
  2. Executa as consultas da etapa 5 reescritas em Cypher
  3. Demonstra text-to-Cypher: o LLM traduz a pergunta em linguagem natural
     para uma consulta Cypher, que é executada no banco

Pré-requisito (Docker):
    docker run -it -p 7687:7687 -p 7444:7444 memgraph/memgraph-mage

Uso:
    python scripts/07_memgraph_cypher.py            # carga + consultas fixas
    python scripts/07_memgraph_cypher.py --llm      # inclui text-to-Cypher
"""

import json
import sys
from importlib import import_module

from neo4j import GraphDatabase

from util_comum import chamar_api, criar_cliente, MODELO_GERACAO

mod04 = import_module("04_construcao_grafo")

URI = "bolt://localhost:7687"

CONSULTAS_CYPHER = {
    "Empresas fundadas por ex-funcionários da Cactus Data": """
        MATCH (p:PESSOA)-[:TRABALHOU_EM]->(c:ORGANIZACAO {nome: 'Cactus Data'}),
              (p)-[:FUNDOU]->(e:ORGANIZACAO)
        WHERE e.nome <> 'Cactus Data'
        RETURN p.nome AS fundador, e.nome AS empresa
    """,
    "Organizações que conectam Agronegócio e Energia": """
        MATCH (a:ORGANIZACAO)-[:ATUA_EM]->(:SETOR {nome: 'Agronegócio'}),
              (b:ORGANIZACAO)-[:ATUA_EM]->(:SETOR {nome: 'Energia'}),
              (a)--(x)--(b)
        WHERE x <> a AND x <> b AND NOT x:SETOR
        RETURN DISTINCT x.nome AS conector, a.nome AS lado_agro, b.nome AS lado_energia
    """,
}

PROMPT_TEXT2CYPHER = """Traduza a pergunta para UMA consulta Cypher.

Esquema do grafo:
- Nós com labels: PESSOA, ORGANIZACAO, TECNOLOGIA, LOCAL, SETOR
  (todo nó tem a propriedade `nome`)
- Relações: FUNDOU, TRABALHOU_EM, DESENVOLVEU, USA_TECNOLOGIA, INVESTIU_EM,
  PARCEIRA_DE, LOCALIZADA_EM, COORDENA, FORMOU_SE_EM, GERE, ATUA_EM

Responda APENAS com a consulta Cypher, sem explicações nem markdown.

PERGUNTA: {pergunta}
"""


def carregar_no_memgraph(driver, triplas):
    with driver.session() as sessao:
        sessao.run("MATCH (n) DETACH DELETE n")  # zera a base da demo
        for t in triplas:
            tipo_destino = t.get("tipo_destino", "ENTIDADE")
            # Setores viram nós :SETOR para as consultas ficarem naturais
            if t["relacao"] == "ATUA_EM":
                tipo_destino = "SETOR"
            sessao.run(
                f"""
                MERGE (a:{t.get('tipo_origem', 'ENTIDADE')} {{nome: $origem}})
                MERGE (b:{tipo_destino} {{nome: $destino}})
                MERGE (a)-[r:{t['relacao']}]->(b)
                SET r.fonte = $fonte, r.evidencia = $evidencia
                """,
                origem=t["origem"], destino=t["destino"],
                fonte=t.get("fonte", "?"), evidencia=t.get("evidencia", ""),
            )
        total = sessao.run("MATCH (n) RETURN count(n) AS n").single()["n"]
        rels = sessao.run("MATCH ()-[r]->() RETURN count(r) AS n").single()["n"]
    print(f"Memgraph carregado: {total} nós, {rels} relações")


def executar(driver, cypher):
    with driver.session() as sessao:
        return [dict(reg) for reg in sessao.run(cypher)]


def main():
    triplas = mod04.carregar_triplas()
    try:
        driver = GraphDatabase.driver(URI, auth=("", ""))
        driver.verify_connectivity()
    except Exception as erro:
        raise SystemExit(
            f"Não foi possível conectar ao Memgraph em {URI} ({erro}).\n"
            "Suba o container: docker run -it -p 7687:7687 memgraph/memgraph-mage"
        )

    carregar_no_memgraph(driver, triplas)

    for titulo, cypher in CONSULTAS_CYPHER.items():
        print(f"\n[Cypher] {titulo}")
        print(cypher.strip())
        for linha in executar(driver, cypher):
            print(f"  -> {linha}")

    if "--llm" in sys.argv:
        cliente = criar_cliente()
        pergunta = "Quem são os fundadores das empresas investidas pelo Litoral Ventures?"
        print(f"\n[text-to-Cypher] PERGUNTA: {pergunta}")
        resposta = chamar_api(
            cliente.models.generate_content,
            model=MODELO_GERACAO,
            contents=PROMPT_TEXT2CYPHER.format(pergunta=pergunta),
        )
        cypher = resposta.text.strip().removeprefix("```cypher").removeprefix(
            "```").removesuffix("```").strip()
        print(f"Cypher gerado pelo LLM:\n{cypher}")
        try:
            for linha in executar(driver, cypher):
                print(f"  -> {linha}")
        except Exception as erro:
            print(f"  [aviso] consulta gerada falhou: {erro}")
            print("  Em produção, isso pede validação/retry — tema de guardrails.")

    driver.close()


if __name__ == "__main__":
    main()