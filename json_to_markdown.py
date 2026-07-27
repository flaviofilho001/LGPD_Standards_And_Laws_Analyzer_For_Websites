"""Módulo para conversão de relatórios de auditoria JSON em Markdown (.md) estruturado e formatado.

Recebe relatorio_auditoria.json e gera um arquivo Markdown (.md) de alta qualidade visual,
com tabelas, callouts do GitHub, badges de status e rastreabilidade explicita.
"""

import json
import os
import sys

PATH_JSON_DEFAULT = os.path.join(os.path.dirname(__file__), "relatorio_auditoria.json")
PATH_MD_DEFAULT = os.path.join(os.path.dirname(__file__), "relatorio_auditoria.md")


def badge_status(status: str) -> str:
    """Retorna um formato visual amigável com emoji para o status de compliance."""
    st = status.upper()
    if st == "CONFORME":
        return "🟢 **CONFORME**"
    elif st == "NAO_CONFORME" or st == "NÃO_CONFORME":
        return "🔴 **NÃO CONFORME**"
    elif st == "ATENCAO" or st == "ATENÇÃO":
        return "🟡 **ATENÇÃO / PARCIAL**"
    return f"⚪ **{status}**"


def gerar_markdown_do_json(caminho_json: str = PATH_JSON_DEFAULT, caminho_md_saida: str = PATH_MD_DEFAULT) -> str:
    """Lê o arquivo JSON estruturado e converte em um documento Markdown formatado."""
    if not os.path.exists(caminho_json):
        raise FileNotFoundError(f"Arquivo JSON não encontrado em: {caminho_json}")
        
    with open(caminho_json, "r", encoding="utf-8") as f:
        dados = json.load(f)
        
    meta = dados.get("metadata", {})
    fundamentacao = dados.get("fundamentacao", [])
    resumo_status = meta.get("resumo_status", {})
    
    linhas = []
    
    # 1. Título Principal
    linhas.append(f"# 🛡️ {dados.get('titulo', 'Relatório de Auditoria de Compliance')}")
    linhas.append("")
    
    # 2. Tabela de Metadados da Auditoria
    linhas.append("## 📋 Informações Gerais da Auditoria")
    linhas.append("")
    linhas.append("| Propriedade | Detalhe |")
    linhas.append("| :--- | :--- |")
    linhas.append(f"| **Data da Análise** | {meta.get('data_auditoria', 'N/A')} |")
    urls_str = "<br>".join([f"`{u}`" for u in meta.get("urls_analisadas", [])])
    linhas.append(f"| **Páginas Auditadas** | {urls_str} |")
    normas_str = ", ".join(meta.get("normas_base", []))
    linhas.append(f"| **Normas & Leis Base** | {normas_str} |")
    linhas.append(f"| **Índice Global de Conformidade** | **{meta.get('indice_conformidade', '0%')}** |")
    linhas.append(f"| **Status dos Requisitos** | 🟢 Conforme: {resumo_status.get('CONFORME', 0)} \| 🟡 Atenção: {resumo_status.get('ATENCAO', 0)} \| 🔴 Não Conforme: {resumo_status.get('NAO_CONFORME', 0)} |")
    linhas.append("")
    
    # 3. Introdução (Callout Note)
    linhas.append("## 📌 1. Visão Geral & Escopo")
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
        
        # Alerta de destaque se for Não Conforme ou Atenção
        if st in ["NAO_CONFORME", "NÃO_CONFORME"]:
            linhas.append("> [!WARNING]")
            linhas.append(f"> **Inconformidade Detectada:** Este item viola ou omite exigência legal expressa da norma (`{item.get('norma_referencia')}`).")
            linhas.append("")
        elif st in ["ATENCAO", "ATENÇÃO"]:
            linhas.append("> [!IMPORTANT]")
            linhas.append(f"> **Ponto de Atenção:** O item apresenta atendimento parcial, ambiguidade ou necessidade de complementação.")
            linhas.append("")
            
        # Trecho Rastreável
        linhas.append("#### 🔍 Evidência Extraída do Site (Rastreabilidade Explicita)")
        linhas.append("```text")
        linhas.append(f"{item.get('trecho_site_evidencia', 'Nenhuma evidência localizada.')}")
        linhas.append("```")
        linhas.append("")
        
        # Fundamentação Jurídica / Técnica
        linhas.append("#### 🧠 Fundamentação & Diagnóstico do Grafo")
        linhas.append(f"{item.get('explicacao_fundamentacao', '')}")
        linhas.append("")
        linhas.append("---")
        linhas.append("")
        
    # 6. Conclusão
    linhas.append("## 🎯 4. Conclusão & Diagnóstico de Risco")
    linhas.append("")
    linhas.append("> [!IMPORTANT]")
    linhas.append(f"> {dados.get('conclusao', '')}")
    linhas.append("")
    
    # 7. Próximos Passos & Plano de Ação
    linhas.append("## 🛠️ 5. Próximos Passos & Plano de Adequação Priorizado")
    linhas.append("")
    linhas.append("Recomenda-se a implementação das seguintes ações corretivas em ordem de prioridade:")
    linhas.append("")
    for passo in dados.get("proximos_passos", []):
        linhas.append(f"- [ ] {passo}")
    linhas.append("")
    
    # Rodapé
    linhas.append("---")
    linhas.append("*Relatório gerado automaticamente pelo Engine GraphRAG de Compliance & IA (LGPD + ISOs).*")
    
    conteudo_md = "\n".join(linhas)
    
    with open(caminho_md_saida, "w", encoding="utf-8") as f:
        f.write(conteudo_md)
        
    print(f" Documento Markdown gerado com sucesso!")
    print(f"    Salvo em: {caminho_md_saida}")
    return conteudo_md


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    c_json = sys.argv[1] if len(sys.argv) > 1 else PATH_JSON_DEFAULT
    c_md = sys.argv[2] if len(sys.argv) > 2 else PATH_MD_DEFAULT
    gerar_markdown_do_json(c_json, c_md)
