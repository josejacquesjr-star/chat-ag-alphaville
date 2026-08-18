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
    }
    h3 {
        color: #C5A880;
    }
    .css-17eq0hr {
        background-color: #1A365D;
    }
</style>
""", unsafe_allow_html=True)

# Contexto de Conhecimento Integrado (Grounding das Fontes Oficiais da AG Alphaville)
CONTEXTO_ALPHAVILLE = """
Você é o Assistente Virtual Oficial da Associação Geral (AG) Alphaville Lagoa dos Ingleses.
Seu objetivo é responder dúvidas de moradores, conselheiros, corretores e prestadores de serviço com base estrita nas regras oficiais.
Abaixo está o resumo consolidado das fontes oficiais da AG para grounding de suas respostas:

1. SOBRE A ASSOCIAÇÃO GERAL (AG):
- Objetivo Principal: Promover o desenvolvimento comunitário do Empreendimento, visando a integração e a melhoria da qualidade de vida da comunidade (Artigo 3º, VI do Estatuto).
- Atribuições: Macroinfraestrutura, preservação da Lagoa dos Ingleses, segurança patrimonial viária (monitoramento 24h), base de saúde/ambulância 24h, transporte executivo privativo e fiscalização de obras/urbanismo.
- Associados Efetivos: São as subassociações (Residenciais U1 a U7, Multifamiliares M1, Comerciais ACUM, ACC e Empresariais AEUM). Os moradores individuais se associam às subassociações, que por sua vez são as associadas da AG (relação B2B).

2. RATEIO DE DESPESAS (MACRO E MICRO):
- Orçamento da AG: Aprovado anualmente na Assembleia Geral da AG e rateado entre as subassociações (Associadas Efetivas) conforme critérios definidos em assembleia (Estatuto AG, Art. 43).
- Transporte Executivo: O custo é rateado apenas entre as Associadas Efetivas (Residenciais) que aderirem formalmente ao serviço.
- Repasse interno nos prédios (Exemplo Mirante do Sol - Multifamiliar M1): Conforme o Artigo 33, Parágrafo Primeiro da Convenção de Condomínio do Mirante do Sol, as taxas e repasses são divididos estritamente pela FRAÇÃO IDEAL de cada apartamento (coberturas pagam proporcionalmente mais, apartamentos menores pagam menos). A cobrança linear (por apartamento) que existiu nos primeiros anos foi uma prática provisória de implantação, mas a Convenção e o Código Civil (Art. 1.336, I) exigem a fração ideal.
- Repasse nos Residenciais Unifamiliares (U1 a U6): Usam uma fórmula ponderada para incentivar a construção (com "Habite-se"):
  * Peso do Lote Construído (com Habite-se) = 1,0
  * Peso do Lote Vago (sem Habite-se) = 1,1
  * Isso dá aos lotes construídos um desconto de 10% na taxa de condomínio em relação ao lote vago.
- Residencial U4 (Minas): Rateio proporcional à área (metragem) do lote.
- Residencial U7 (Costa Laguna): Rateio por fração de 1/N (onde N é o número total de lotes). Concede 10% de desconto após a emissão do "Habite-se".
- Inadimplência: Multa de 10% se pago no mês de vencimento (U1 a U6), subindo para 20% após o mês civil de vencimento, mais 1% de juros ao mês e IGP-M. No U7 (Costa Laguna), multa de 2% se atrasar após o dia 10, juros de 1% e IGP-M. Em casos extremos, pode haver cessação de serviços individuais (como fornecimento de água/esgoto pela Samotracia) com aviso prévio de 48h.

3. REGRAS DE OBRAS, URBANISMO E MEIO AMBIENTE:
- Responsabilidade Técnica: Toda obra exige a Anotação de Responsabilidade Técnica (ART no CREA-MG) ou Registro de Responsabilidade Técnica (RRT no CAU-MG).
- Placa de Obra: É obrigatório fixar a placa oficial de identificação no tapume (padrão branco) contendo o nome e o registro profissional (CREA/CAU) do responsável técnico.
- Junta Recursal: Órgão independente da AG criado para julgar, em grau de recurso, as penalidades e multas aplicadas pela fiscalização de obras (Normativo da Junta Recursal).
- Concessionárias parceiras: Samotracia (água e esgoto), Cemig (energia elétrica), Gásmig (gás subterrâneo).
- Drones: O uso de Drones (RPA) no complexo e na Lagoa exige registro na ANAC, homologação de rádio na ANATEL e autorização do espaço aéreo no DECEA.

DIRETRIZES DE COMPORTAMENTO:
- Seja sempre extremamente educado, cordial e profissional.
- Se a pergunta do usuário não puder ser respondida com base nas informações acima, informe educadamente que, por questões de segurança e compliance, você só responde com dados estritamente validados pelas fontes oficiais da AG, e sugira que o morador procure a administração de seu residencial ou o síndico para detalhes específicos.
- Nunca invente regras, valores ou dados que não estejam neste contexto.
"""

# Interface Visual do Aplicativo
st.title("🤖 Assistente Virtual — AG Alphaville")
st.subheader("Plataforma Inteligente de Apoio à Governança e Atendimento ao Morador")

# Painel Lateral (Branding e Configuração)
with st.sidebar:
    st.markdown("<h2 style='color: #C5A880;'>AG ALPHAVILLE</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Demonstração Segura de Tecnologia**")
    st.write("Esta aplicação foi desenhada para materializar o atendimento virtual inteligente para a Diretoria Executiva de forma rápida, local e 100% segura.")
    
    st.markdown("---")
    # Entrada de Chave de API de forma segura
    api_key_input = st.text_input("Insira sua Gemini API Key:", type="password", help="Sua chave fica salva apenas localmente na memória do seu navegador durante esta sessão.")
    
    # Seleção de Modelo para evitar erros 404 de compatibilidade
    model_options = [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-3.6-flash",
        "gemini-2.5-pro"
    ]
    selected_model_name = st.selectbox(
        "Selecione o Modelo Gemini:",
        options=model_options,
        index=0,
        help="Caso o modelo padrão dê erro, mude para outro compatível com sua chave."
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
    st.markdown("### 📌 Sugestões de Perguntas para Testar:")
    if st.button("Como funciona o rateio de despesas?"):
        st.session_state.suggested_query = "Como funciona o rateio de despesas?"
    if st.button("Por que a taxa do Mirante do Sol mudou?"):
        st.session_state.suggested_query = "Por que a taxa do Mirante do Sol mudou?"
    if st.button("Quais são as regras para iniciar uma obra?"):
        st.session_state.suggested_query = "Quais são as regras para iniciar uma obra?"
    if st.button("Qual o objetivo principal da AG?"):
        st.session_state.suggested_query = "Qual o objetivo principal da AG?"

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
                    system_instruction=CONTEXTO_ALPHAVILLE
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
                        "\n\n**🔍 DIAGNÓSTICO DE COMPATIBILIDADE:**\n"
                        f"O modelo `{final_model}` parece não estar ativo, foi depreciado ou não é suportado pelo seu tipo de chave de API.\n"
                        "**Como resolver no aplicativo:**\n"
                        "1. Na barra lateral esquerda, selecione o modelo **`gemini-1.5-pro`** (que possui alta estabilidade).\n"
                        "2. Se a mensagem de erro sugerir um modelo mais novo (como o `gemini-3.6-flash`), digite-o no campo **'Ou digite um modelo customizado'** na barra lateral.\n"
                        "3. Se você acabou de criar a chave no Google AI Studio, ela pode levar de 1 a 3 minutos para se propagar totalmente pelos servidores do Google."
                    )
                    
                    # Tentar listar os modelos disponíveis reais da chave para ajudar o usuário
                    try:
                        available_models = []
                        for m in genai.list_models():
                            if 'generateContent' in m.supported_generation_methods:
                                available_models.append(m.name.replace("models/", ""))
                        if available_models:
                            diagnostic_info += f"\n\n**Modelos suportados por sua chave atualmente:**\n" + ", ".join([f"`{name}`" for name in available_models])
                    except Exception:
                        pass
                
                error_msg = f"❌ **Erro na conexão com a API do Gemini:** {error_str}{diagnostic_info}"
                message_placeholder.markdown(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
