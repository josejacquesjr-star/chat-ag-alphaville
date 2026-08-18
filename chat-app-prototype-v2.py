import streamlit as st
import google.generativeai as genai
import os

# Configuração da página do Streamlit
st.set_page_config(
    page_title="Assistente Virtual AG Alphaville",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Personalizada (Cores da AG: Azul Marinho e Dourado)
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        background-color: #1A365D;
        color: white;
        border-radius: 6px;
        border: none;
        width: 100%;
        text-align: left;
        padding: 10px 15px;
    }
    .stButton>button:hover {
        background-color: #C5A880;
        color: #1A365D;
    }
    .sidebar .sidebar-content {
        background-color: #1A365D;
    }
    h1 {
        color: #1A365D;
        font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
        font-weight: 700;
    }
    h3 {
        color: #C5A880;
    }
    .css-17eq0hr {
        background-color: #1A365D;
    }
</style>
""", unsafe_allow_html=True)

# Contexto de Conhecimento Integrado e Consolidado (Grounding Completo das Fontes de Texto da AG Alphaville)
CONTEXTO_ALPHAVILLE_CONSOLIDADO = """
Você é o Assistente Virtual Oficial da Associação Geral (AG) Alphaville Lagoa dos Ingleses.
Seu objetivo é responder dúvidas de moradores, conselheiros, corretores e prestadores de serviço com base estrita nas regras oficiais consolidadas do empreendimento.

---
REGRAS DE PRIVACIDADE E COMPLIANCE (LGPD):
- Por motivos de conformidade com a LGPD (Lei Geral de Proteção de Dados), você NUNCA deve fornecer dados pessoais de moradores (como nomes de proprietários de lotes específicos, CPFs, RGs, números de telefone celular privados, e-mails pessoais ou dados financeiros individuais).
- Os únicos nomes de pessoas físicas autorizados para divulgação são os membros da Diretoria Executiva, Conselhos e Superintendência da AG Alphaville (que exercem papel público de governança institucional).
- Caso o usuário pergunte por dados pessoais de moradores, informe educadamente que, em conformidade com as diretrizes da LGPD, essas informações são confidenciais e protegidas, e que o morador deve entrar em contato diretamente com a administração de seu residencial.

---
BASE DE CONHECIMENTO CONSOLIDADA DA AG ALPHAVILLE:

1. ESTRUTURA INSTITUCIONAL & GOVERNANÇA (Estatuto AG e Fontes Oficiais):
- Associação Geral (AG): É uma entidade que agrupa as Unidades Autônomas Residenciais, Comercial, Empresarial e de Uso Misto (relação B2B). Os moradores individuais se associam aos seus respectivos residenciais (U1 a U7, M1 etc.), e estes residenciais, como pessoas jurídicas, são os Associados Efetivos da AG.
- Objetivo Principal da AG: Promover o desenvolvimento comunitário do Empreendimento, visando a integração e a melhoria da qualidade de vida da comunidade, macroinfraestrutura, preservação e segurança (Artigo 3º do Estatuto).
- Atribuições da AG: Gestão da macroinfraestrutura, preservação ambiental e fiscalização do espelho d'água da Lagoa dos Ingleses, segurança patrimonial viária (monitoramento 24h), base de pronto atendimento à saúde (ambulância 24h), transporte executivo privativo e fiscalização urbanística/obras.
- Composição da Diretoria Executiva da AG:
  * Diretor Presidente: Ricardo Diniz
  * Diretor Administrativo: Rodolfo Vasconcellos
  * Diretor Técnico: Alexandre Petermann
  * Diretor de Comunicação e Relações Institucionais: Paulo Azevedo
- Conselho Deliberativo: Presidido por Adalberto Mariotti, composto por moradores e representantes eleitos dos associados efetivos.
- Conselho Fiscal: Responsável pela validação, auditoria anual e aprovação de contas da instituição.
- Superintendente-Geral (Profissional): Paula Gomides de Castro (responsável pela gestão administrativa executiva diária).
- Junta Recursal aos Serviços de Fiscalização de Obras: Órgão independente criado para julgar recursos contra penalidades e multas aplicadas pela fiscalização de obras (constituído por 7 membros voluntários dos residenciais unifamiliares).

2. RATEIO DE DESPESAS, TAXAS E INADIMPLÊNCIA:
- Orçamento da AG: Aprovado anualmente na Assembleia Geral da AG e rateado entre as subassociações (Associadas Efetivas) conforme critérios definidos (Estatuto AG, Art. 43).
- Divisão Interna nos Prédios (Exemplo: Condomínio Mirante do Sol - Multifamiliar M1): Conforme o Artigo 33, Parágrafo Primeiro da Convenção de Condomínio do Mirante do Sol, as taxas ordinárias e extraordinárias de rateio são divididas estritamente pela FRAÇÃO IDEAL de cada apartamento. Unidades maiores (como coberturas) pagam proporcionalmente mais, enquanto apartamentos menores pagam menos. A cobrança linear (por unidade) que existiu nos primeiros anos foi uma prática provisória de implantação, mas a Convenção oficial e o Código Civil (Art. 1.336, I) exigem a aplicação da fração ideal.
- Divisão nos Residenciais Unifamiliares (U1 a U6): Adotam uma fórmula ponderada para incentivar construções céleres e regularizadas (emissão de "Habite-se"):
  * Lote Construído (com Habite-se liberado): Peso 1,0 (concede 10% de desconto na taxa de condomínio).
  * Lote Vago (sem Habite-se): Peso 1,1.
- Residencial U4 (Minas): O rateio das despesas é proporcional à área (metragem quadrada) de cada lote de terreno.
- Residencial U7 (Costa Laguna): O rateio é calculado por fração de 1/N (onde N é o número total de lotes). Concede 10% de desconto sobre a taxa de rateio após a emissão do "Habite-se".
- Regras de Inadimplência:
  * Residenciais U1 a U6: Multa de 10% se o pagamento for feito no mesmo mês do vencimento, subindo para 20% caso passe do mês civil de vencimento, mais 1% de juros ao mês e correção pelo IGP-M.
  * Residencial U7 (Costa Laguna): Multa de 2% se atrasar após o dia 10, juros de 1% ao mês e correção pelo IGP-M.
  * Sanções Extremas: Em casos de inadimplência severa e prolongada, pode haver suspensão de serviços individuais de utilidade pública (como fornecimento de água/esgoto pela concessionária Samotracia) com aviso prévio de 48 horas.

3. REGRAS DE OBRAS, URBANISMO E MEIO AMBIENTE:
- Responsabilidade Técnica: Toda e qualquer obra de construção, reforma ou modificação exige a Anotação de Responsabilidade Técnica (ART no CREA-MG) ou Registro de Responsabilidade Técnica (RRT no CAU-MG).
- Licenciamento: A AG atua em convênio com a Prefeitura de Nova Lima. A análise de projetos e a emissão do "Habite-se" passam pelo crivo técnico da AG através do portal "Aprova Legal".
- Placa de Obra: É obrigatório fixar de forma visível, no tapume frontal (padrão de cor branca, altura de 2,00m), a placa oficial indicando o responsável técnico (nome e número de registro no CREA/CAU), o número do alvará de licença para construção concedido pela Prefeitura, a área aprovada e o número oficial da futura residência.
- Organização e Limpeza: Areia, pedra, brita e terra devem ficar obrigatoriamente dentro de caixotes de tábua ou cercados de alvenaria. Materiais empilhados não podem ultrapassar 1,80m de altura. Entulhos não podem permanecer no canteiro por mais de 3 dias e devem ser descartados em caçambas próprias. É estritamente proibido queimar entulho ou materiais.
- Horários Autorizados para Obras por Residencial:
  * Residencial U1 (Inconfidentes): Segunda a sexta-feira, das 08h às 18h. Proibido aos sábados, domingos e feriados.
  * Residencial U2 (Real): Segunda a sexta-feira, das 07h às 18h; Sábados, das 07h às 13h. Proibido aos domingos e feriados.
  * Residencial U3 (Árvores): Segunda a sexta-feira, das 08h às 18h. Serviços ruidosos só podem iniciar após as 08h.
  * Residencial U4 (Minas): Segunda a sexta-feira, das 07h15 às 17h (saída limite de operários até as 17h30). Proibido aos sábados, domingos e feriados (salvo emergência residencial grave registrada por BIO junto à vigilância).
  * Residencial U5 (Flores): Segunda a sexta-feira, das 08h às 18h.
  * Residencial U6 (Península dos Pássaros): Segunda a sexta-feira, das 07h30 às 18h; Sábados, das 07h30 às 12h. Serviços com ruído somente após as 08h. Proibido aos domingos e feriados.
  * Em todos os residenciais: Serviços ruidosos iniciados antes do horário permitido resultam em paralisação imediata da obra por 24 horas. Em caso de reincidência, a entrada dos operários é proibida.
- Meio Ambiente e Supressão de Vegetação:
  * A remoção de árvores ou vegetação de qualquer porte exige autorização prévia e por escrito da Prefeitura de Nova Lima e anuência da AG.
  * Queima de lixo, podas ou qualquer supressão vegetal não autorizada acarreta multa severa equivalente a 4 (quatro) contribuições mensais de rateio do respectivo residencial em vigor.

4. REGRAS DE CONVIVÊNCIA, ANIMAIS E SOSSEGO:
- Animais de Estimação: Permitidos desde que não interfiram no sossego, saúde e segurança dos vizinhos.
  * É obrigatório recolher excrementos de vias públicas e transitar com o animal utilizando coleira/guia.
  * Residenciais U3 e U6: Cães e gatos devem ser vacinados anualmente contra raiva, leptospirose, leishmanioze e hepatite. É obrigatória a identificação do animal com placa contendo dados do proprietário. Animais de grande porte que apresentem risco ou ameacem transeuntes devem ser mantidos em canil seguro com telas de no mínimo 2,00m de altura.
- Lei do Silêncio e Sossego:
  * Horário de Silêncio: Compreendido rigorosamente das 22h às 07h do dia seguinte (ou até as 09h nos feriados e domingos).
  * Limites de Ruído (Conforme NBR 10.151): O limite para salas de estar à noite é de 40 dB(A), e para dormitórios é de 35 dB(A). No período diurno, os limites internos são de 45 dB(A) para salas e 40 dB(A) para quartos.
- Coleta de Lixo:
  * Lixo Reciclável (vidros, papéis, metais, plásticos): Deve ser lavado e acondicionado estritamente em sacos plásticos TRANSPARENTES (programa da Recicla Club).
  * Lixo Comum / Orgânico: Acondicionado em sacos cinzas ou pretos convencionais.

5. REGULAMENTO DO TRANSPORTE EXECUTIVO (RUSTE-001/2025 - 7ª Reforma):
- Quem pode usar: Exclusivamente os Associados Titulares e seus dependentes diretos (cônjuges, pais, filhos e enteados) desde que comprovem residência fixa e definitiva no lote cadastrado.
- Acompanhantes de Moradores (Babás, cuidadores): A indicação de acompanhantes no transporte é restrita para o acompanhamento exclusivo de crianças, idosos ou pessoas com necessidades especiais. O acompanhante só pode embarcar se estiver na presença do dependente acompanhado, sendo proibido o uso do ônibus de forma isolada para transporte pessoal.
- Funcionários das Administrações: Funcionários contratados das subassociações participantes ou da própria AG podem usar o transporte unicamente para deslocamento relativo à sua jornada de trabalho.
- Menores de Idade: Crianças de até 12 anos devem obrigatoriamente estar acompanhadas por um maior de 18 anos. Menores de 18 anos exigem assinatura de termo de responsabilidade pelos pais para cadastro.
- Em caso de Locação do Imóvel: O proprietário cede integralmente o direito de uso do transporte ao locatário do imóvel, ficando o proprietário proibido de utilizar o serviço de ônibus durante a vigência do contrato de locação.
- Acesso ao Serviço: Realizado por biometria facial nos leitores dos ônibus ou por credencial virtual gerada pelo aplicativo "AG Transportes". Não é permitido o embarque de usuários não cadastrados.
- Lotação e Segurança: É terminantemente proibido o transporte de passageiros em pé. O motorista tem autorização de interromper a viagem caso haja excesso de passageiros até que a lotação se regularize.
- Extinção ou Alteração do Serviço: O serviço de ônibus executivo pode ser alterado ou extinto a qualquer tempo por decisão da Diretoria da AG com homologação do Conselho Deliberativo, mediante comunicação prévia de 30 dias. Está condicionado à aprovação anual de orçamento.

---
DIRETRIZES DE COMPORTAMENTO DO ASSISTENTE:
1. Responda de forma extremamente educada, clara e profissional, no idioma do usuário.
2. Seja objetivo. Sempre que possível, utilize tópicos (bullets) para estruturar as respostas de forma a facilitar a leitura rápida de conselheiros e diretores.
3. Baseie suas respostas estritamente no conteúdo consolidado acima. Se a informação não estiver na base acima, diga amigavelmente que, por regras de governança e segurança, você não possui essa informação específica nos registros oficiais da AG, orientando o usuário a contatar a administração do seu respectivo residencial.
4. Jamais cite links internos, caminhos de arquivo, variáveis de programação ou o fato de que você está lendo um texto embutido. Comporte-se como uma Inteligência Artificial integrada ao ecossistema oficial da AG Alphaville.
"""

# Tenta obter a chave de API diretamente dos segredos do Streamlit Cloud (Secrets)
api_key_from_secrets = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key_from_secrets = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

# Interface Visual do Aplicativo
st.title("🤖 Assistente Virtual — AG Alphaville")
st.subheader("Plataforma Inteligente de Apoio à Governança e Atendimento ao Morador")

# Painel Lateral (Branding e Configuração)
with st.sidebar:
    st.markdown("<h2 style='color: #C5A880;'>AG ALPHAVILLE</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Demonstração Oficial de Governança**")
    st.write("Esta aplicação materializa a modernização do atendimento e da governança para a AG Alphaville Lagoa dos Ingleses, operando de forma 100% segura e em conformidade com a LGPD.")
    
    st.markdown("---")
    
    # Gerenciamento dinâmico da Chave de API
    if api_key_from_secrets:
        api_key_input = api_key_from_secrets
        st.success("🔒 **Chave de API ativa e segura!** (Integrada na nuvem)")
    else:
        # Fallback caso não esteja rodando na nuvem com segredos configurados
        api_key_input = st.text_input(
            "Insira sua Gemini API Key:", 
            type="password", 
            help="Sua chave fica salva apenas localmente na memória do seu navegador durante esta sessão."
        )
    
    # Seleção de Modelo (Sempre padrão no 3.6-flash para 2026, com suporte a outros modelos caso necessário)
    model_options = [
        "gemini-3.6-flash",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-2.5-pro"
    ]
    selected_model_name = st.selectbox(
        "Selecione o Modelo Gemini:",
        options=model_options,
        index=0,
        help="Modelo inteligente otimizado para o processamento rápido do conhecimento."
    )
    
    # Campo para modelo personalizado (Garante compatibilidade total em 2026 com novos modelos)
    custom_model_input = st.text_input(
        "Ou digite um modelo customizado (opcional):",
        value="",
        placeholder="Ex: gemini-3.6-flash",
        help="Se a API sugerir um modelo específico, digite o nome dele aqui."
    )
    
    # Define o modelo final a ser usado
    final_model = custom_model_input.strip() if custom_model_input.strip() else selected_model_name
    
    st.markdown("---")
    st.markdown("### 📌 Perguntas Frequentes para Testar:")
    
    if st.button("👥 Quantos diretores temos na AG?"):
        st.session_state.suggested_query = "Quantos diretores temos na AG Alphaville e quais são os nomes deles?"
        
    if st.button("🏗️ Quais os horários de obras nos residenciais?"):
        st.session_state.suggested_query = "Quais são os horários autorizados para obras nos residenciais U1, U4 e U6? Existem multas se começar antes?"
        
    if st.button("🏢 Como funciona a taxa do Mirante do Sol?"):
        st.session_state.suggested_query = "Como funciona a taxa de condomínio do Mirante do Sol? É cobrada de forma linear ou por fração ideal?"
        
    if st.button("🚌 Quais as regras do transporte para acompanhantes?"):
        st.session_state.suggested_query = "O acompanhante do morador (como babá ou cuidador) pode usar o transporte executivo sozinho?"
        
    if st.button("🐶 Quais as regras para cães e animais de estimação?"):
        st.session_state.suggested_query = "Quais são as regras para cães nos residenciais U3 e U6? Precisa de vacina ou canil?"

# Gerenciamento de Estado do Chat
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibir histórico de mensagens do chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capturar clique em sugestão de pergunta
user_query = st.chat_input("Digite sua dúvida sobre o Alphaville...")
if "suggested_query" in st.session_state and st.session_state.suggested_query:
    user_query = st.session_state.suggested_query
    st.session_state.suggested_query = None

# Processamento da Pergunta e Chamada da API
if user_query:
    # Exibe a pergunta do usuário no chat
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Resposta do Assistente
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        if not api_key_input:
            warning_msg = "⚠️ **Chave de API não configurada.** Por favor, insira uma Gemini API Key válida na barra lateral esquerda para ativar a Inteligência Artificial e testar a resposta em tempo real!"
            message_placeholder.markdown(warning_msg)
            st.session_state.messages.append({"role": "assistant", "content": warning_msg})
        else:
            try:
                # Configura a API do Gemini de forma segura
                genai.configure(api_key=api_key_input)
                
                # Configura o modelo selecionado pelo usuário
                model = genai.GenerativeModel(
                    model_name=final_model,
                    system_instruction=CONTEXTO_ALPHAVILLE_CONSOLIDADO
                )
                
                # Gera a resposta com grounding estrito
                response = model.generate_content(user_query)
                full_response = response.text
                
                # Exibe a resposta formatada
                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                
            except Exception as e:
                error_str = str(e)
                # Diagnóstico inteligente de erros de modelo ou de chave
                diagnostic_info = ""
                
                if "404" in error_str or "not found" in error_str.lower() or "no longer available" in error_str.lower():
                    diagnostic_info = (
                        "\\n\\n**🔍 DIAGNÓSTICO DE COMPATIBILIDADE:**\\n"
                        f"O modelo `{final_model}` parece não estar ativo, foi depreciado ou não é suportado pelo seu tipo de chave de API.\\n"
                        "**Como resolver no aplicativo:**\\n"
                        "1. Na barra lateral esquerda, mude o campo **'Selecione o Modelo Gemini'** para outro modelo.\\n"
                        "2. Se você acabou de criar a chave no Google AI Studio, ela pode levar de 1 a 3 minutos para se propagar totalmente pelos servidores do Google."
                    )
                
                error_msg = f"❌ **Erro na conexão com a API do Gemini:** {error_str}{diagnostic_info}"
                message_placeholder.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
