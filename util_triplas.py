"""Módulo de Gerenciamento e Persistência de Triplas do Grafo de Conhecimento (triplas.json).

Garante que o arquivo triplas.json é consultado antes de qualquer busca,
elimina duplicações de triplas que levam à mesma coisa e permite o incremento contínuo de novas triplas.
"""

import json
import os
import time

PATH_TRIPLAS_JSON = os.path.join(os.path.dirname(__file__), "triplas.json")

# Triplas Base Iniciais de Compliance (LGPD, ISO 27001, ISO 27002, ISO 31000, TPRM)
TRIPLAS_BASE_INICIAIS = [
    # LGPD - Identificação e DPO
    {"origem": "LGPD", "relacao": "EXIGE", "destino": "LGPD_Art_41_DPO", "fonte": "LGPD Art. 41"},
    {"origem": "LGPD_Art_41_DPO", "relacao": "REQUER_EVIDENCIA", "destino": "Divulgação_Pública_Contato_DPO", "fonte": "LGPD Art. 41 § 1º"},
    {"origem": "LGPD", "relacao": "EXIGE", "destino": "LGPD_Art_5_Identificacao_Controlador", "fonte": "LGPD Art. 5, VI"},
    {"origem": "LGPD_Art_5_Identificacao_Controlador", "relacao": "REQUER_EVIDENCIA", "destino": "Razao_Social_e_CNPJ_Claros", "fonte": "LGPD Art. 6, VI (Transparência)"},
    
    # LGPD - Consentimento e Bases Legais
    {"origem": "LGPD", "relacao": "EXIGE", "destino": "LGPD_Art_7_Bases_Legais", "fonte": "LGPD Art. 7"},
    {"origem": "LGPD_Art_7_Bases_Legais", "relacao": "DISPOE_SOBRE", "destino": "Especificacao_Finalidade_Tratamento", "fonte": "LGPD Art. 6, I"},
    {"origem": "LGPD", "relacao": "EXIGE", "destino": "LGPD_Art_8_Revogacao_Consentimento", "fonte": "LGPD Art. 8 § 5º"},
    {"origem": "LGPD_Art_8_Revogacao_Consentimento", "relacao": "REQUER_EVIDENCIA", "destino": "Procedimento_Gratuito_Facil_OptOut", "fonte": "LGPD Art. 8 § 4º e 5º"},
    
    # LGPD - Direitos do Titular
    {"origem": "LGPD", "relacao": "EXIGE", "destino": "LGPD_Art_18_Direitos_Titular", "fonte": "LGPD Art. 18"},
    {"origem": "LGPD_Art_18_Direitos_Titular", "relacao": "INCLUI_DIREITO", "destino": "Acesso_Correcao_Eliminacao_Portabilidade", "fonte": "LGPD Art. 18, I a IX"},
    {"origem": "LGPD_Art_18_Direitos_Titular", "relacao": "REQUER_EVIDENCIA", "destino": "Canal_Atendimento_Solicitacoes_Titular", "fonte": "LGPD Art. 19 (Prazo 15 dias)"},
    
    # LGPD & ISO 27001/27002 - Segurança da Informação
    {"origem": "LGPD", "relacao": "EXIGE", "destino": "LGPD_Art_46_Seguranca_Tecnica_Admin", "fonte": "LGPD Art. 46"},
    {"origem": "LGPD_Art_46_Seguranca_Tecnica_Admin", "relacao": "APLICA_CONTROLE", "destino": "ISO_27002_Controle_10_Criptografia", "fonte": "ISO 27002 Seção 10"},
    {"origem": "ISO_27002_Controle_10_Criptografia", "relacao": "REQUER_EVIDENCIA", "destino": "Cifragem_Dados_Transito_HTTPS_TLS", "fonte": "ISO 27002 Controle 10.1"},
    {"origem": "LGPD_Art_46_Seguranca_Tecnica_Admin", "relacao": "APLICA_CONTROLE", "destino": "ISO_27002_Controle_12_Backup_Logs", "fonte": "ISO 27002 Seção 12"},
    {"origem": "ISO_27002_Controle_12_Backup_Logs", "relacao": "REQUER_EVIDENCIA", "destino": "Retencao_Logs_e_Protecao_Malware", "fonte": "ISO 27002 Controle 12.4"},
    
    # LGPD & TPRM / ISO 31000 - Compartilhamento e Terceiros
    {"origem": "LGPD", "relacao": "REGULA", "destino": "LGPD_Art_33_Transferencia_Compartilhamento", "fonte": "LGPD Art. 33 e 34"},
    {"origem": "LGPD_Art_33_Transferencia_Compartilhamento", "relacao": "APLICA_CONTROLE", "destino": "ISO_27002_Controle_15_TPRM_Fornecedores", "fonte": "ISO 27002 Seção 15"},
    {"origem": "ISO_27002_Controle_15_TPRM_Fornecedores", "relacao": "APLICA_CONTROLE", "destino": "TPRM_Gestao_Riscos_Terceiros", "fonte": "ISO 31000 & TPRM Framework"},
    {"origem": "TPRM_Gestao_Riscos_Terceiros", "relacao": "REQUER_EVIDENCIA", "destino": "Clausulas_Contratuais_Compliance_Terceiros", "fonte": "ISO 27002 Controle 15.1"},
    
    # LGPD - Incidentes de Segurança
    {"origem": "LGPD", "relacao": "EXIGE", "destino": "LGPD_Art_48_Notificacao_Incidentes", "fonte": "LGPD Art. 48"},
    {"origem": "LGPD_Art_48_Notificacao_Incidentes", "relacao": "APLICA_CONTROLE", "destino": "ISO_27002_Controle_16_Gestao_Incidentes", "fonte": "ISO 27002 Seção 16"},
    {"origem": "LGPD_Art_48_Notificacao_Incidentes", "relacao": "REQUER_EVIDENCIA", "destino": "Procedimento_Comunicacao_ANPD_Titulares", "fonte": "LGPD Art. 48 § 1º"},

    # LGPD - Retenção e Eliminação de Dados (AUD-009)
    {"origem": "LGPD", "relacao": "REGULA", "destino": "LGPD_Art_15_16_Retencao_Eliminacao", "fonte": "LGPD Art. 15 e 16"},
    {"origem": "LGPD_Art_15_16_Retencao_Eliminacao", "relacao": "APLICA_CONTROLE", "destino": "ISO_27002_Controle_8_Retencao", "fonte": "ISO 27002 Controle 8.3"},
    {"origem": "LGPD_Art_15_16_Retencao_Eliminacao", "relacao": "REQUER_EVIDENCIA", "destino": "Politica_Prazo_Descarte_Eliminacao_Dados", "fonte": "LGPD Art. 16"},

    # LGPD - Dados Sensíveis e Crianças/Adolescentes (AUD-010)
    {"origem": "LGPD", "relacao": "PROTEGE", "destino": "LGPD_Art_11_14_Dados_Sensives_Menores", "fonte": "LGPD Art. 11 e 14"},
    {"origem": "LGPD_Art_11_14_Dados_Sensives_Menores", "relacao": "APLICA_CONTROLE", "destino": "ISO_27002_Controle_8_Classificacao", "fonte": "ISO 27002 Controle 8.2"},
    {"origem": "LGPD_Art_11_14_Dados_Sensives_Menores", "relacao": "REQUER_EVIDENCIA", "destino": "Consentimento_Destacado_Sensivel_Menor", "fonte": "LGPD Art. 11, I e Art. 14 § 1º"}
]


def deduplicar_triplas(lista_triplas: list) -> list:
    """Remove repetições de triplas que levam à mesma coisa (chave única: origem + relacao + destino)."""
    vistas = set()
    triplas_unicas = []
    
    for t in lista_triplas:
        origem = str(t.get("origem", "")).strip()
        relacao = str(t.get("relacao", "")).strip()
        destino = str(t.get("destino", "")).strip()
        fonte = str(t.get("fonte", "Norma")).strip()
        
        chave = (origem.lower(), relacao.lower(), destino.lower())
        
        if chave not in vistas and origem and relacao and destino:
            vistas.add(chave)
            triplas_unicas.append({
                "origem": origem,
                "relacao": relacao,
                "destino": destino,
                "fonte": fonte
            })
            
    return triplas_unicas


def carregar_ou_inicializar_triplas(caminho: str = PATH_TRIPLAS_JSON) -> list:
    """Carrega o arquivo triplas.json se existir. Caso contrário, inicializa e salva o arquivo."""
    if os.path.exists(caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
                triplas = dados.get("triplas", [])
                # Garante que novas triplas base também sejam mescladas se ausentes
                combinadas = deduplicar_triplas(triplas + TRIPLAS_BASE_INICIAIS)
                if len(combinadas) > len(triplas):
                    salvar_triplas(combinadas, caminho)
                return combinadas
        except Exception as e:
            print(f" -> [Aviso] Falha ao ler {caminho} ({e}). Reinicializando base de triplas.")
            
    triplas_iniciais = deduplicar_triplas(TRIPLAS_BASE_INICIAIS)
    salvar_triplas(triplas_iniciais, caminho)
    return triplas_iniciais


def salvar_triplas(lista_triplas: list, caminho: str = PATH_TRIPLAS_JSON):
    """Salva a lista de triplas no arquivo triplas.json estruturado e deduplicado."""
    unicas = deduplicar_triplas(lista_triplas)
    
    estrutura = {
        "metadata": {
            "descricao": "Base de Triplas Deduplicadas do Grafo de Conhecimento de Compliance (LGPD, ISOs, TPRM)",
            "versao": "1.1",
            "ultima_atualizacao": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_triplas": len(unicas)
        },
        "triplas": unicas
    }
    
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(estrutura, f, ensure_ascii=False, indent=2)
        
    print(f" -> [triplas.json] Arquivo salvo em '{caminho}' com {len(unicas)} triplas únicas.")


def incrementar_triplas(novas_triplas: list, caminho: str = PATH_TRIPLAS_JSON) -> list:
    """Adiciona novas triplas ao arquivo triplas.json sem duplicar as existentes."""
    atuais = carregar_ou_inicializar_triplas(caminho)
    tamanho_antes = len(atuais)
    
    combinadas = atuais + novas_triplas
    deduplicadas = deduplicar_triplas(combinadas)
    
    novas_adicionadas = len(deduplicadas) - tamanho_antes
    if novas_adicionadas > 0:
        salvar_triplas(deduplicadas, caminho)
        print(f" -> [triplas.json] +{novas_adicionadas} novas triplas incrementadas com sucesso!")
    else:
        print(" -> [triplas.json] Nenhuma nova tripla inédita adicionada (todas já existiam no arquivo).")
        
    return deduplicadas


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    t = carregar_ou_inicializar_triplas()
    print(f"Triplas verificadas: {len(t)} itens.")
