"""Popula os textos das normas LGPD e ISO 27002 na pasta extracted_texts/ com artigos e controles detalhados.
"""

import os

DIR_TEXTOS_EXTRAIDOS = os.path.join(os.path.dirname(__file__), "extracted_texts")
os.makedirs(DIR_TEXTOS_EXTRAIDOS, exist_ok=True)

TEXTO_LGPD = """# LGPD - LEI GERAL DE PROTEÇÃO DE DADOS PESSOAIS (Lei nº 13.709/2018)

--- [Documento: LGPD.pdf | Página 1] ---
CAPÍTULO I - DISPOSIÇÕES GERAIS
Art. 1º Esta Lei dispõe sobre o tratamento de dados pessoais, inclusive nos meios digitais, por pessoa natural ou por pessoa jurídica de direito público ou privado, com o objetivo de proteger os direitos fundamentais de liberdade e de privacidade e o livre desenvolvimento da personalidade da pessoa natural.

Art. 2º A disciplina da proteção de dados pessoais tem como fundamentos:
I - o respeito à privacidade;
II - a autodeterminação informativa;
III - a liberdade de expressão, de informação, de comunicação e de opinião;
IV - a inviolabilidade da intimidade, da honra e da imagem;
V - o desenvolvimento econômico e tecnológico e a inovação;
VI - a livre iniciativa, a livre concorrência e a defesa do consumidor; e
VII - os direitos humanos, o livre desenvolvimento da personalidade e a dignidade das pessoas naturais.

--- [Documento: LGPD.pdf | Página 2] ---
Art. 5º Para os fins desta Lei, considera-se:
I - dado pessoal: informação relacionada a pessoa natural identificada ou identificável;
II - dado pessoal sensível: dado pessoal sobre origem racial ou étnica, convicção religiosa, opinião política, filiação a sindicato ou a organização de caráter religioso, filosófico ou político, dado referente à saúde ou à vida sexual, dado genético ou biométrico, quando vinculado a uma pessoa natural;
VI - controlador: pessoa natural ou jurídica, de direito público ou privado, a quem competem as decisões referentes ao tratamento de dados pessoais;
VII - operador: pessoa natural ou jurídica, de direito público ou privado, que realiza o tratamento de dados pessoais em nome do controlador;
VIII - encarregado (DPO): pessoa indicada pelo controlador e operador para atuar como canal de comunicação entre o controlador, os titulares dos dados e a Autoridade Nacional de Proteção de Dados (ANPD);
X - tratamento: toda operação realizada com dados pessoais, como as que se referem a coleta, produção, recepção, classificação, utilização, acesso, reprodução, transmissão, distribuição, processamento, arquivamento, armazenamento, eliminação, avaliação ou controle da informação, modificação, comunicação, transferência, difusão ou extração.

--- [Documento: LGPD.pdf | Página 3] ---
Art. 6º As atividades de tratamento de dados pessoais deverão observar a boa-fé e os seguintes princípios:
I - finalidade: realização do tratamento para propósitos legítimos, específicos, explícitos e informados ao titular, sem possibilidade de tratamento posterior de forma incompatível com essas finalidades;
II - adequação: compatibilidade do tratamento com as finalidades informadas ao titular, de acordo com o contexto do tratamento;
III - necessidade: limitação do tratamento ao mínimo necessário para a realização de suas finalidades, com abrangência dos dados pertinentes, proporcionais e não excessivos em relação às finalidades do tratamento de dados;
IV - livre acesso: garantia, aos titulares, de consulta facilitada e gratuita sobre a forma e a duração do tratamento, bem como sobre a integralidade de seus dados pessoais;
V - qualidade dos dados: garantia, aos titulares, de exatidão, clareza, relevância e atualização dos dados, de acordo com a necessidade e para o cumprimento da finalidade de seu tratamento;
VI - transparência: garantia, aos titulares, de informações claras, precisas e facilmente acessíveis sobre a realização do tratamento e os respectivos agentes de tratamento, observados os segredos comercial e industrial;
VII - segurança: utilização de medidas técnicas e administrativas aptas a proteger os dados pessoais de acessos não autorizados e de situações acidentais ou ilícitas de destruição, perda, alteração, comunicação ou difusão;
VIII - prevenção: adoção de medidas para prevenir a ocorrência de danos em virtude do tratamento de dados pessoais;
IX - não discriminação: impossibilidade de realização do tratamento para fins discriminatórios ilícitos ou abusivos;
X - responsabilização e prestação de contas: demonstração, pelo agente, da adoção de medidas eficazes e capazes de comprovar a observância e o cumprimento das normas de proteção de dados pessoais e, inclusive, da eficácia dessas medidas.

--- [Documento: LGPD.pdf | Página 4] ---
CAPÍTULO II - DO TRATAMENTO DE DADOS PESSOAIS
Art. 7º O tratamento de dados pessoais somente poderá ser realizado nas seguintes hipóteses:
I - mediante o fornecimento de consentimento pelo titular;
II - para o cumprimento de obrigação legal ou regulatória pelo controlador;
V - quando necessário para a execução de contrato ou de procedimentos preliminares relacionados a contrato do qual seja parte o titular, a pedido do titular do dado;
VI - para o exercício regular de direitos em processo judicial, administrativo ou arbitral;
IX - quando necessário para atender aos interesses legítimos do controlador ou de terceiro, exceto no caso de prevalecerem direitos e liberdades fundamentais do titular que exijam a proteção dos dados pessoais.

Art. 8º O consentimento previsto no inciso I do art. 7º desta Lei deverá ser fornecido por escrito ou por outro meio que demonstre a manifestação de vontade do titular.
§ 1º Caso o consentimento seja fornecido por escrito, este deverá constar de cláusula destacada das demais cláusulas contratuais.
§ 4º O consentimento pode ser revogado a qualquer momento mediante manifestação expressa do titular, por procedimento gratuito e facilitado.
§ 5º A ausência de consentimento para tratamentos que dependam exclusivamente dele impede a realização das operações.

--- [Documento: LGPD.pdf | Página 5] ---
Art. 11. O tratamento de dados pessoais sensíveis somente poderá ocorrer nas seguintes hipóteses:
I - quando o titular ou seu responsável legal consentir, de forma específica e destacada, para finalidades específicas;
II - sem fornecimento de consentimento do titular, nas hipóteses em que for indispensável para:
a) cumprimento de obrigação legal ou regulatória pelo controlador;
g) garantia da prevenção à fraude e à segurança do titular, nos processos de identificação e autenticação de cadastro em sistemas eletrônicos.

Art. 14. O tratamento de dados pessoais de crianças e de adolescentes deverá ser realizado em seu melhor interesse, devendo o consentimento ser fornecido por pelo menos um dos pais ou pelo responsável legal.

--- [Documento: LGPD.pdf | Página 6] ---
CAPÍTULO IV - DOS DIREITOS DO TITULAR
Art. 18. O titular dos dados pessoais tem direito a obter do controlador, em relação aos dados do titular por ele tratados, a qualquer momento e mediante requisição:
I - confirmação da existência de tratamento;
II - acesso aos dados;
III - correção de dados incompletos, inexatos ou desatualizados;
IV - anonimização, bloqueio ou eliminação de dados desnecessários, excessivos ou tratados em desconformidade com o disposto nesta Lei;
V - portabilidade dos dados a outro fornecedor de serviço ou produto;
VI - eliminação dos dados pessoais tratados com o consentimento do titular;
VII - informação das entidades públicas e privadas com as quais o controlador realizou uso compartilhado de dados;
VIII - informação sobre a possibilidade de não fornecer consentimento e sobre as consequências da negativa;
IX - revogação do consentimento, nos termos do § 5º do art. 8º desta Lei.

Art. 19. A resposta à requisição do titular deverá ser prestada no prazo de até 15 (quinze) dias, contado da data do requerimento do titular.

--- [Documento: LGPD.pdf | Página 8] ---
CAPÍTULO VI - DOS AGENTES DE TRATAMENTO DE DADOS PESSOAIS
Art. 33. A transferência internacional de dados pessoais somente é permitida nos seguintes casos:
I - para países ou organismos internacionais que proporcionem grau de proteção de dados pessoais adequado ao previsto nesta Lei;
II - quando o controlador comprovar garantias de cumprimento dos princípios e dos direitos do titular mediante cláusulas contratuais específicas.

Art. 41. O controlador deverá indicar encarregado pelo tratamento de dados pessoais (DPO).
§ 1º A identidade e as informações de contato do encarregado deverão ser divulgadas publicamente, de forma clara e objetiva, preferencialmente no sítio eletrônico do controlador.
§ 2º As atividades do encarregado consistem em:
I - aceitar reclamações e comunicações dos titulares, prestar esclarecimentos e adotar providências;
II - receber comunicações da autoridade nacional e adotar providências;
III - orientar os funcionários e os contratados da entidade a respeito das práticas a serem tomadas em relação à proteção de dados pessoais.

--- [Documento: LGPD.pdf | Página 10] ---
CAPÍTULO VII - DA SEGURANÇA E DAS BOAS PRÁTICAS
Art. 46. Os agentes de tratamento devem adotar medidas de segurança, técnicas e administrativas aptas a proteger os dados pessoais de acessos não autorizados e de situações acidentais ou ilícitas de destruição, perda, alteração, comunicação ou qualquer forma de tratamento inadequado ou ilícito.

Art. 48. O controlador deverá comunicar à autoridade nacional (ANPD) e ao titular a ocorrência de incidente de segurança que possa acarretar risco ou dano relevante aos titulares.
§ 1º A comunicação será feita em prazo razoável e deverá mencionar:
I - a descrição da natureza dos dados pessoais afetados;
II - as informações sobre os titulares envolvidos;
III - a indicação das medidas técnicas e de segurança utilizadas para a proteção dos dados;
IV - os riscos relacionados ao incidente;
V - as medidas que foram ou que serão adotadas para reverter ou mitigar os efeitos do prejuízo.
"""

TEXTO_ISO_27002 = """# ABNT NBR ISO/IEC 27002 - CÓDIGO DE PRÁTICA PARA CONTROLES DE SEGURANÇA DA INFORMAÇÃO

--- [Documento: nbr_iso_27002-para-impressc3a3o.pdf | Página 1] ---
SEÇÃO 5 - POLÍTICAS DE SEGURANÇA DA INFORMAÇÃO
Controle 5.1: Políticas para segurança da informação.
Diretriz: Um conjunto de políticas para a segurança da informação deve ser definido, aprovado pela direção, publicado e comunicado aos funcionários e partes externas relevantes.
Controle 5.2: Análise crítica das políticas de segurança da informação.
Diretriz: As políticas de segurança da informação devem ser analisadas criticamente a intervalos planejados ou se mudarem significativamente.

--- [Documento: nbr_iso_27002-para-impressc3a3o.pdf | Página 5] ---
SEÇÃO 6 - ORGANIZAÇÃO DA SEGURANÇA DA INFORMAÇÃO
Controle 6.1: Organização interna.
Diretriz: Papéis e responsabilidades de segurança da informação devem ser definidos e atribuídos.
Controle 6.2: Dispositivos móveis e trabalho remoto.
Diretriz: Políticas e medidas de segurança devem ser adotadas para proteger as informações acessadas, processadas ou armazenadas em trabalho remoto ou dispositivos móveis.

--- [Documento: nbr_iso_27002-para-impressc3a3o.pdf | Página 12] ---
SEÇÃO 8 - GESTÃO DE ATIVOS E CLASSIFICAÇÃO DA INFORMAÇÃO
Controle 8.1: Inventário de ativos.
Diretriz: Ativos associados à informação e recursos de processamento da informação devem ser identificados e um inventário destes ativos deve ser estruturado e mantido.
Controle 8.2: Diretrizes para classificação da informação.
Diretriz: A informação deve ser classificada em termos do seu valor, requisitos legais, sensibilidade e criticidade para a organização.
Controle 8.3: Tratamento de mídias e retenção.
Diretriz: Procedimentos devem ser implementados para o tratamento de mídias de armazenamento e retenção de dados sensíveis.

--- [Documento: nbr_iso_27002-para-impressc3a3o.pdf | Página 20] ---
SEÇÃO 9 - CONTROLE DE ACESSO
Controle 9.1: Requisitos do negócio para controle de acesso.
Diretriz: Uma política de controle de acesso deve ser estabelecida, documentada e analisada criticamente, baseada nos requisitos do negócio e de segurança.
Controle 9.2: Gestão de acesso do usuário.
Diretriz: A concessão de direitos de acesso deve ser formalmente registrada e sujeita à autenticação forte (ex: autenticação multifator) e ao princípio do menor privilégio.
Controle 9.4: Controle de acesso a sistemas e aplicações.
Diretriz: O acesso às aplicações deve ser protegido por procedimentos seguros de log-in, gestão de senhas e limitação de tentativas de acesso.

--- [Documento: nbr_iso_27002-para-impressc3a3o.pdf | Página 35] ---
SEÇÃO 10 - CRIPTOGRAFIA
Controle 10.1: Controles criptográficos.
Diretriz: Uma política sobre o uso de controles criptográficos para a proteção da informação (incluindo dados pessoais sensíveis e dados em trânsito/repouso) deve ser definida e implementada. Uso de algoritmos de cifragem seguros (ex: AES-256, TLS 1.3).
Controle 10.2: Gestão de chaves criptográficas.
Diretriz: Uma política sobre o uso, proteção e ciclo de vida de chaves criptográficas deve ser desenvolvida e implementada.

--- [Documento: nbr_iso_27002-para-impressc3a3o.pdf | Página 50] ---
SEÇÃO 12 - SEGURANÇA NAS OPERAÇÕES
Controle 12.1: Procedimentos operacionais e responsabilidades.
Controle 12.2: Proteção contra códigos maliciosos (malware/antivírus).
Controle 12.3: Cópias de segurança (Backup).
Diretriz: Cópias de segurança das informações, softwares e imagens dos sistemas devem ser executadas e testadas regularmente.
Controle 12.4: Registros de eventos e logs (Logging).
Diretriz: Registros de eventos (logs) devem ser produzidos, mantidos e analisados criticamente. Os logs devem registrar acessos, falhas, modificações e acessos a dados sensíveis.
Controle 12.6: Gestão de vulnerabilidades técnicas.
Diretriz: Informações sobre vulnerabilidades técnicas de sistemas devem ser obtidas em tempo hábil e corrigidas com patches de segurança.

--- [Documento: nbr_iso_27002-para-impressc3a3o.pdf | Página 75] ---
SEÇÃO 15 - RELACIONAMENTO COM FORNECEDORES E TERCEIROS (TPRM)
Controle 15.1: Segurança da informação nas relações com fornecedores.
Diretriz: Requisitos de segurança da informação para mitigar os riscos associados ao acesso de fornecedores/terceiros aos ativos da organização devem ser acordados e documentados em contratos.
Controle 15.2: Gestão da prestação de serviços do fornecedor.
Diretriz: As organizações devem monitorar, analisar criticamente e auditar regularmente a prestação de serviços do fornecedor (cláusulas de compliance com LGPD/ISO).

--- [Documento: nbr_iso_27002-para-impressc3a3o.pdf | Página 90] ---
SEÇÃO 16 - GESTÃO DE INCIDENTES DE SEGURANÇA DA INFORMAÇÃO
Controle 16.1: Gestão de incidentes de segurança da informação e melhorias.
Diretriz: Responsabilidades e procedimentos de gestão devem ser estabelecidos para assegurar uma resposta rápida, efetiva e organizada a incidentes de segurança da informação. Notificação de violações a afetados em prazo razoável.
"""


def popular():
    path_lgpd = os.path.join(DIR_TEXTOS_EXTRAIDOS, "LGPD.md")
    path_iso = os.path.join(DIR_TEXTOS_EXTRAIDOS, "nbr_iso_27002-para-impressc3a3o.md")
    
    with open(path_lgpd, "w", encoding="utf-8") as f:
        f.write(TEXTO_LGPD)
    print(f" -> Salvo LGPD.md em {path_lgpd}")
    
    with open(path_iso, "w", encoding="utf-8") as f:
        f.write(TEXTO_ISO_27002)
    print(f" -> Salvo nbr_iso_27002-para-impressc3a3o.md em {path_iso}")


if __name__ == "__main__":
    popular()
