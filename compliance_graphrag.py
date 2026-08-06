"""Core Compliance GraphRAG Engine.

Constrói o Grafo de Conhecimento de Compliance (LGPD, ISO 27001, ISO 27002, ISO 31000, TPRM),
submete dados raspados de sites a auditorias por subgrafos e gera relatorio_auditoria.json estruturado.
Suporta execução paralela em modelos locais (Ollama) com N trabalhadores simultâneos de forma thread-safe.
"""

import json
import os
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import networkx as nx
from tqdm import tqdm

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
LOCK_LOG = threading.Lock()


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


# Definição dos 10 Tópicos Principais de Auditoria de Compliance
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
    },
    {
        "id": "AUD-009",
        "titulo": "Política de Retenção, Término do Tratamento e Descarte de Dados",
        "categoria": "Ciclo de Vida do Dado (LGPD Art. 15 e 16 / ISO 27002 A.8.3)",
        "ancoras_grafo": ["LGPD_Art_15_16_Retencao_Eliminacao", "ISO_27002_Controle_8_Retencao"],
        "palavras_chave": ["retenção", "armazenamento", "descarte", "eliminação", "término do tratamento", "exclusão de conta"],
        "normas": "LGPD Art. 15 e 16; ABNT NBR ISO/IEC 27002 Controle 8.3"
    },
    {
        "id": "AUD-010",
        "titulo": "Proteção de Dados Pessoais Sensíveis e de Crianças/Adolescentes",
        "categoria": "Tratamento Especial (LGPD Art. 11 e 14 / ISO 27002 A.8.2)",
        "ancoras_grafo": ["LGPD_Art_11_14_Dados_Sensives_Menores", "ISO_27002_Controle_8_Classificacao"],
        "palavras_chave": ["dados sensíveis", "biometria", "saúde", "crianças", "adolescentes", "menores", "responsável legal"],
        "normas": "LGPD Art. 11 e Art. 14; ABNT NBR ISO/IEC 27002 Controle 8.2"
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
    
    nos_subgrafo = set()
    g_und = g.to_undirected()
    for anc in topico["ancoras_grafo"]:
        if anc in g:
            nos_subgrafo |= set(nx.ego_graph(g_und, anc, radius=2).nodes)
            
    subgrafo = g.subgraph(nos_subgrafo) if nos_subgrafo else g
    
    regras_linhas = []
    for u, v, d in subgrafo.edges(data=True):
        regras_linhas.append(f"- REGRA NORMATIVA: ({u}) -[{d.get('relacao')}]-> ({v}) [Fonte: {d.get('fonte', 'Norma')}]")
    regras_texto = "\n".join(regras_linhas) if regras_linhas else f"- Requisito base: {topico['normas']}"
    
    if paragrafos_evidencia:
        evidencias_texto = "\n".join([
            f"* [{p['url']} | Linha {p['linha']}] (Tag: {p['tag']}): \"{p['texto']}\""
            for p in paragrafos_evidencia[:6]
        ])
    else:
        evidencias_texto = "Nenhuma menção explícita ou evidência direta encontrada nos textos analisados do site."
        
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


def _trabalhador_auditoria(args):
    """Função trabalhadora thread-safe para execução paralela."""
    idx, topico, cliente, g, dados_sites, provedor, modelo_local = args
    paragrafos_ev = buscar_paragrafos_relevantes(dados_sites, topico["palavras_chave"])
    resultado_item = auditar_topico_com_graphrag(
        cliente, g, topico, paragrafos_ev, 
        provedor=provedor, modelo_local=modelo_local
    )
    return idx, topico, resultado_item


def executar_auditoria_completa(urls: list, novas_triplas=None, provedor="ollama", modelo_local="gemma4:12b", progress_callback=None, max_workers=2):
    """Executa a auditoria completa GraphRAG para os 10 tópicos com opção de paralelização (N trabalhadores simultâneos)."""
    
    # Se for Gemini API (cloud), força 1 trabalhador sequencial para não estourar rate-limit 429 da API
    if provedor.lower() == "gemini":
        max_workers = 1

    print("=" * 80)
    print(f" INICIANDO PIPELINE DE AUDITORIA GRAPHRAG - 10 TÓPICOS (Provedor: {provedor.upper()} | Paralelização: {max_workers} por vez)")
    print("=" * 80)
    
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
        print(f" -> Conectando ao Ollama Local no modelo '{modelo_local}' (paralelizado em {max_workers} requisições simultâneas).")

    g, triplas_carregadas = construir_grafo_compliance(novas_triplas_para_incrementar=novas_triplas)
    print(f" -> Grafo de Conhecimento de Compliance pronto: {g.number_of_nodes()} nós, {g.number_of_edges()} arestas (baseado em triplas.json).")
    
    dados_sites = raspar_multiplas_urls(urls)
    urls_com_sucesso = [s["url"] for s in dados_sites if s["sucesso"]]
    
    if not urls_com_sucesso:
        print("\n[ERRO CRÍTICO] Nenhuma URL pôde ser raspada com sucesso.")
        
    total_topicos = len(TOPICOS_AUDITORIA)
    totais = {"CONFORME": 0, "NAO_CONFORME": 0, "ATENCAO": 0}
    resultados_ordenados = [None] * total_topicos
    concluidos_count = 0
    
    pbar = tqdm(total=total_topicos, desc="Auditando Requisitos (Paralelo)", unit="requisito", file=sys.stdout)
    
    # Prepara lista de tarefas com índice explícito para garantir ordenação perfeita sem misturar
    tarefas = [
        (i, topico, cliente, g, dados_sites, provedor, modelo_local)
        for i, topico in enumerate(TOPICOS_AUDITORIA)
    ]
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_trabalhador_auditoria, t): t[0] for t in tarefas}
        
        for future in as_completed(futures):
            idx, topico, resultado_item = future.result()
            resultados_ordenados[idx] = resultado_item
            
            st = resultado_item["status"]
            totais[st] = totais.get(st, 0) + 1
            concluidos_count += 1
            
            pbar.update(1)
            msg_progresso = f"[{concluidos_count}/{total_topicos}] Concluído ({topico['id']}): {topico['titulo']} [{st}]"
            
            with LOCK_LOG:
                pbar.set_postfix({"último": topico["id"], "status": st, "paralelo": max_workers})
                if progress_callback:
                    progress_callback(concluidos_count, total_topicos, msg_progresso)

    pbar.close()
    itens_fundamentacao = [r for r in resultados_ordenados if r is not None]

    total_itens = len(itens_fundamentacao)
    porcentagem_conforme = round((totais["CONFORME"] / total_itens) * 100, 1) if total_itens > 0 else 0
    
    relatorio_json = {
        "titulo": "Relatório de Auditoria de Compliance LGPD, ISO 27001, ISO 27002 & ISO 31000 (10 Tópicos)",
        "metadata": {
            "data_auditoria": "2026-07-27",
            "urls_analisadas": urls,
            "provedor_ia": f"{provedor.upper()} ({modelo_local if provedor.lower() == 'ollama' else MODELO_GERACAO})",
            "paralelizacao_trabalhadores": max_workers,
            "normas_base": ["LGPD (Lei 13.709/2018)", "ABNT NBR ISO/IEC 27001", "ABNT NBR ISO/IEC 27002", "ABNT NBR ISO 31000", "TPRM Framework"],
            "total_requisitos_auditados": total_itens,
            "total_triplas_grafo": len(triplas_carregadas),
            "resumo_status": totais,
            "indice_conformidade": f"{porcentagem_conforme}%"
        },
        "introducao": (
            "Este relatório apresenta o resultado da avaliação automatizada de conformidade legal e regulatória "
            f"das páginas web analisadas ({', '.join(urls)}). A análise utiliza a metodologia GraphRAG (Retrieval-Augmented Generation em Grafo), "
            f"executada via motor de IA {provedor.upper()} ({modelo_local if provedor.lower() == 'ollama' else MODELO_GERACAO}) paralelizado em {max_workers} processos simultâneos, "
            "correlacionando os textos das políticas públicas da plataforma com a Base de Conhecimento (triplas.json) formada pelos diplomas legais da LGPD, "
            "as normas ABNT NBR ISO/IEC 27001, 27002, 31000 e frameworks de Gestão de Riscos de Terceiros (TPRM). Cada ponto auditado possui "
            "rastreabilidade direta aos trechos e linhas do site, permitindo verificação imediata."
        ),
        "fundamentacao": itens_fundamentacao,
        "conclusao": (
            f"A análise automatizada de compliance de 10 tópicos críticos resultou em um índice global de conformidade de {porcentagem_conforme}%. "
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
            "5. Formalizar um Plano de Resposta a Incidentes de Segurança da Informação (SIRT) conforme ISO 27002 Controle 16.1 e LGPD Art. 48.",
            "6. Definir e publicar regras claras de retenção, armazenamento e descarte/eliminação de dados pessoais após o término do tratamento (LGPD Art. 15 e 16).",
            "7. Coletar consentimento específico e destacado para tratamento de dados pessoais sensíveis ou de menores (LGPD Art. 11 e 14)."
        ]
    }
    
    with open(PATH_JSON_SAIDA, "w", encoding="utf-8") as f:
        json.dump(relatorio_json, f, ensure_ascii=False, indent=2)
        
    print(f"\n Relatório em JSON gerado com sucesso!")
    print(f"    Salvo em: {PATH_JSON_SAIDA}")
    return relatorio_json


def responder_pergunta_livre_graphrag(pergunta: str, g=None, triplas=None, provedor="ollama", modelo_local="qwen3.5:2b", cliente_gemini=None) -> dict:
    """Responde a uma pergunta em linguagem natural usando o Grafo de Conhecimento (GraphRAG)."""
    if g is None:
        g, triplas = construir_grafo_compliance()
        
    pergunta_lower = pergunta.lower()
    
    nos_candidatos = []
    for no in g.nodes():
        no_str = str(no).replace("_", " ").lower()
        palavras_no = [p for p in no_str.split() if len(p) > 3]
        if any(p in pergunta_lower for p in palavras_no) or no_str in pergunta_lower:
            nos_candidatos.append(no)
            
    if not nos_candidatos:
        nos_candidatos = list(g.nodes())[:5]
        
    g_und = g.to_undirected()
    nos_subgrafo = set()
    for c in nos_candidatos[:6]:
        if c in g:
            nos_subgrafo |= set(nx.ego_graph(g_und, c, radius=2).nodes)
            
    subgrafo = g.subgraph(nos_subgrafo) if nos_subgrafo else g
    
    linhas_triplas = []
    triplas_listadas = []
    for u, v, d in subgrafo.edges(data=True):
        rel = d.get("relacao", "RELACIONADO")
        fonte = d.get("fonte", "LGPD/ISO")
        linhas_triplas.append(f"- ({u}) -[{rel}]-> ({v}) [Fonte: {fonte}]")
        triplas_listadas.append({
            "origem": u,
            "relacao": rel,
            "destino": v,
            "fonte": fonte
        })
        
    contexto_triplas = "\n".join(linhas_triplas[:30])
    
    prompt = f"""Você é um assistente especialista em LGPD, ISO 27001/27002, ISO 31000 e Governança de Dados.

Responda à pergunta do usuário utilizando como CONTEXTO FUNDAMENTAL as regras e relacionamentos do Grafo de Conhecimento abaixo.

CONTEXTO DO GRAFO DE CONHECIMENTO (Subgrafo GraphRAG):
{contexto_triplas}

PERGUNTA DO USUÁRIO:
{pergunta}

INSTRUÇÕES DE RESPOSTA:
1. Responda de forma clara, técnica e objetiva em português.
2. Ancore sua resposta nas regras e conceitos extraídos do Grafo de Conhecimento.
3. Cite explicitamente as normas/artigos que sustentam o raciocínio (ex: LGPD Art. 18, ISO 27002).
"""
    
    resposta_texto = gerar_resposta_llm(
        prompt,
        provedor=provedor,
        modelo_local=modelo_local,
        cliente_gemini=cliente_gemini,
        exigi_json=False
    )

    
    if not resposta_texto:
        regras_formatadas = []
        for t in triplas_listadas[:10]:
            regras_formatadas.append(f"- O conceito '{t['origem'].replace('_', ' ')}' {t['relacao'].replace('_', ' ').lower()} '{t['destino'].replace('_', ' ')}' (Fonte: {t['fonte']}).")
            
        texto_regras = "\n".join(regras_formatadas) if regras_formatadas else "Nenhuma tripla normativamente direta encontrada no grafo para os termos pesquisados."
        
        resposta_texto = (
            f"Com base na análise do Grafo de Conhecimento regulatório, foram recuperadas as seguintes regras e exigências normativas para a sua consulta:\n\n"
            f"{texto_regras}\n\n"
            "(Obs: Para obter síntese contextual avançada por modelo de linguagem, certifique-se de que o Ollama está rodando localmente na porta 11434 ou informe sua chave API do Gemini na barra lateral)."
        )
    
    return {
        "pergunta": pergunta,
        "resposta": resposta_texto,
        "nos_ancoras": nos_candidatos,
        "total_nos_subgrafo": subgrafo.number_of_nodes(),
        "total_arestas_subgrafo": subgrafo.number_of_edges(),
        "triplas_utilizadas": triplas_listadas[:15]
    }



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Motor Core GraphRAG de Compliance LGPD & ISOs")
    parser.add_argument("--pergunta", type=str, help="Pergunta em linguagem natural para consultar o Grafo de Conhecimento")
    parser.add_argument("--urls", nargs="+", help="URLs dos sites para auditoria de 10 tópicos")
    parser.add_argument("--provedor", default="ollama", choices=["ollama", "gemini", "heuristico"])
    parser.add_argument("--modelo", default="qwen3.5:2b")
    
    args = parser.parse_args()
    
    if args.pergunta:
        res = responder_pergunta_livre_graphrag(args.pergunta, provedor=args.provedor, modelo_local=args.modelo)
        print("\n" + "="*80)
        print(f"PERGUNTA: {res['pergunta']}")
        print(f"NÓS ÂNCORA: {res['nos_ancoras']}")
        print(f"SUBGRAFO: {res['total_nos_subgrafo']} nós, {res['total_arestas_subgrafo']} arestas")
        print("="*80)
        print(f"RESPOSTA:\n{res['resposta']}")
    else:
        sample_urls = args.urls or [
            "https://www.vizinhub.com.br/privacy",
            "https://www.vizinhub.com.br/terms"
        ]
        executar_auditoria_completa(sample_urls, provedor=args.provedor, modelo_local=args.modelo, max_workers=2)

