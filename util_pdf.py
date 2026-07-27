"""Módulo para extração e preparação da Base de Conhecimento em PDF.

Lê todos os PDFs da pasta Knowledge_Base/, converte em texto estruturado em .md
com rastreabilidade por páginas e nome do arquivo original.
"""

import os
import re
import sys
import pypdf

DIR_KNOWLEDGE_BASE = os.path.join(os.path.dirname(__file__), "Knowledge_Base")
DIR_TEXTOS_EXTRAIDOS = os.path.join(os.path.dirname(__file__), "extracted_texts")


def extrair_texto_pdf(caminho_pdf):
    """Extrai todo o texto de um arquivo PDF mantendo marcação de páginas."""
    nome_arquivo = os.path.basename(caminho_pdf)
    reader = pypdf.PdfReader(caminho_pdf)
    paginas_texto = []
    
    for num_pag, pagina in enumerate(reader.pages, start=1):
        texto = pagina.extract_text() or ""
        # Limpa espaços excessivos
        texto_limpo = re.sub(r'[ \t]+', ' ', texto).strip()
        if texto_limpo:
            header_pag = f"\n\n--- [Documento: {nome_arquivo} | Página {num_pag}] ---\n"
            paginas_texto.append(header_pag + texto_limpo)
            
    return "\n".join(paginas_texto)


def processar_base_conhecimento(force_reextract=False):
    """Processa todos os PDFs em Knowledge_Base e salva arquivos Markdown."""
    if not os.path.exists(DIR_KNOWLEDGE_BASE):
        raise FileNotFoundError(f"Diretório da base de conhecimento não encontrado: {DIR_KNOWLEDGE_BASE}")
        
    os.makedirs(DIR_TEXTOS_EXTRAIDOS, exist_ok=True)
    
    arquivos_pdf = [f for f in os.listdir(DIR_KNOWLEDGE_BASE) if f.lower().endswith(".pdf")]
    print(f"Encontrados {len(arquivos_pdf)} arquivos PDF em '{DIR_KNOWLEDGE_BASE}'")
    
    resultados = {}
    
    for pdf_nome in arquivos_pdf:
        caminho_pdf = os.path.join(DIR_KNOWLEDGE_BASE, pdf_nome)
        nome_base = os.path.splitext(pdf_nome)[0]
        # sanitiza nome do arquivo md
        nome_md_sanitizado = re.sub(r'[^a-zA-Z0-9_\-]', '_', nome_base) + ".md"
        caminho_md = os.path.join(DIR_TEXTOS_EXTRAIDOS, nome_md_sanitizado)
        
        if not force_reextract and os.path.exists(caminho_md):
            print(f" -> Usando cache existente: {nome_md_sanitizado}")
            with open(caminho_md, "r", encoding="utf-8") as f:
                conteudo = f.read()
        else:
            print(f" -> Processando PDF: {pdf_nome} ...")
            conteudo = extrair_texto_pdf(caminho_pdf)
            with open(caminho_md, "w", encoding="utf-8") as f:
                f.write(conteudo)
            print(f"    Salvo em: {caminho_md}")
            
        resultados[pdf_nome] = {
            "caminho_md": caminho_md,
            "conteudo": conteudo,
            "tamanho_caracteres": len(conteudo)
        }
        
    return resultados


def carregar_todos_textos_base():
    """Retorna uma string consolidada de toda a base de conhecimento extraída."""
    base_dict = processar_base_conhecimento(force_reextract=False)
    blocos = []
    for nome_pdf, info in base_dict.items():
        blocos.append(f"# BASE: {nome_pdf}\n\n{info['conteudo']}")
    return "\n\n" + "="*80 + "\n\n".join(blocos)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding='utf-8')
    res = processar_base_conhecimento(force_reextract=True)
    print("\nProcessamento concluído com sucesso!")
    for k, v in res.items():
        print(f"- {k}: {v['tamanho_caracteres']} caracteres extraídos.")
