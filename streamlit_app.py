import streamlit as st
import pandas as pd
import os

# Configuração da página
st.set_page_config(page_title="Ian & Iara Finanças", layout="centered")

# --- 1. REMOVER O CLARÃO (CSS Customizado) ---
st.markdown("""
    <style>
    /* Remove o fundo branco dos cards de métricas */
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
    }
    /* Ajusta a cor do texto para não sumir */
    div[data-testid="stMetricLabel"] p {
        color: #e0e0e0 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES PARA SALVAR E CARREGAR DADOS ---
DB_FILE = "dados_financas.csv"

def carregar_dados():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        # Recupera salários e lista de contas
        sal_ian = df['sal_ian'].iloc[0]
        sal_iara = df['sal_iara'].iloc[0]
        contas = df[['Descrição', 'Valor']].dropna().to_dict('records')
        return sal_ian, sal_iara, contas
    return 1894.34, 1894.34, []

def salvar_dados(s_ian, s_iara, lista_contas):
    if not lista_contas:
        df = pd.DataFrame([{'sal_ian': s_ian, 'sal_iara': s_iara, 'Descrição': None, 'Valor': None}])
    else:
        df = pd.DataFrame(lista_contas)
        df['sal_ian'] = s_ian
        df['sal_iara'] = s_iara
    df.to_csv(DB_FILE, index=False)

# Carregar dados iniciais
s_ian_init, s_iara_init, contas_init = carregar_dados()

if 'contas' not in st.session_state:
    st.session_state.contas = contas_init

# --- 3. INTERFACE ---
st.title("☀️ Ian & Iara Finanças")

# Sidebar para salários
st.sidebar.header("⚙️ Ajustar Rendas")
sal_ian = st.sidebar.number_input("Renda Ian", value=float(s_ian_init), step=100.0)
sal_iara = st.sidebar.number_input("Renda Iara", value=float(s_iara_init), step=100.0)
renda_total = sal_ian + sal_iara

# Salva automaticamente se mudar o salário
if sal_ian != s_ian_init or sal_iara != s_iara_init:
    salvar_dados(sal_ian, sal_iara, st.session_state.contas)

st.subheader("💸 Novo Gasto")
with st.container():
    col_n, col_v, col_b = st.columns([2, 1, 1])
    nome = col_n.text_input("O que é?", placeholder="Ex: Internet")
    valor = col_v.number_input("Valor R$", min_value=0.0, step=10.0)
    
    if col_b.button("✅ Adicionar", use_container_width=True):
        if nome and valor > 0:
            st.session_state.contas.append({'Descrição': nome, 'Valor': valor})
            salvar_dados(sal_ian, sal_iara, st.session_state.contas)
            st.rerun()

st.divider()

# --- 4. CÁLCULOS ---
gasto_total = sum(item['Valor'] for item in st.session_state.contas)
sobra_total = renda_total - gasto_total
divisao = sobra_total / 2 if sobra_total > 0 else 0

# --- 5. DASHBOARD SEM CLARÃO ---
c1, c2 = st.columns(2)
c1.metric("💰 RENDA TOTAL", f"R$ {renda_total:,.2f}")
c2.metric("📉 TOTAL GASTOS", f"R$ {gasto_total:,.2f}", delta=f"-{gasto_total:,.2f}", delta_color="inverse")

st.markdown("---")
st.subheader("🎯 Destino da Sobra")

d1, d2 = st.columns(2)
with d1:
    st.success(f"**💜 INVESTIR (50%)**\n\n R$ {divisao:,.2f}")
with d2:
    st.info(f"**🛍️ GASTAR (50%)**\n\n R$ {divisao:,.2f}")

# --- 6. TABELA E CONTROLE ---
st.divider()
if st.session_state.contas:
    st.write("### 📝 Contas do Mês")
    df_exibir = pd.DataFrame(st.session_state.contas)
    st.table(df_exibir)
    
    if st.button("🗑️ Resetar para Novo Mês"):
        st.session_state.contas = []
        salvar_dados(sal_ian, sal_iara, [])
        st.rerun()
