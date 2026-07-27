# 🛡️ LGPD Standards and Laws Analyzer for Websites (GraphRAG)

Uma plataforma de auditoria automatizada de **Compliance Legal e Regulatória** para sites e serviços digitais, baseada em **GraphRAG (Retrieval-Augmented Generation em Grafo)**.

O sistema analisa políticas públicas de plataformas digitais (Termos de Uso, Política de Privacidade, Cookies, Suporte) contra a Base de Conhecimento formada pela **LGPD (Lei nº 13.709/2018)**, **ABNT NBR ISO/IEC 27001**, **ISO/IEC 27002**, **ISO 31000** e **TPRM (Gestão de Riscos de Terceiros)**.

---

## ✨ Funcionalidades Principais

- 🧠 **Engine GraphRAG com Grafo de Conhecimento:** Expansão de vizinhança ($k$-hops) sobre triplas regulatórias para recuperar contexto exato antes de enviar ao LLM.
- 🤖 **Suporte Dual a Modelos de IA:**
  - **Ollama Local (Sem Limites & 100% Offline):** Funciona localmente com modelos como `gemma4`, `llama3.2`, `qwen2.5` sem requisições pagas ou bloqueios de API.
  - **Google Gemini API:** Integração cloud com modelos Gemini 2.0.
- 🕸️ **Gerenciador de Triplas Persistente (`triplas.json`):** Salva e deduplica triplas normativas sem repetições, com suporte a incremento contínuo.
- 🔍 **Rastreabilidade Explicita de Evidências:** Associa cada apontamento ao trecho exato do site, incluindo **URL e número de linha**.
- 📊 **Interface Visual Interativa (Streamlit):** Dashboard web completo com KPIs, matriz resumo, visualização de subgrafos e exportação de relatórios.
- 📝 **Exportação Multi-Formato:** Gera automaticamente relatórios em `relatorio_auditoria.json` e `relatorio_auditoria.md` (com callouts e alertas do GitHub).

---

## 🛠️ Arquitetura do Projeto

```text
├── Knowledge_Base/           # PDFs das leis e normas (LGPD, ISO 27001, 27002, 31000)
├── extracted_texts/          # Textos extraídos e sanitizados com marcação de páginas
├── triplas.json              # Grafo de Conhecimento de triplas deduplicadas
├── compliance_graphrag.py    # Motor principal de auditoria GraphRAG
├── util_triplas.py           # Gerenciador de triplas (deduplicação e incremento)
├── util_scraper.py           # Web Scraper com indexação por linha
├── util_pdf.py               # Extrator de PDFs da base de conhecimento
├── util_comum.py             # Conector de IAs (Ollama Local & Gemini API)
├── json_to_markdown.py       # Conversor de JSON para Markdown formatado
├── run_audit_pipeline.py     # Orquestrador via linha de comando (CLI)
├── app_ui.py                 # Interface Web Visual (Streamlit)
├── relatorio_auditoria.json  # Relatório estruturado em JSON
└── relatorio_auditoria.md    # Relatório formatado em Markdown
```

---

## 🚀 Como Executar

### 1. Instalação das Dependências

```bash
pip install -r requirements.txt
```

### 2. Executando a Interface Visual Web (Streamlit)

```bash
python -m streamlit run app_ui.py
```

Acesse no seu navegador: **`http://localhost:8501`**

### 3. Executando via Linha de Comando (CLI)

```bash
python run_audit_pipeline.py https://www.vizinhub.com.br/privacy https://www.vizinhub.com.br/terms
```

---

## 🛡️ Normas Auditadas

- **LGPD (Lei 13.709/2018):** Identificação do Controlador, CNPJ, Bases Legais, Consentimento, DPO (Art. 41), Direitos do Titular (Art. 18), Segurança (Art. 46) e Incidentes (Art. 48).
- **ISO/IEC 27001 & 27002:** Controles de Criptografia (A.10), Segurança Operacional e Logs (A.12), Gestão de Fornecedores/Terceiros (A.15) e Gestão de Incidentes (A.16).
- **ISO 31000 & TPRM Framework:** Gestão e mitigação de riscos em ecossistemas de parceiros digitais.
