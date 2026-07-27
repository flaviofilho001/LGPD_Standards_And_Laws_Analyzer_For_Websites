"""Módulo Gerador de Triplas (gerador_triplas.py).

Gera triplas regulatórias no formato (Origem, Relação, Destino, Fonte) a partir da Base de Conhecimento,
suportando IA Local (Ollama), Gemini API, ou conversão de arquivos de ontologia (.ttl / Turtle / RDF).
Deduplica e incrementa automaticamente no triplas.json.
"""

import os
import sys
import json
import re
from tqdm import tqdm

# Reconfigura o encoding do terminal Windows para UTF-8
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from util_comum import gerar_resposta_llm, extrair_json_seguro, criar_cliente, obter_api_key
from util_triplas import carregar_ou_inicializar_triplas, incrementar_triplas, PATH_TRIPLAS_JSON
from util_pdf import processar_base_conhecimento

DIR_TEXTOS = os.path.join(os.path.dirname(__file__), "extracted_texts")

try:
    import rdflib
    HAS_RDFLIB = True
except ImportError:
    HAS_RDFLIB = False


PROMPT_GERACAO_TRIPLAS = """Extraia triplas conceituais do texto normativo abaixo.

Responda EXCLUSIVAMENTE em formato JSON com o seguinte modelo exato (sem texto explicativo antes ou depois):

```json
{{
  "triplas": [
    {{
      "origem": "LGPD_Art_18",
      "relacao": "EXIGE",
      "destino": "Canal_Atendimento_Titular",
      "fonte": "LGPD Art. 18"
    }}
  ]
}}
```

REGRAS:
- origem: Nome do artigo ou norma (sem espaços).
- relacao: Verbo em maiúsculas (ex: EXIGE, PROIBE, REQUER_EVIDENCIA, APLICA_CONTROLE, REGULA, GARANTE).
- destino: Nome do requisito ou obrigação (sem espaços).
- fonte: Citação do artigo/fonte.

TEXTO DA NORMA:
{texto_chunk}
"""


def converter_ttl_para_triplas(caminho_ttl: str) -> list:
    """Converte um arquivo ontológico .ttl (Turtle/RDF) em triplas no formato do projeto."""
    if not HAS_RDFLIB:
        print("[ERRO] rdflib não instalado. Instale com: pip install rdflib")
        return []

    if not os.path.exists(caminho_ttl):
        print(f"[ERRO] Arquivo .ttl não encontrado em: {caminho_ttl}")
        return []

    g = rdflib.Graph()
    try:
        g.parse(caminho_ttl, format="turtle")
    except Exception as e:
        print(f"[ERRO] Falha ao ler arquivo Turtle {caminho_ttl}: {e}")
        return []

    triplas_extraidas = []
    for s, p, o in g:
        s_clean = str(s).split("#")[-1].split("/")[-1]
        p_clean = str(p).split("#")[-1].split("/")[-1].upper()
        o_clean = str(o).split("#")[-1].split("/")[-1]
        
        s_clean = re.sub(r'\s+', '_', s_clean)
        p_clean = re.sub(r'[^A-Z0-9_]', '_', p_clean)
        o_clean = re.sub(r'\s+', '_', o_clean)

        if s_clean and p_clean and o_clean:
            triplas_extraidas.append({
                "origem": s_clean,
                "relacao": p_clean,
                "destino": o_clean,
                "fonte": f"Arquivo TTL: {os.path.basename(caminho_ttl)}"
            })

    print(f" -> [RDF/TTL] Extraídas {len(triplas_extraidas)} triplas do arquivo '{caminho_ttl}'.")
    return triplas_extraidas


def extrair_triplas_de_texto(texto_chunk: str, provedor: str = "ollama", modelo_local: str = "qwen3.5:2b", cliente_gemini=None) -> list:
    """Extrai triplas de um bloco de texto usando IA (Ollama Local ou Gemini API)."""
    prompt = PROMPT_GERACAO_TRIPLAS.format(texto_chunk=texto_chunk[:2200])
    
    resposta_texto = gerar_resposta_llm(
        prompt, 
        provedor=provedor, 
        modelo_local=modelo_local, 
        cliente_gemini=cliente_gemini
    )
    
    if resposta_texto:
        dados_json = extrair_json_seguro(resposta_texto)
        if dados_json and "triplas" in dados_json and isinstance(dados_json["triplas"], list):
            return dados_json["triplas"]
            
    return []


def gerar_triplas_da_base_conhecimento(provedor: str = "ollama", modelo_local: str = "qwen3.5:2b", max_arquivos: int = 4) -> list:
    """Varre a pasta extracted_texts/, gera novas triplas via IA e incrementa no triplas.json."""
    print("=" * 80)
    print(f" 🧠 INICIANDO GERADOR AUTOMÁTICO DE TRIPLAS (Provedor: {provedor.upper()} | Modelo: {modelo_local})")
    print("=" * 80)

    processar_base_conhecimento(force_reextract=False)

    if not os.path.exists(DIR_TEXTOS):
        print(f"[ERRO] Diretório {DIR_TEXTOS} não encontrado.")
        return []

    arquivos_md = [os.path.join(DIR_TEXTOS, f) for f in os.listdir(DIR_TEXTOS) if f.endswith(".md")]
    arquivos_md = arquivos_md[:max_arquivos]
    
    cliente_gemini = None
    if provedor.lower() == "gemini" and obter_api_key():
        try:
            cliente_gemini = criar_cliente()
        except Exception:
            pass

    novas_triplas_geradas = []

    for arq_path in tqdm(arquivos_md, desc=f"Gerando Triplas ({modelo_local})", unit="arquivo"):
        nome_arq = os.path.basename(arq_path)
        with open(arq_path, "r", encoding="utf-8") as f:
            conteudo = f.read()

        blocos = [conteudo[i:i+2000] for i in range(0, len(conteudo), 1800)]
        
        for idx, bloco in enumerate(blocos[:3]):
            triplas_bloco = extrair_triplas_de_texto(
                bloco, 
                provedor=provedor, 
                modelo_local=modelo_local, 
                cliente_gemini=cliente_gemini
            )
            for t in triplas_bloco:
                if not t.get("fonte") or t["fonte"] == "CitacaoDaNorma":
                    t["fonte"] = nome_arq
            novas_triplas_geradas.extend(triplas_bloco)

    print(f"\n -> Total de candidatas a triplas geradas pela IA: {len(novas_triplas_geradas)}")

    if novas_triplas_geradas:
        triplas_finais = incrementar_triplas(novas_triplas_geradas)
        return triplas_finais
    else:
        print(" -> Nenhuma nova tripla inédita adicionada nesta rodada.")
        return carregar_ou_inicializar_triplas()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Gerador Automático de Triplas GraphRAG")
    parser.add_argument("--provedor", default="ollama", choices=["ollama", "gemini"], help="Provedor de IA")
    parser.add_argument("--modelo", default="qwen3.5:2b", help="Modelo Ollama Local")
    parser.add_argument("--ttl", help="Caminho para arquivo .ttl (Turtle/RDF) para converter")

    args = parser.parse_args()

    if args.ttl:
        print(f"Convertendo arquivo TTL '{args.ttl}' para triplas.json...")
        triplas_ttl = converter_ttl_para_triplas(args.ttl)
        if triplas_ttl:
            incrementar_triplas(triplas_ttl)
    else:
        gerar_triplas_da_base_conhecimento(provedor=args.provedor, modelo_local=args.modelo)
