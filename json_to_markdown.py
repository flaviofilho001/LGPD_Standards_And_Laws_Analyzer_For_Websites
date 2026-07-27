"""Módulo de Geração de Documentação Markdown (.md) a partir de relatorio_auditoria.json.

Converte o relatório JSON de auditoria de compliance em um documento em formato Markdown (GitHub-flavored)
com tabelas, estatísticas, badges de status, citações de evidência e alertas de não conformidade.
"""

import json
import os
import sys

# Reconfigura o encoding do terminal Windows para UTF-8
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def badge_status(status: str) -> str:
    """Retorna uma tag formatada para o status."""
    st_upper = status.upper().strip()
    if st_upper == "CONFORME":
        return "🟢 `CONFORME`"
    elif st_upper in ["NAO_CONFORME", "NÃO_CONFORME"]:
        return "🔴 `NÃO CONFORME`"
    elif st_upper in ["ATENCAO", "ATENÇÃO"]:
        return "🟡 `ATENÇÃO`"
    return f"⚪ `{status}`"


def gerar_markdown_do_json(caminho_json: str, caminho_md_saida: str):
    """Lê relatorio_auditoria.json e gera o documento relatorio_auditoria.md."""
    if not os.path.exists(caminho_json):
        print(f"[ERRO] Arquivo JSON não encontrado em: {caminho_json}")
        return

    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)

    meta = dados.get("metadata", {})
    fundamentacao = dados.get("fundamentacao", [])
    resumo_st = meta.get("resumo_status", {})

    linhas = []

    # 1. Título e Metadados do Cabeçalho
    linhas.append(f"# 🛡️ {dados.get('titulo', 'Relatório de Auditoria de Compliance')}")
    linhas.append("")
    linhas.append("> **Autor / Desenvolvedor:** Flávio Mesquita — Universidade Federal da Paraíba (UFPB) — Ciência da Computação")
    linhas.append("> **Plataforma de Auditoria:** GraphRAG Compliance Engine (LGPD, ISO 27001, ISO 27002, ISO 31000 & TPRM)")
    linhas.append("")
    linhas.append("---")
    linhas.append("")
    
    # 2. Metadados Gerais da Análise
    linhas.append("## 📋 1. Metadados da Auditoria")
    linhas.append("")
    linhas.append(f"- **Data de Execução:** `{meta.get('data_auditoria', 'N/A')}`")
    linhas.append(f"- **Motor de Inteligência Artificial:** `{meta.get('provedor_ia', 'N/A')}`")
    linhas.append(f"- **Paralelização:** `{meta.get('paralelizacao_trabalhadores', 1)} tópico(s) simultâneo(s)`")
    linhas.append(f"- **Páginas Auditadas:** {', '.join([f'`{u}`' for u in meta.get('urls_analisadas', [])])}")
    linhas.append(f"- **Total de Requisitos Auditados:** `{meta.get('total_requisitos_auditados', 0)}`")
    linhas.append(f"- **Triplas no Grafo de Conhecimento:** `{meta.get('total_triplas_grafo', 0)}` (triplas.json)")
    linhas.append(f"- **Índice Global de Conformidade:** **`{meta.get('indice_conformidade', '0%')}`**")
    linhas.append("")
    linhas.append("### 📊 Resumo Executivo por Status")
    linhas.append(f"- 🟢 **Conformes:** `{resumo_st.get('CONFORME', 0)}`")
    linhas.append(f"- 🔴 **Não Conformes:** `{resumo_st.get('NAO_CONFORME', 0)}`")
    linhas.append(f"- 🟡 **Pontos de Atenção:** `{resumo_st.get('ATENCAO', 0)}`")
    linhas.append("")
    
    # 3. Introdução
    linhas.append("")
    linhas.append("> [!NOTE]")
    linhas.append(f"> {dados.get('introducao', '')}")
    linhas.append("")
    
    # 4. Tabela Resumo Executivo
    linhas.append("## 📊 2. Matriz Resumo de Compliance")
    linhas.append("")
    linhas.append("| ID | Requisito / Tópico | Categoria | Status | Norma de Referência |")
    linhas.append("| :--- | :--- | :--- | :--- | :--- |")
    for item in fundamentacao:
        st_badge = badge_status(item.get("status", ""))
        linhas.append(f"| `{item.get('item_id', 'N/A')}` | {item.get('titulo_item', '')} | {item.get('categoria', '')} | {st_badge} | `{item.get('norma_referencia', '')}` |")
    linhas.append("")
    
    # 5. Fundamentação Detalhada com Rastreabilidade
    linhas.append("## ⚖️ 3. Fundamentação Técnica Detalhada & Rastreabilidade")
    linhas.append("")
    linhas.append("Abaixo está a análise individualizada de cada ponto, correlacionando o texto extraído do site com as normas legais do Grafo de Conhecimento.")
    linhas.append("")
    
    for idx, item in enumerate(fundamentacao, start=1):
        st = item.get("status", "").upper()
        st_badge = badge_status(st)
        
        linhas.append(f"### 3.{idx} [{item.get('item_id')}] {item.get('titulo_item')}")
        linhas.append(f"**Categoria:** {item.get('categoria')}  ")
        linhas.append(f"**Status da Avaliação:** {st_badge}  ")
        linhas.append(f"**Norma / Artigo Base:** `{item.get('norma_referencia')}`")
        linhas.append("")
        
        if st in ["NAO_CONFORME", "NÃO_CONFORME"]:
            linhas.append("> [!WARNING]")
            linhas.append("> **Vulnerabilidade de Compliance Detectada!** A ausência ou inadequação desta cláusula expõe a organização a sanções da ANPD (Art. 52 da LGPD) e não conformidade com a ISO 27001/27002.")
            linhas.append("")
        elif st in ["ATENCAO", "ATENÇÃO"]:
            linhas.append("> [!IMPORTANT]")
            linhas.append("> **Ponto de Atenção!** O texto do site menciona o tópico, porém necessita de adequação técnica ou maior clareza.")
            linhas.append("")
            
        linhas.append("**🔍 Evidência Encontrada no Site (Rastreável por URL e Linha):**")
        linhas.append("```text")
        linhas.append(item.get("trecho_site_evidencia", "Nenhuma evidência localizada."))
        linhas.append("```")
        linhas.append("")
        linhas.append("**🧠 Diagnóstico & Fundamentação Técnica:**")
        linhas.append(item.get("explicacao_fundamentacao", ""))
        linhas.append("")
        linhas.append("---")
        linhas.append("")
        
    # 6. Conclusão e Próximos Passos
    linhas.append("## 🎯 4. Conclusão e Plano de Ação Recomendado")
    linhas.append("")
    linhas.append(dados.get("conclusao", ""))
    linhas.append("")
    linhas.append("### 🚀 Próximos Passos Prioritários:")
    for passo in dados.get("proximos_passos", []):
        linhas.append(f"- [ ] {passo}")
        
    linhas.append("")
    linhas.append("---")
    linhas.append("*Relatório gerado automaticamente pela suíte de auditoria **GraphRAG Compliance Engine**.*  ")
    linhas.append("*Desenvolvido por: **Flávio Mesquita** (UFPB - Ciência da Computação)*")

    conteudo_final = "\n".join(linhas)

    with open(caminho_md_saida, "w", encoding="utf-8") as f:
        f.write(conteudo_final)

    print(f" Documento Markdown gerado com sucesso!")
    print(f"    Salvo em: {caminho_md_saida}")


if __name__ == "__main__":
    dir_atual = os.path.dirname(__file__)
    p_json = os.path.join(dir_atual, "relatorio_auditoria.json")
    p_md = os.path.join(dir_atual, "relatorio_auditoria.md")
    gerar_markdown_do_json(p_json, p_md)
