"""Utility module for API initialization, LLM calls (Gemini API & Ollama Local), and environment configuration.
"""

import json
import os
import sys
import time
import re
import requests

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
    from google import genai
    from google.genai import types
    HAS_NEW_GENAI = True
except ImportError:
    HAS_NEW_GENAI = False
    try:
        import google.generativeai as genai_old
        HAS_OLD_GENAI = True
    except ImportError:
        HAS_OLD_GENAI = False

MODELO_GERACAO = "gemini-2.0-flash"
OLLAMA_HOST = "http://localhost:11434"


def obter_api_key():
    """Obtém a chave da API do Gemini a partir das variáveis de ambiente."""
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not key:
        if os.path.exists(".env"):
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("GEMINI_API_KEY=") or line.startswith("GOOGLE_API_KEY="):
                        key = line.split("=", 1)[1].strip().strip('"').strip("'")
                        break
    return key


def criar_cliente():
    """Inicializa o cliente da API do Gemini."""
    api_key = obter_api_key()
    if not api_key:
        print("[AVISO] Nenhuma chave GEMINI_API_KEY ou GOOGLE_API_KEY encontrada.")
        
    if HAS_NEW_GENAI:
        return genai.Client(api_key=api_key) if api_key else genai.Client()
    elif HAS_OLD_GENAI:
        if api_key:
            genai_old.configure(api_key=api_key)
        return genai_old
    else:
        raise ImportError("Nenhuma biblioteca do Google GenAI instalada.")


def listar_modelos_ollama_locais(host: str = OLLAMA_HOST) -> list:
    """Lista todos os modelos de IA disponíveis no Ollama local."""
    try:
        r = requests.get(f"{host}/api/tags", timeout=2)
        if r.status_code == 200:
            models_data = r.json().get("models", [])
            return [m["name"] for m in models_data]
    except Exception:
        pass
    return []


def chamar_ollama_local(prompt: str, modelo: str = "qwen3.5:2b", host: str = OLLAMA_HOST, exigi_json: bool = True) -> str:
    """Realiza uma chamada direta ao servidor Ollama local (com suporte a modelos de raciocínio como qwen3.5:2b)."""
    url = f"{host}/api/generate"
    payload = {
        "model": modelo,
        "prompt": prompt,
        "stream": False
    }
    if exigi_json:
        payload["format"] = "json"

    try:
        r = requests.post(url, json=payload, timeout=180)
        r.raise_for_status()
        res_json = r.json()
        
        # Suporte a modelos normais e modelos de raciocínio/thinking (ex: qwen3.5:2b)
        resposta_texto = res_json.get("response") or res_json.get("thinking") or ""
        if not resposta_texto and isinstance(res_json.get("message"), dict):
            resposta_texto = res_json["message"].get("content", "")
            
        return resposta_texto
    except Exception as e:
        print(f"  [Aviso Ollama Local] Falha ao comunicar com {modelo} em {host}: {e}")
        return ""


def chamar_api(func_ou_metodo, *args, **kwargs):
    """Executa chamadas de API do Gemini com tratamento de erro 429 (rate limit) e retentativas seguras."""
    max_tentativas = 3
    for tentativa in range(max_tentativas):
        try:
            res = func_ou_metodo(*args, **kwargs)
            return res
        except Exception as e:
            err_msg = str(e)
            if "429" in err_msg or "RESOURCE_EXHAUSTED" in err_msg:
                tempo_espera = 15 * (tentativa + 1)
                print(f"  [Aviso Rate Limit 429 - Gemini API] Aguardando {tempo_espera}s para retentar...")
                time.sleep(tempo_espera)
            else:
                if tentativa == max_tentativas - 1:
                    print(f"  [Aviso API Error] {e}")
                    return None
                time.sleep(3)
    return None


def gerar_resposta_llm(prompt: str, provedor: str = "ollama", modelo_local: str = "qwen3.5:2b", cliente_gemini=None) -> str:
    """Interface unificada para geração de respostas por IA (Ollama Local ou Gemini API)."""
    provedor_clean = str(provedor).lower().strip()
    
    if provedor_clean == "ollama":
        resposta = chamar_ollama_local(prompt, modelo=modelo_local)
        if resposta:
            return resposta
        provedor_clean = "gemini"

    if provedor_clean == "gemini" and cliente_gemini:
        res = chamar_api(cliente_gemini.models.generate_content, model=MODELO_GERACAO, contents=prompt)
        if res and hasattr(res, "text"):
            return res.text
            
    return ""


def limpar_json_markdown(texto: str) -> str:
    """Remove blocos de código ```json ... ``` de respostas do LLM."""
    if not texto:
        return "{}"
    t = texto.strip()
    if t.startswith("```"):
        lines = t.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        t = "\n".join(lines).strip()
    return t


def extrair_json_seguro(texto: str, default=None):
    """Tenta converter uma resposta de LLM em JSON de forma extremamente robusta."""
    limpo = limpar_json_markdown(texto)
    try:
        return json.loads(limpo)
    except Exception:
        pass
        
    match_obj = re.search(r'(\{[\s\S]*\})', texto)
    if match_obj:
        try:
            return json.loads(match_obj.group(1))
        except Exception:
            pass
            
    match_arr = re.search(r'(\[[\s\S]*\])', texto)
    if match_arr:
        try:
            arr = json.loads(match_arr.group(1))
            return {"triplas": arr}
        except Exception:
            pass
            
    return default if default is not None else {}