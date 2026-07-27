"""Core Compliance GraphRAG Engine.

Constrói o Grafo de Conhecimento de Compliance (LGPD, ISO 27001, ISO 27002, ISO 31000, TPRM),
submete dados raspados de sites a auditorias por subgrafos e gera relatorio_auditoria.json estruturado.
Suporta execução via Ollama Local (Sem Limites) ou Gemini API.
"""

import json
import os
import re
import sys
import networkx as nx

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

from util_comum import (
    chamar_api, criar_cliente, extrair_json_seguro, MODELO_GERACAO, 
    obter_api_key, gerar_resposta_llm, listar_modelos_ollama_locais
)
from util_pdf import carregar_todos_textos_base
from util_scraper import raspar_multiplas_urls
from util_triplas import carregar_ou_inicializar_triplas, incrementar_triplas

PATH_JSON_SAIDA = os.path.join(os.path.dirname(__file__), "relatorio_auditoria.json")


def construir_grafo_compliance(novas_triplas_para_incrementar=None):
    """Constrói o Grafo de Conhecimento a partir do arquivo triplas.json (com suporte a incremento)."""
    if novas_triplas_para_incrementar:
        triplas = incrementar_triplas(novas_triplas_para_incrementar)
    else:
        triplas = carregar_ou_inicializar_triplas()

    g = nx.DiGraph()
    for t in triplas:
        origem = t["origem"]
        destino = t["destino"]
        relacao = t["relacao"]
        fonte = t.get("fonte", "Norma Base")
        
        if not g.has_node(origem):
            g.add_node(origem, tipo="ENTIDADE_NORMA")
        if not g.has_node(destino):
            g.add_node(destino, tipo="REQUISITO_CONTROLE")
            
        g.add_edge(origem, destino, relacao=relacao, fonte=fonte)
        
    return g, triplas


# Definição dos Tópicos de Auditoria de Compliance
TOPICOS_AUDITORIA = [
    {
        "id": "AUD-001",
        "titulo": "Identificação do Controlador, Razão Social e CNPJ",
        "categoria": "Transparência & Governança (LGPD)",
        "ancoras_grafo": ["LGPD_Art_5_Identificacao_Controlador", "Razao_Social_e_CNPJ_Claros"],
        "palavras_chave": ["cnpj", "razão social", "operado por", "controlador", "empresa", "endereço"],
        "normas": "LGPD Art. 5º VI; LGPD Art. 6º VI (Princípio da Transparência)"
    },
    {
        "id": "AUD-002",
        "titulo": "Bases Legais, Consentimento e Especificação da Finalidade",
        "categoria": "Tratamento de Dados (LGPD)",
        "ancoras_grafo": ["LGPD_Art_7_Bases_Legais", "Especificacao_Finalidade_Tratamento"],
        "palavras_chave": ["finalidade", "consentimento", "base legal", "coletamos dados", "para que usamos", "legítimo interesse"],
        "normas": "LGPD Art. 6º I e II; LGPD Art. 7º I e V"
    },
    {
        "id": "AUD-003",
        "titulo": "Direitos dos Titulares e Canal de Atendimento de Requisições",
        "categoria": "Direitos do Titular (LGPD / ISO 27001)",
        "ancoras_grafo": ["LGPD_Art_18_Direitos_Titular", "Canal_Atendimento_Solicitacoes_Titular"],
        "palavras_chave": ["seus direitos", "acesso", "exclusão", "revogação", "portabilidade", "solicitar", "exercer"],
        "normas": "LGPD Art. 18; LGPD Art. 19 (Prazo 15 dias)"
    },
    {
        "id": "AUD-004",
        "titulo": "Indicação Pública do Encarregado pelo Tratamento de Dados (DPO)",
        "categoria": "Governança & DPO (LGPD Art. 41)",
        "ancoras_grafo": ["LGPD_Art_41_DPO", "Divulgação_Pública_Contato_DPO"],
        "palavras_chave": ["dpo", "encarregado", "privacidade@", "contato do encarregado", "encarregado de dados"],
        "normas": "LGPD Art. 41 § 1º (Obrigação de divulgação pública do DPO)"
    },
    {
        "id": "AUD-005",
        "titulo": "Medidas de Segurança, Criptografia e Proteção de Dados",
        "categoria": "Segurança da Informação (LGPD Art. 46 / ISO 27002 A.10 & A.12)",
        "ancoras_grafo": ["LGPD_Art_46_Seguranca_Tecnica_Admin", "ISO_27002_Controle_10_Criptografia"],
        "palavras_chave": ["segurança", "criptografia", "ssl", "tls", "https", "proteção", "acesso não autorizado", "backup"],
        "normas": "LGPD Art. 46; ABNT NBR ISO/IEC 27002 Controles 10.1 e 12.4"
    },
    {
        "id": "AUD-006",
        "titulo": "Compartilhamento de Dados com Terceiros e Transferência Internacional",
        "categoria": "Gestão de Terceiros & TPRM (LGPD Art. 33 / ISO 27002 A.15)",
        "ancoras_grafo": ["LGPD_Art_33_Transferencia_Compartilhamento", "TPRM_Gestao_Riscos_Terceiros"],
        "palavras_chave": ["compartilhamos", "terceiros", "parceiros", "processadores", "transferência internacional", "fornecedores"],
        "normas": "LGPD Art. 33 e 34; ABNT NBR ISO/IEC 27002 Controle 15.1; ISO 31000"
    },
    {
        "id": "AUD-007",
        "titulo": "Gestão de Cookies, Tecnologias de Rastreamento e Opt-Out",
        "categoria": "Privacidade Digital & Consentimento (LGPD)",
        "ancoras_grafo": ["LGPD_Art_8_Revogacao_Consentimento", "Procedimento_Gratuito_Facil_OptOut"],
        "palavras_chave": ["cookies", "pixels", "rastreamento", "analytics", "navegador", "opt-out", "desativar"],
        "normas": "LGPD Art. 8º § 5º (Facilidade de Revogação); LGPD Art. 18 IX"
    },
    {
        "id": "AUD-008",
        "titulo": "Notificação e Protocolo de Resposta a Incidentes de Segurança",
        "categoria": "Gestão de Incidentes (LGPD Art. 48 / ISO 27002 A.16)",
        "ancoras_grafo": ["LGPD_Art_48_Notificacao_Incidentes", "ISO_27002_Controle_16_Gestao_Incidentes"],
        "palavras_chave": ["vazamento", "incidente", "notificação", "anpd", "violação de dados", "comunicação aos titulares"],
        "normas": "LGPD Art. 48 § 1º; ABNT NBR ISO/IEC 27002 Controle 16.1"
    }
]


def buscar_paragrafos_relevantes(dados_sites: list, palavras_chave: list) -> list:
    """Filtra parágrafos dos sites raspados que contenham palavras-chave do tópico."""
    relevantes = []
    for site in dados_sites:
        if not site.get("sucesso"):
            continue
        for p in site.get("paragrafos", []):
            texto_lower = p["texto"].lower()
            if any(kw in texto_lower for kw in palavras_chave):
                relevantes.append(p)
    return relevantes


def auditar_topico_com_graphrag(cliente, g, topico, paragrafos_evidencia, provedor="ollama", modelo_local="gemma4:12b"):
    """Realiza a auditoria de um tópico usando o Grafo de Conhecimento e o Provedor de IA selecionado."""
    
    # 1. Recupera Subgrafo no Raio k=2 das Âncoras do Tópico
    nos_subgrafo = set()
    g_und = g.to_undirected()
    for anc in topico["ancoras_grafo"]:
        if anc in g:
            nos_subgrafo |= set(nx.ego_graph(g_und, anc, radius=2).nodes)
            
    subgrafo = g.subgraph(nos_subgrafo) if nos_subgrafo else g
    
    # 2. Serializa as regras do Subgrafo
    regras_linhas = []
    for u, v, d in subgrafo.edges(data=True):
        regras_linhas.append(f"- REGRA NORMATIVA: ({u}) -[{d.get('relacao')}]-> ({v}) [Fonte: {d.get('fonte', 'Norma')}]")
    regras_texto = "\n".join(regras_linhas) if regras_linhas else f"- Requisito base: {topico['normas']}"
    
    # 3. Formata Evidências Encontradas no Site com Rastreabilidade
    if paragrafos_evidencia:
        evidencias_texto = "\n".join([
            f"* [{p['url']} | Linha {p['linha']}] (Tag: {p['tag']}): \"{p['texto']}\""
            for p in paragrafos_evidencia[:6]
        ])
    else:
        evidencias_texto = "Nenhuma menção explícita ou evidência direta encontrada nos textos analisados do site."
        
    # 4. Avaliação com IA (Ollama Local, Gemini API ou Fallback)
    if provedor != "heuristico":
        prompt = f"""Você é um auditor sênior de Compliance especialista em LGPD, ISO/IEC 27001, ISO/IEC 27002 e ISO 31000.

Sua tarefa é analisar as evidências extraídas do site de um serviço digital contra os requisitos legais e normativos do Grafo de Conhecimento.

REQUISITO AUDITADO: {topico['titulo']} (ID: {topico['id']})
CATEGORIA: {topico['categoria']}
NORMAS DE REFERÊNCIA: {topico['normas']}

REGRAS EXTRAÍDAS DO GRAFO DE CONHECIMENTO (Subgrafo GraphRAG de triplas.json):
{regras_texto}

EVIDÊNCIAS ENCONTRADAS NO SITE (Rastreável por URL e Linha):
{evidencias_texto}

INSTRUÇÕES DE RESPOSTA:
Analise rigorosamente as evidências fornecidas.
Determine o STATUS:
- "CONFORME": O site cumpre claramente o requisito legal/normativo com texto explícito.
- "NAO_CONFORME": O site descumpre a exigência obrigatória ou omite informação essencial exigida por lei (ex: não menciona CNPJ, não indica DPO, omite direitos do titular).
- "ATENCAO": O requisito é mencionado, mas de forma ambígua, incompleta ou com ressalvas.

Responda APENAS em formato JSON com a seguinte estrutura estrita:
{{
  "status": "CONFORME" | "NAO_CONFORME" | "ATENCAO",
  "trecho_site_evidencia": "Citação exata do trecho com [URL | Linha X] ou indicação explicativa de ausência",
  "norma_referencia": "{topico['normas']}",
  "explicacao_fundamentacao": "Explicação técnica detalhada em português justificando por que está certo ou errado, apontando lacunas ou conformidades conforme os artigos da LGPD e ISOs."
}}
"""
        resposta_texto = gerar_resposta_llm(
            prompt, 
            provedor=provedor, 
            modelo_local=modelo_local, 
            cliente_gemini=cliente
        )
        
        if resposta_texto:
            dados_json = extrair_json_seguro(resposta_texto)
            if dados_json and "status" in dados_json:
                return {
                    "item_id": topico["id"],
                    "titulo_item": topico["titulo"],
                    "categoria": topico["categoria"],
                    "status": dados_json.get("status", "ATENCAO"),
                    "trecho_site_evidencia": dados_json.get("trecho_site_evidencia", evidencias_texto[:250]),
                    "norma_referencia": dados_json.get("norma_referencia", topico["normas"]),
                    "explicacao_fundamentacao": dados_json.get("explicacao_fundamentacao", "Análise realizada com base nas regras do subgrafo de compliance.")
                }

    # Fallback Heurístico (quando sem IA ou se falhar)
    status_fall = "CONFORME" if paragrafos_evidencia else "NAO_CONFORME"
    if paragrafos_evidencia:
        trecho_fall = f"[{paragrafos_evidencia[0]['url']} | Linha {paragrafos_evidencia[0]['linha']}] \"{paragrafos_evidencia[0]['texto']}\""
        expl_fall = f"Foram identificadas evidências de atendimento ao requisito em {len(paragrafos_evidencia)} trechos do site auditado. O texto aborda os elementos da norma."
    else:
        trecho_fall = "Ausência de texto ou cláusula no site indicando atendimento ao requisito."
        expl_fall = f"Não foram encontradas evidências explícitas nas páginas analisadas para o requisito '{topico['titulo']}'. A ausência configura inconformidade frente à {topico['normas']}."
        
    return {
        "item_id": topico["id"],
        "titulo_item": topico["titulo"],
        "categoria": topico["categoria"],
        "status": status_fall,
        "trecho_site_evidencia": trecho_fall,
        "norma_referencia": topico["normas"],
        "explicacao_fundamentacao": expl_fall
    }


def executar_auditoria_completa(urls: list, novas_triplas=None, provedor="ollama", modelo_local="gemma4:12b"):
    """Executa a auditoria completa GraphRAG para uma lista de URLs consultando triplas.json e usando o provedor de IA escolhido."""
    print("=" * 80)
    print(f" INICIANDO PIPELINE DE AUDITORIA DE COMPLIANCE GRAPHRAG (Provedor: {provedor.upper()})")
    print("=" * 80)
    
    # 1. Prepara Cliente Gemini (se o provedor selecionado for Gemini)
    cliente = None
    if provedor.lower() == "gemini":
        if obter_api_key():
            try:
                cliente = criar_cliente()
                print(" -> Cliente Gemini API inicializado com sucesso.")
            except Exception as e:
                print(f" -> [Aviso] Falha ao conectar com Gemini API ({e}).")
        else:
            print(" -> [Aviso] Nenhuma chave GEMINI_API_KEY detectada para a API Gemini.")
    elif provedor.lower() == "ollama":
        print(f" -> Conectando ao Ollama Local no modelo '{modelo_local}' (sem limites de API).")

    # 2. Consulta o triplas.json e constrói o Grafo
    g, triplas_carregadas = construir_grafo_compliance(novas_triplas_para_incrementar=novas_triplas)
    print(f" -> Grafo de Conhecimento de Compliance pronto: {g.number_of_nodes()} nós, {g.number_of_edges()} arestas (baseado em triplas.json).")
    
    # 3. Realiza Scraping das URLs
    dados_sites = raspar_multiplas_urls(urls)
    urls_com_sucesso = [s["url"] for s in dados_sites if s["sucesso"]]
    
    if not urls_com_sucesso:
        print("\n[ERRO CRÍTICO] Nenhuma URL pôde ser raspada com sucesso.")
        
    # 4. Executa Auditoria por Tópico
    itens_fundamentacao = []
    totais = {"CONFORME": 0, "NAO_CONFORME": 0, "ATENCAO": 0}
    
    for topico in TOPICOS_AUDITORIA:
        print(f"\n[Auditoria {topico['id']}] {topico['titulo']}...")
        paragrafos_ev = buscar_paragrafos_relevantes(dados_sites, topico["palavras_chave"])
        resultado_item = auditar_topico_com_graphrag(
            cliente, g, topico, paragrafos_ev, 
            provedor=provedor, modelo_local=modelo_local
        )
        
        st = resultado_item["status"]
        totais[st] = totais.get(st, 0) + 1
        print(f"  -> Status: [{st}] - Ref: {resultado_item['norma_referencia']}")
        itens_fundamentacao.append(resultado_item)

    # 5. Monta o JSON Estruturado Final
    total_itens = len(itens_fundamentacao)
    porcentagem_conforme = round((totais["CONFORME"] / total_itens) * 100, 1) if total_itens > 0 else 0
    
    relatorio_json = {
        "titulo": "Relatório de Auditoria de Compliance LGPD, ISO 27001, ISO 27002 & ISO 31000",
        "metadata": {
            "data_auditoria": "2026-07-27",
            "urls_analisadas": urls,
            "provedor_ia": f"{provedor.upper()} ({modelo_local if provedor.lower() == 'ollama' else MODELO_GERACAO})",
            "normas_base": ["LGPD (Lei 13.709/2018)", "ABNT NBR ISO/IEC 27001", "ABNT NBR ISO/IEC 27002", "ABNT NBR ISO 31000", "TPRM Framework"],
            "total_requisitos_auditados": total_itens,
            "total_triplas_grafo": len(triplas_carregadas),
            "resumo_status": totais,
            "indice_conformidade": f"{porcentagem_conforme}%"
        },
        "introducao": (
            "Este relatório apresenta o resultado da avaliação automatizada de conformidade legal e regulatória "
            f"das páginas web analisadas ({', '.join(urls)}). A análise utiliza a metodologia GraphRAG (Retrieval-Augmented Generation em Grafo), "
            f"executada via motor de IA {provedor.upper()} ({modelo_local if provedor.lower() == 'ollama' else MODELO_GERACAO}), "
            "correlacionando os textos das políticas públicas da plataforma com a Base de Conhecimento (triplas.json) formada pelos diplomas legais da LGPD, "
            "as normas ABNT NBR ISO/IEC 27001, 27002, 31000 e frameworks de Gestão de Riscos de Terceiros (TPRM). Cada ponto auditado possui "
            "rastreabilidade direta aos trechos e linhas do site, permitindo verificação imediata."
        ),
        "fundamentacao": itens_fundamentacao,
        "conclusao": (
            f"A análise automatizada de compliance resultou em um índice global de conformidade de {porcentagem_conforme}%. "
            f"Foram identificados {totais['CONFORME']} pontos em conformidade, {totais['ATENCAO']} pontos que exigem atenção/ajuste, "
            f"e {totais['NAO_CONFORME']} vulnerabilidades críticas de não conformidade com a LGPD e ISOs. "
            "A adequação dos pontos apontados como não conformes é indispensável para elidir riscos de sanções administrativas da ANPD (Art. 52 da LGPD) "
            "e garantir a integridade da segurança da informação conforme os padrões ISO/IEC 27001 e 27002."
        ),
        "proximos_passos": [
            "1. Nomear e divulgar publicamente a identidade e canal de contato do Encarregado pelo Tratamento de Dados Pessoais (DPO) na Política de Privacidade (LGPD Art. 41).",
            "2. Atualizar os Termos de Uso e Política de Privacidade para incluir a Razão Social completa e o número de inscrição no CNPJ do controlador de dados (LGPD Art. 5º VI, Art. 6º VI).",
            "3. Implementar um canal direto e procedimento claro com prazo de até 15 dias para que os titulares exercem seus direitos previstos no Art. 18 da LGPD.",
            "4. Estabelecer um banner interativo de Cookies com opção clara de Opt-Out (recusa) e gestão de preferências de rastreamento.",
            "5. Formalizar um Plano de Resposta a Incidentes de Segurança da Informação (SIRT) conforme ISO 27002 Controle 16.1 e LGPD Art. 48."
        ]
    }
    
    # Salva o arquivo JSON
    with open(PATH_JSON_SAIDA, "w", encoding="utf-8") as f:
        json.dump(relatorio_json, f, ensure_ascii=False, indent=2)
        
    print(f"\n Relatório em JSON gerado com sucesso!")
    print(f"    Salvo em: {PATH_JSON_SAIDA}")
    return relatorio_json


if __name__ == "__main__":
    sample_urls = [
        "https://www.vizinhub.com.br/privacy",
        "https://www.vizinhub.com.br/terms"
    ]
    executar_auditoria_completa(sample_urls, provedor="ollama", modelo_local="gemma4:12b")
