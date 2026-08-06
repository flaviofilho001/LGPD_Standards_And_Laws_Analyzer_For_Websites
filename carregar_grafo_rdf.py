"""Módulo de Grafo de Conhecimento RDF/OWL & Consultas SPARQL (Trilha A - SBC).

Converte triplas.json em uma ontologia formal em sintaxe Turtle (.ttl),
carrega o grafo via rdflib, executa inferência RDFS/OWL-RL com owlrl,
e possibilita a execução de consultas SPARQL sobre o conhecimento normativo.
"""

import json
import os
import re
import sys
import rdflib
from rdflib import Graph, URIRef, Literal, Namespace, RDF, RDFS, OWL

# Reconfigura o encoding do terminal Windows para UTF-8 de forma segura
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

try:
    import owlrl
    HAS_OWLRL = True
except ImportError:
    HAS_OWLRL = False

PATH_TRIPLAS = os.path.join(os.path.dirname(__file__), "triplas.json")
PATH_TTL = os.path.join(os.path.dirname(__file__), "knowledge_graph.ttl")

# Namespaces RDF Formais
EX = Namespace("http://example.org/lgpd#")
DCTERMS = Namespace("http://purl.org/dc/terms/")


def exportar_triplas_para_turtle_rdf(caminho_json=PATH_TRIPLAS, caminho_ttl=PATH_TTL) -> Graph:
    """Lê o arquivo triplas.json e gera o arquivo Turtle (.ttl) com ontologia RDF/OWL."""
    if not os.path.exists(caminho_json):
        print(f"[ERRO] Arquivo {caminho_json} não encontrado.")
        return Graph()

    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)

    triplas = dados.get("triplas", [])

    g = Graph()
    g.bind("ex", EX)
    g.bind("rdfs", RDFS)
    g.bind("owl", OWL)
    g.bind("dcterms", DCTERMS)

    # Definição do Grafo Ontológico
    lgpd_ontology = URIRef("http://example.org/lgpd#ComplianceOntology")
    g.add((lgpd_ontology, RDF.type, OWL.Ontology))
    g.add((lgpd_ontology, RDFS.label, Literal("Ontologia de Compliance LGPD, ISOs e TPRM")))

    # Classes Principais
    cls_norma = URIRef(EX["NormaRegulatoria"])
    cls_requisito = URIRef(EX["RequisitoControle"])
    cls_evidencia = URIRef(EX["EvidenciaEmpirica"])

    g.add((cls_norma, RDF.type, OWL.Class))
    g.add((cls_requisito, RDF.type, OWL.Class))
    g.add((cls_evidencia, RDF.type, OWL.Class))

    for t in triplas:
        s_raw = t["origem"]
        p_raw = t["relacao"]
        o_raw = t["destino"]
        fonte = t.get("fonte", "LGPD/ISO")

        s_clean = re.sub(r'[^a-zA-Z0-9_]', '_', s_raw)
        p_clean = re.sub(r'[^a-zA-Z0-9_]', '_', p_raw)
        o_clean = re.sub(r'[^a-zA-Z0-9_]', '_', o_raw)

        subj = URIRef(EX[s_clean])
        pred = URIRef(EX[p_clean])
        obj = URIRef(EX[o_clean])

        # Tripla principal
        g.add((subj, pred, obj))
        
        # Metadados de Rastreabilidade
        g.add((subj, RDFS.label, Literal(s_raw)))
        g.add((obj, RDFS.label, Literal(o_raw)))
        g.add((subj, DCTERMS.source, Literal(fonte)))

    # Salva o arquivo Turtle (.ttl)
    g.serialize(destination=caminho_ttl, format="turtle")
    print(f" -> Ontologia RDF/OWL gerada com sucesso em Turtle: {caminho_ttl} ({len(g)} triplas RDF)")
    return g


def carregar_e_consultar_grafo_rdf(caminho_ttl=PATH_TTL, aplicar_inferencia=True) -> Graph:
    """Carrega a ontologia Turtle, aplica inferência OWL-RL e executa consultas SPARQL."""
    if not os.path.exists(caminho_ttl):
        print(f"Arquivo Turtle não encontrado. Exportando a partir do triplas.json...")
        exportar_triplas_para_turtle_rdf(caminho_ttl=caminho_ttl)

    g = Graph()
    g.parse(caminho_ttl, format="turtle")
    print(f" -> [RDF] Carregadas {len(g)} triplas do arquivo Turtle '{os.path.basename(caminho_ttl)}'.")

    if aplicar_inferencia and HAS_OWLRL:
        print(" -> [OWL-RL] Aplicando inferência lógica no grafo...")
        try:
            owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(g)
            print(f" -> [OWL-RL] Inferência concluída. Total de triplas expandidas: {len(g)}")
        except Exception as e:
            print(f" -> [Aviso] Falha ao executar inferência OWL-RL: {e}")

    return g


def executar_consultas_sparql_exemplo(g: Graph):
    """Executa consultas SPARQL demonstrativas sobre a ontologia."""
    print("\n" + "=" * 80)
    print(" EXECUÇÃO DE CONSULTAS SPARQL SOBRE O GRAFO DE CONHECIMENTO (TRILHA A)")
    print("=" * 80)

    # Consulta 1: Todos os Requisitos exigidos diretamente pela LGPD
    query_1 = """
    PREFIX ex: <http://example.org/lgpd#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?origem ?relacao ?destino WHERE {
        ?origem ?relacao ?destino .
        FILTER (STRSTARTS(STR(?origem), "http://example.org/lgpd#LGPD"))
    }
    LIMIT 10
    """
    print("\n--- Consulta SPARQL 1: Relacionamentos da LGPD ---")
    res1 = g.query(query_1)
    for row in res1:
        s = str(row.origem).split("#")[-1]
        p = str(row.relacao).split("#")[-1]
        o = str(row.destino).split("#")[-1]
        print(f" ({s}) -[{p}]-> ({o})")

    # Consulta 2: Mapeamento de Controles ISO aplicados à LGPD
    query_2 = """
    PREFIX ex: <http://example.org/lgpd#>
    
    SELECT ?origem ?destino WHERE {
        ?origem ex:APLICA_CONTROLE ?destino .
    }
    """
    print("\n--- Consulta SPARQL 2: Controles ISO aplicados à LGPD (ex:APLICA_CONTROLE) ---")
    res2 = g.query(query_2)
    for row in res2:
        s = str(row.origem).split("#")[-1]
        d = str(row.destino).split("#")[-1]
        print(f" Norma LGPD: {s} ===> Controle ISO: {d}")


if __name__ == "__main__":
    g_rdf = exportar_triplas_para_turtle_rdf()
    g_rdf = carregar_e_consultar_grafo_rdf(aplicar_inferencia=True)
    executar_consultas_sparql_exemplo(g_rdf)
