# LGPD Standards and Laws Analyzer for Websites (GraphRAG)

[![Autor](https://img.shields.io/badge/Autor-Fl%C3%A1vio%20Mesquita-blue.svg)](https://github.com/flaviofilho001)
[![Instituição](https://img.shields.io/badge/UFPB-Ci%C3%Aan-cia%20da%20Computa%C3%A7%C3%A3o-green.svg)](https://www.ufpb.br)
[![Python](https://img.shields.io/badge/Python-3.10%2B-yellow.svg)](https://www.python.org/)
[![GraphRAG](https://img.shields.io/badge/Engine-GraphRAG%20%2B%20NetworkX%20%2B%20RDF-purple.svg)](https://networkx.org/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-red.svg)](https://streamlit.io/)

Uma plataforma de auditoria automatizada de **Compliance Legal e Regulatória** para sites e serviços digitais, desenvolvida por **Flávio Mesquita** (Universidade Federal da Paraíba - UFPB / Ciência da Computação).

O sistema utiliza a arquitetura **GraphRAG (Retrieval-Augmented Generation em Grafo)** para correlacionar políticas públicas de plataformas digitais (Termos de Uso, Política de Privacidade, Cookies, Suporte) com a Base de Conhecimento regulatória formada pela **LGPD (Lei nº 13.709/2018)**, **ABNT NBR ISO/IEC 27001**, **ISO/IEC 27002**, **ISO 31000** e o framework **TPRM (Gestão de Riscos de Terceiros)**.

---

## Autor e Créditos Acadêmicos

- **Autores:** Flávio Mesquita, Yuri De Lima, John Victor
- **Instituição:** Universidade Federal da Paraíba (UFPB)
- **Curso:** Bacharelado em Ciência da Computação
- **Repositório GitHub:** [flaviofilho001/LGPD_Standards_And_Laws_Analyzer_For_Websites](https://github.com/flaviofilho001/LGPD_Standards_And_Laws_Analyzer_For_Websites)
- **Relatório Oficial SBC:** [Artigo_SBC_LGPD_GraphRAG.pdf](Artigo_SBC_LGPD_GraphRAG.pdf)

---

## Funcionalidades Principais

- **10 Tópicos Críticos de Compliance Auditados:**
  - **AUD-001:** Identificação do Controlador, Razão Social e CNPJ (*LGPD Art. 5º VI / Art. 6º VI*).
  - **AUD-002:** Bases Legais, Consentimento e Especificação da Finalidade (*LGPD Art. 6º I/II / Art. 7º*).
  - **AUD-003:** Direitos dos Titulares e Canal de Atendimento de Requisições (*LGPD Art. 18 / Art. 19*).
  - **AUD-004:** Indicação Pública do Encarregado pelo Tratamento de Dados - DPO (*LGPD Art. 41*).
  - **AUD-005:** Medidas de Segurança, Criptografia e Proteção de Dados (*LGPD Art. 46 / ISO 27002 A.10 & A.12*).
  - **AUD-006:** Compartilhamento com Terceiros e Transferência Internacional (*LGPD Art. 33/34 / ISO 27002 A.15 / ISO 31000*).
  - **AUD-007:** Gestão de Cookies, Tecnologias de Rastreamento e Opt-Out (*LGPD Art. 8º § 5º / Art. 18 IX*).
  - **AUD-008:** Notificação e Resposta a Incidentes de Segurança (*LGPD Art. 48 / ISO 27002 A.16*).
  - **AUD-009:** Política de Retenção, Término do Tratamento e Descarte de Dados (*LGPD Art. 15/16 / ISO 27002 A.8.3*).
  - **AUD-010:** Proteção de Dados Pessoais Sensíveis e de Crianças/Adolescentes (*LGPD Art. 11/14 / ISO 27002 A.8.2*).

- **Consultas em Linguagem Natural (Chat GraphRAG):** Faça qualquer pergunta livre em linguagem natural e receba respostas fundamentadas com subgrafos normativos ativados.
- **Suporte à Trilha A (Web Semântica - RDF/OWL & SPARQL):** Ontologia serializada em formato Turtle (`knowledge_graph.ttl`), inferência lógica OWL-RL (`owlrl`) e script de consultas SPARQL (`carregar_grafo_rdf.py`).
- **Motor GraphRAG com Grafo de Conhecimento (NetworkX & rdflib):** Expansão de vizinhança ($k$-hops) sobre triplas regulatórias para recuperar contexto exato antes do envio ao LLM.
- **Suporte Dual de Inteligência Artificial:**
  - **Ollama Local (Sem Limites & 100% Offline):** Executa localmente com modelos como `qwen3.5:2b`, `gemma4:12b`, `gemma4:26b` sem custos de API ou bloqueios por rate-limit.
  - **Google Gemini API:** Integração cloud com modelos Gemini 2.0.
- **Paralelização Thread-Safe de Tópicos:** Suporta a execução concorrente de múltiplos tópicos de auditoria no modelo local para multiplicar a velocidade de processamento.
- **Gerador Automático de Triplas (`gerador_triplas.py`):** IA extrai triplas inéditas da base de conhecimento e converte/exporta arquivos ontológicos `.ttl` (Turtle / RDF / OWL).
- **Rastreabilidade por URL e Número de Linha:** Cada apontamento de compliance referencia a URL exata e a linha onde a evidência foi localizada.
- **Interface Visual Interativa (Streamlit):** Dashboard web completo com KPIs, filtros por status, chat em linguagem natural, visualização de subgrafos e exportação de relatórios.

---

## Arquitetura do Repositório

```text
├── Knowledge_Base/           # PDFs originais das leis e normas (LGPD, ISO 27001, 27002, 31000)
├── extracted_texts/          # Textos extraídos dos PDFs com marcação de páginas
├── triplas.json              # Grafo de Conhecimento de triplas deduplicadas
├── knowledge_graph.ttl       # Ontologia oficial serializada em sintaxe Turtle (RDF/OWL)
├── carregar_grafo_rdf.py     # Carregador RDF, Inferência OWL-RL e Consultas SPARQL
├── compliance_graphrag.py    # Motor principal de auditoria GraphRAG & Pergunta em Linguagem Natural
├── gerador_triplas.py        # Gerador automático de triplas via IA e sincronizador de .ttl
├── util_triplas.py           # Gerenciador de triplas (deduplicação e incremento)
├── util_scraper.py           # Web Scraper com indexação e rastreabilidade por linha
├── util_pdf.py               # Extrator de PDFs da base de conhecimento
├── util_comum.py             # Router unificado de IAs (Ollama Local & Gemini API)
├── json_to_markdown.py       # Conversor de relatórios JSON para Markdown formatado
├── run_audit_pipeline.py     # Orquestrador via linha de comando (CLI)
├── app_ui.py                 # Dashboard Web Interativo (Streamlit)
├── Artigo_SBC_LGPD_GraphRAG.pdf # Relatório no formato de artigo científico SBC
├── relatorio_auditoria.json  # Saída estruturada em JSON
├── relatorio_auditoria.md    # Saída formatada em Markdown
└── requirements.txt          # Dependências do projeto Python
```

---

## Como Executar

### 1. Requisitos Prévios

- **Python 3.10** ou superior.
- **Ollama** (Opcional, para execução local sem limites): [https://ollama.com/](https://ollama.com/)
  - Baixe um modelo local: `ollama pull qwen3.5:2b` ou `ollama pull gemma4:12b`

### 2. Instalação das Dependências

Clone o repositório e instale as dependências:

```bash
git clone git@github.com:flaviofilho001/LGPD_Standards_And_Laws_Analyzer_For_Websites.git
cd LGPD_Standards_And_Laws_Analyzer_For_Websites
pip install -r requirements.txt
```

### 3. Executando a Interface Web (Streamlit Dashboard)

```bash
python -m streamlit run app_ui.py
```

Acesse no navegador: **`http://localhost:8501`**

### 4. Consultas em Linguagem Natural via Linha de Comando (CLI)

```bash
python compliance_graphrag.py --pergunta "Quais os direitos dos titulares previstos no Artigo 18 da LGPD?"
```

### 5. Executando a Ontologia RDF & Consultas SPARQL (Trilha A)

```bash
python carregar_grafo_rdf.py
```

### 6. Executando o Gerador Automático de Triplas (`gerador_triplas.py`)

Para extrair novas triplas da base de conhecimento usando o modelo local `qwen3.5:2b`:

```bash
python gerador_triplas.py --provedor ollama --modelo qwen3.5:2b
```

Para exportar o arquivo `knowledge_graph.ttl`:

```bash
python gerador_triplas.py --export-ttl
```

---

## Licença

Este projeto é disponibilizado para fins acadêmicos, de pesquisa e auditabilidade sob a licença **MIT**.

---

**Desenvolvido por Flávio Mesquita**  
*Universidade Federal da Paraíba (UFPB) — Ciência da Computação*
