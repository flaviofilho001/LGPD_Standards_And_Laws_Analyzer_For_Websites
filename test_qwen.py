import requests

url = 'http://localhost:11434/api/generate'
payload = {
    'model': 'qwen3.5:2b',
    'prompt': 'Extraia em JSON com as chaves origem, relacao, destino. Exemplo: {"triplas": [{"origem": "LGPD", "relacao": "EXIGE", "destino": "DPO"}]}',
    'format': 'json',
    'stream': False
}

try:
    print("Enviando requisição com format=json...")
    r = requests.post(url, json=payload, timeout=180)
    print("HTTP Status Code:", r.status_code)
    res_json = r.json()
    print("Full Ollama Response Keys:", list(res_json.keys()))
    print("Response text:", repr(res_json.get("response")))
    print("Thinking/Message text:", repr(res_json.get("thinking") or res_json.get("message")))
except Exception as e:
    print("Erro ao chamar Ollama:", e)
