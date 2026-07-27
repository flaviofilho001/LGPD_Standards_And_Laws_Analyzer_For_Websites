"""Módulo de Web Scraping e Processamento de Conteúdo de Sites.

Extrai o texto de Termos de Uso, Políticas de Privacidade, Suporte, Cookies, etc.
Organiza os parágrafos com numeração de linha e URL para garantir 100% de rastreabilidade.
"""

import os
import re
import sys
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}


def raspagem_url(url: str, timeout: int = 15) -> dict:
    """Realiza a raspagem de uma URL e retorna parágrafos numerados para rastreabilidade."""
    url = url.strip()
    resultado = {
        "url": url,
        "sucesso": False,
        "titulo": "",
        "paragrafos": [],
        "texto_bruto": "",
        "erro": None
    }
    
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout, verify=False)
        response.raise_for_status()
        
        # Define codificação correta
        if response.encoding is None or response.encoding == 'ISO-8859-1':
            response.encoding = response.apparent_encoding or 'utf-8'
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove elementos irrelevantes (scripts, estilos, cabeçalhos de navegação)
        for elem in soup(["script", "style", "nav", "footer", "header", "noscript", "svg", "button"]):
            elem.decompose()
            
        # Título da página
        titulo = soup.title.string.strip() if soup.title and soup.title.string else url
        resultado["titulo"] = titulo
        
        # Extrai elementos de texto estruturado (h1-h6, p, li, tr)
        elementos = soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "li", "td", "th"])
        
        paragrafos_processados = []
        num_linha = 1
        
        for el in elementos:
            texto = el.get_text(separator=" ", strip=True)
            # Ignora textos insignificantes
            if not texto or len(texto) < 5:
                continue
                
            # Limpa espaços em branco duplicados
            texto_limpo = re.sub(r'\s+', ' ', texto)
            
            # Evita duplicatas consecutivas exatas
            if paragrafos_processados and paragrafos_processados[-1]["texto"] == texto_limpo:
                continue
                
            paragrafos_processados.append({
                "linha": num_linha,
                "tag": el.name,
                "texto": texto_limpo,
                "url": url,
                "referencia_rastreavel": f"[{url} | Linha {num_linha}] \"{texto_limpo[:100]}...\""
            })
            num_linha += 1
            
        resultado["sucesso"] = True
        resultado["paragrafos"] = paragrafos_processados
        resultado["texto_bruto"] = "\n".join([f"L{p['linha']} ({p['tag']}): {p['texto']}" for p in paragrafos_processados])
        
    except Exception as e:
        resultado["erro"] = str(e)
        resultado["paragrafos"] = []
        resultado["texto_bruto"] = f"Erro ao acessar {url}: {e}"
        
    return resultado


def raspar_multiplas_urls(urls: list) -> list:
    """Raspa múltiplas URLs e retorna a lista de resultados estruturados."""
    resultados = []
    for url in urls:
        print(f" -> Realizando scraping de: {url}")
        res = raspagem_url(url)
        if res["sucesso"]:
            print(f"    Sucesso! {len(res['paragrafos'])} parágrafos extraídos.")
        else:
            print(f"    [Aviso] Falha ao acessar URL ({res['erro']}).")
        resultados.append(res)
    return resultados


if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    sys.stdout.reconfigure(encoding='utf-8')
    
    test_urls = ["https://www.vizinhub.com.br/privacy", "https://www.vizinhub.com.br/terms"]
    res = raspar_multiplas_urls(test_urls)
    for r in res:
        print(f"\nSite: {r['titulo']} ({r['url']}) - Sucesso: {r['sucesso']}")
        if r['paragrafos']:
            print("Primeiros 3 parágrafos:")
            for p in r['paragrafos'][:3]:
                print(f"  {p['referencia_rastreavel']}")
