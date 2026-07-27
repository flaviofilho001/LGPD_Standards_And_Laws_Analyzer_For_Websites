"""Pipeline Principal de Auditoria de Compliance GraphRAG.

Orquestra todo o fluxo:
  1. Garante que os PDFs da Base de Conhecimento estão processados em extracted_texts/
  2. Raspa e extrai textos com numeração de linha e rastreabilidade das URLs fornecidas
  3. Realiza a auditoria GraphRAG cruzando com a Base de Conhecimento (LGPD + ISOs)
  4. Gera o arquivo relatorio_auditoria.json
  5. Converte o JSON em relatorio_auditoria.md de alta qualidade visual

Uso:
  python run_audit_pipeline.py [URL1] [URL2] ...
  Exemplo:
  python run_audit_pipeline.py https://www.vizinhub.com.br/terms https://www.vizinhub.com.br/privacy
"""

import sys
import os
import urllib3

from populate_knowledge_texts import popular as popular_normas_base
from util_pdf import processar_base_conhecimento
from compliance_graphrag import executar_auditoria_completa
from json_to_markdown import gerar_markdown_do_json

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    sys.stdout.reconfigure(encoding='utf-8')
    print("\n" + "=" * 80)
    print(" 🚀 INICIANDO SISTEMA DE AUDITORIA DE COMPLIANCE GRAPHRAG (LGPD & ISOs)")
    print("=" * 80 + "\n")
    
    # 1. Prepara Base de Conhecimento (PDFs e Normas)
    print("[Passo 1/4] Verificando e carregando a Base de Conhecimento...")
    popular_normas_base()
    processar_base_conhecimento(force_reextract=False)
    
    # 2. Define as URLs a serem auditadas
    if len(sys.argv) > 1:
        urls = sys.argv[1:]
    else:
        urls = [
            "https://www.vizinhub.com.br/privacy",
            "https://www.vizinhub.com.br/terms"
        ]
        
    print(f"\n[Passo 2/4] URLs selecionadas para auditoria:")
    for u in urls:
        print(f"  • {u}")
        
    # 3. Executa a Auditoria GraphRAG (gera relatorio_auditoria.json)
    print("\n[Passo 3/4] Executando análise GraphRAG e gerando relatorio_auditoria.json...")
    relatorio_json = executar_auditoria_completa(urls)
    
    # 4. Gera o documento Markdown (relatorio_auditoria.md)
    print("\n[Passo 4/4] Convertendo JSON em relatório Markdown (relatorio_auditoria.md)...")
    path_json = os.path.join(os.path.dirname(__file__), "relatorio_auditoria.json")
    path_md = os.path.join(os.path.dirname(__file__), "relatorio_auditoria.md")
    gerar_markdown_do_json(path_json, path_md)
    
    print("\n" + "=" * 80)
    print(" 🎉 AUDITORIA CONCLUÍDA COM SUCESSO!")
    print(f" 📄 Arquivo JSON: {path_json}")
    print(f" 📝 Arquivo Markdown: {path_md}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
