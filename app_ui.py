"""Interface Visual Streamlit para a Suite de Auditoria GraphRAG (LGPD & ISOs).

Execução:
    python -m streamlit run app_ui.py
"""

import json
import os
import sys

# Reconfigura stdout/stderr para UTF-8 de forma segura para o Windows
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

import streamlit as st

from compliance_graphrag import construir_grafo_compliance, executar_auditoria_completa
from json_to_markdown import gerar_markdown_do_json
from util_pdf import processar_base_conhecimento
from util_triplas import carregar_ou_inicializar_triplas, incrementar_triplas, PATH_TRIPLAS_JSON
from util_comum import listar_modelos_ollama_locais

PATH_JSON = os.path.join(os.path.dirname(__file__), "relatorio_auditoria.json")
PATH_MD = os.path.join(os.path.dirname(__file__), "relatorio_auditoria.md")
DIR_TEXTOS = os.path.join(os.path.dirname(__file__), "extracted_texts")

# Configuração da página Streamlit
st.set_page_config(
    page_title="GraphRAG Compliance Suite",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS para Estética Moderna (Glassmorphism & CoresHarmônicas)
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(90deg, #10B981, #3B82F6, #6366F1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.1rem;
        color: #9CA3AF;
        margin-bottom: 1.5rem;
    }
    .status-conforme {
        background-color: #065F46;
        color: #D1FAE5;
        padding: 0.3rem 0.8rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .status-nao-conforme {
        background-color: #991B1B;
        color: #FEE2E2;
        padding: 0.3rem 0.8rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .status-atencao {
        background-color: #92400E;
        color: #FEF3C7;
        padding: 0.3rem 0.8rem;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)


def carregar_json_relatorio():
    if os.path.exists(PATH_JSON):
        with open(PATH_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def main():
    # Header Principal
    st.markdown('<div class="main-header">🛡️ GraphRAG Compliance & Auditoria Suite</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Auditoria de Conformidade Legal com Opção de IA Local (Ollama - Sem Limites) ou Cloud (Gemini API)</div>', unsafe_allow_html=True)

    # Sidebar - Configurações da Auditoria
    st.sidebar.image("https://img.icons8.com/isometric-folders/100/security-checked.png", width=70)
    st.sidebar.header("⚙️ Configurações da Análise")
    
    # 1. Seleção do Provedor de IA
    provedor_opcao = st.sidebar.radio(
        "🤖 Provedor de Inteligência Artificial:",
        options=["🤖 Ollama Local (Sem Limites)", "☁️ Google Gemini API (Com Limites)", "⚙️ Motor de Regras (Sem IA)"],
        index=0,
        help="Ollama Local roda 100% no seu computador sem limites de requisições por minuto e sem custos de API."
    )
    
    provedor_cod = "ollama" if "Ollama" in provedor_opcao else ("gemini" if "Gemini" in provedor_opcao else "heuristico")
    modelo_local_sel = "gemma4:12b"
    
    if provedor_cod == "ollama":
        modelos_detectados = listar_modelos_ollama_locais()
        if modelos_detectados:
            modelo_local_sel = st.sidebar.selectbox(
                "Modelo Local Detectado no Ollama:",
                options=modelos_detectados,
                index=0
            )
            st.sidebar.success(f"🟢 Ollama ativo com {len(modelos_detectados)} modelo(s) local(is)!")
        else:
            modelo_local_sel = st.sidebar.text_input("Nome do Modelo Ollama:", value="gemma4:12b")
            st.sidebar.info("💡 Certifique-se de que o serviço do Ollama está rodando localmente na porta 11434.")
            
    elif provedor_cod == "gemini":
        api_key_input = st.sidebar.text_input(
            "Chave API do Gemini:",
            type="password",
            help="Defina a variável de ambiente GEMINI_API_KEY ou insira aqui."
        )
        if api_key_input:
            os.environ["GEMINI_API_KEY"] = api_key_input
            
    st.sidebar.divider()

    urls_input = st.sidebar.text_area(
        "URLs para Auditoria (uma por linha):",
        value="https://www.vizinhub.com.br/privacy\nhttps://www.vizinhub.com.br/terms",
        height=120,
        help="Insira os links dos Termos de Uso, Política de Privacidade, Suporte ou Cookies da plataforma a ser auditada."
    )

    triplas_atuais = carregar_ou_inicializar_triplas()
    st.sidebar.info(f"📊 **triplas.json**: {len(triplas_atuais)} triplas únicas cadastradas.")
    
    btn_executar = st.sidebar.button("🚀 Executar Auditoria GraphRAG", width="stretch", type="primary")

    if btn_executar:
        urls_lista = [u.strip() for u in urls_input.splitlines() if u.strip()]
        if not urls_lista:
            st.error("Por favor, insira pelo menos uma URL válida.")
        else:
            msg_spinner = f"⏳ Executando auditoria via {provedor_opcao}..."
            with st.spinner(msg_spinner):
                rel_json = executar_auditoria_completa(
                    urls_lista, 
                    provedor=provedor_cod, 
                    modelo_local=modelo_local_sel
                )
                gerar_markdown_do_json(PATH_JSON, PATH_MD)
                st.success("✅ Auditoria GraphRAG concluída com sucesso!")
                st.rerun()

    # Carrega dados do último relatório
    dados_relatorio = carregar_json_relatorio()

    if not dados_relatorio:
        st.info("👋 Nenhuma auditoria foi executada ainda. Insira as URLs na barra lateral e clique em **Executar Auditoria GraphRAG**.")
        return

    # Tabs de Navegação da Interface
    tab_dash, tab_md, tab_triplas, tab_kb = st.tabs([
        "📊 Dashboard de Compliance",
        "📝 Relatório Markdown & Downloads",
        "🕸️ Gerenciador de Triplas (triplas.json)",
        "📜 Base de Conhecimento (PDFs)"
    ])

    meta = dados_relatorio.get("metadata", {})
    fundamentacao = dados_relatorio.get("fundamentacao", [])
    resumo_st = meta.get("resumo_status", {})

    # TAB 1: DASHBOARD
    with tab_dash:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Índice de Conformidade", meta.get("indice_conformidade", "0%"), delta="Score Global")
        c2.metric("🟢 Itens Conformes", resumo_st.get("CONFORME", 0))
        c3.metric("🔴 Não Conformidades", resumo_st.get("NAO_CONFORME", 0), delta_color="inverse")
        c4.metric("🟡 Pontos de Atenção", resumo_st.get("ATENCAO", 0))

        st.caption(f"🤖 **Motor da Análise:** `{meta.get('provedor_ia', 'N/A')}`")

        st.divider()

        col_f1, col_f2 = st.columns([1, 3])
        with col_f1:
            filtro_status = st.selectbox("Filtrar por Status:", ["Todos", "🟢 CONFORME", "🔴 NAO_CONFORME", "🟡 ATENCAO"])

        items_filtrados = fundamentacao
        if filtro_status != "Todos":
            st_limpo = filtro_status.split()[-1]
            items_filtrados = [i for i in fundamentacao if i.get("status") == st_limpo]

        st.subheader(f"📋 Requisitos Auditados ({len(items_filtrados)} itens)")

        for item in items_filtrados:
            st_val = item.get("status", "")
            
            with st.expander(f"[{item.get('item_id')}] {item.get('titulo_item')} — {st_val}", expanded=(st_val == "NAO_CONFORME")):
                st.markdown(f"**Categoria:** {item.get('categoria')} | **Norma:** `{item.get('norma_referencia')}`")
                
                st.markdown("**🔍 Evidência do Site (Rastreabilidade por URL & Linha):**")
                st.code(item.get("trecho_site_evidencia"), language="text")
                
                st.markdown("**🧠 Diagnóstico & Fundamentação Técnica:**")
                st.write(item.get("explicacao_fundamentacao"))

    # TAB 2: RELATÓRIO MARKDOWN & DOWNLOADS
    with tab_md:
        st.subheader("📄 Relatório Estruturado em Markdown (.md) & Downloads")
        
        c_dl1, c_dl2, c_dl3 = st.columns(3)
        if os.path.exists(PATH_JSON):
            with open(PATH_JSON, "rb") as f_json:
                c_dl1.download_button("⬇️ Baixar relatorio_auditoria.json", data=f_json, file_name="relatorio_auditoria.json", mime="application/json")
        if os.path.exists(PATH_MD):
            with open(PATH_MD, "rb") as f_md:
                c_dl2.download_button("⬇️ Baixar relatorio_auditoria.md", data=f_md, file_name="relatorio_auditoria.md", mime="text/markdown")
        if os.path.exists(PATH_TRIPLAS_JSON):
            with open(PATH_TRIPLAS_JSON, "rb") as f_trip:
                c_dl3.download_button("⬇️ Baixar triplas.json", data=f_trip, file_name="triplas.json", mime="application/json")

        st.divider()

        if os.path.exists(PATH_MD):
            with open(PATH_MD, "r", encoding="utf-8") as f:
                conteudo_md = f.read()
            st.markdown(conteudo_md)

    # TAB 3: GERENCIADOR DE TRIPLAS (triplas.json)
    with tab_triplas:
        st.subheader("🕸️ Base de Triplas Deduplicadas (triplas.json)")
        st.write("O arquivo `triplas.json` armazena as regras em formato `(Origem) -[Relação]-> (Destino)`. "
                 "Novas triplas são adicionadas sem repetições para expandir continuamente o conhecimento do sistema.")
        
        triplas_lista = carregar_ou_inicializar_triplas()
        
        with st.form("form_incrementar_tripla"):
            st.markdown("#### ➕ Incrementar Nova Tripla de Norma/Requisito")
            f_col1, f_col2, f_col3, f_col4 = st.columns(4)
            in_origem = f_col1.text_input("Origem (ex: LGPD_Art_18):")
            in_relacao = f_col2.text_input("Relação (ex: EXIGE):")
            in_destino = f_col3.text_input("Destino (ex: Canal_Gratuito_OptOut):")
            in_fonte = f_col4.text_input("Fonte/Norma (ex: LGPD Art. 18 IX):")
            
            btn_add = st.form_submit_button("Adicionar / Incrementar no triplas.json")
            if btn_add:
                if in_origem and in_relacao and in_destino:
                    nova_t = [{"origem": in_origem, "relacao": in_relacao, "destino": in_destino, "fonte": in_fonte or "Manual"}]
                    res = incrementar_triplas(nova_t)
                    st.success("✅ Tripla processada! Se era inédita, foi incrementada sem duplicatas.")
                    st.rerun()
                else:
                    st.warning("Preencha Origem, Relação e Destino.")

        st.divider()
        st.markdown(f"**Total de Triplas Únicas:** `{len(triplas_lista)}`")
        
        t_table = []
        for idx, t in enumerate(triplas_lista, start=1):
            t_table.append({
                "#": idx,
                "Origem (Nó)": t["origem"],
                "Relação (Aresta)": t["relacao"],
                "Destino (Nó)": t["destino"],
                "Fonte / Norma": t.get("fonte", "Norma")
            })
        st.dataframe(t_table, use_container_width=True)

    # TAB 4: BASE DE CONHECIMENTO (PDFs)
    with tab_kb:
        st.subheader("📚 Documentos da Base de Conhecimento (PDFs Processados)")
        if os.path.exists(DIR_TEXTOS):
            arquivos_md = [f for f in os.listdir(DIR_TEXTOS) if f.endswith(".md")]
            doc_sel = st.selectbox("Selecione a Norma / Documento extraído:", arquivos_md)
            if doc_sel:
                with open(os.path.join(DIR_TEXTOS, doc_sel), "r", encoding="utf-8") as f:
                    st.text_area("Conteúdo do Documento (com marcas de páginas):", value=f.read(), height=450)


if __name__ == "__main__":
    main()
