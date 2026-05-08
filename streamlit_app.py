import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Ian & Iara Finanças", layout="centered")

# --- 1. CSS PARA REMOVER O CLARÃO E MELHORAR O VISUAL ---
st.markdown("""
    <style>
    div[data-testid="stMetric"] {
        background-color: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 15px;
        border-radius: 10px;
    }
    div[data-testid="stMetricValue"] { font-size: 24px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. PERSISTÊNCIA DE DADOS ---
DB_FILE = "dados_financas.csv"

def carregar_dados():
    if os.path.exists(DB_FILE):
        df = pd.read_csv(DB_FILE)
        s_ian = df['sal_ian'].iloc[0]
        s_iara = df['sal_iara'].iloc[0]
        # Filtrar apenas as linhas que possuem descrição de conta
        contas = df[['Descrição', 'Valor']].dropna().to_dict('records')
        return s_ian, s_iara, contas
    return 1894.34, 1894.34, []

def salvar_dados(s_ian, s_iara, lista_contas):
    if not lista_contas:
        df = pd.DataFrame([{'sal_ian': s_ian, 'sal_iara': s_iara, 'Descrição': None, 'Valor': None}])
    else:
        df = pd.DataFrame(lista_contas)
        df['sal_ian'] = s_ian
        df['sal_iara'] = s_iara
    df.to_csv(DB_FILE, index=False)

s_ian_init, s_iara_init, contas_init = carregar_dados()

if 'contas' not in st.session_state:
    st.session_state.contas = contas_init

# --- 3. ENTRADAS (SIDEBAR) ---
st.sidebar.header("⚙️ Configurações")
sal_ian = st.sidebar.number_input("Renda Ian", value=float(s_ian_init), step=100.0)
sal_iara = st.sidebar.number_input("Renda Iara", value=float(s_iara_init), step=100.0)
renda_total = sal_ian + sal_iara

# --- 4. LANÇAMENTOS ---
st.title("☀️ Ian & Iara Finanças")
st.subheader("💸 Lançar Gasto")

with st.container():
    c_n, c_v, c_b = st.columns([2, 1, 1])
    nome = c_n.text_input("Descrição", placeholder="Ex: Aluguel")
    valor = c_v.number_input("Valor R$", min_value=0.0)
    if c_b.button("✅ Lançar", use_container_width=True):
        if nome and valor > 0:
            st.session_state.contas.append({'Descrição': nome, 'Valor': valor})
            salvar_dados(sal_ian, sal_iara, st.session_state.contas)
            st.rerun()

st.divider()

# --- 5. CÁLCULOS DO BALANÇO ---
total_gastos = sum(item['Valor'] for item in st.session_state.contas)
saldo_restante = renda_total - total_gastos # Valor que sobra após as contas
divisao = saldo_restante / 2 if saldo_restante > 0 else 0

# --- 6. DASHBOARD ---
# Primeira linha: O que entra e o que sai
col1, col2 = st.columns(2)
col1.metric("💰 RENDA BRUTA", f"R$ {renda_total:,.2f}")
col2.metric("📉 TOTAL DE CONTAS", f"R$ {total_gastos:,.2f}", delta=f"-{total_gastos:,.2f}", delta_color="inverse")

# Segunda linha: O impacto real no bolso
st.metric("🔓 SALDO DISPONÍVEL (Pós-Contas)", f"R$ {saldo_restante:,.2f}")

st.markdown("---")
st.subheader("🎯 Planejamento do Saldo")

d1, d2 = st.columns(2)
with d1:
    st.success(f"**💜 INVESTIMENTO (50%)**\n\n R$ {divisao:,.2f}")
with d2:
    st.info(f"**🛍️ GASTO LIVRE (50%)**\n\n R$ {divisao:,.2f}")

# --- 7. HISTÓRICO E EXPORTAÇÃO ---
st.divider()
if st.session_state.contas:
    st.write("### 📝 Detalhamento Mensal")
    df_mes = pd.DataFrame(st.session_state.contas)
    st.table(df_mes)
    
    # Botões de Ação
    col_del, col_exp = st.columns(2)
    
    with col_exp:
        # Gerar CSV para Download (Balanço Mensal)
        csv = df_mes.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Baixar Balanço (CSV)",
            data=csv,
            file_name=f"balanco_{datetime.now().strftime('%m_%Y')}.csv",
            mime='text/csv',
            use_container_width=True
        )
        
    with col_del:
        if st.button("🗑️ Resetar Mês", use_container_width=True):
            st.session_state.contas = []
            salvar_dados(sal_ian, sal_iara, [])
            st.rerun()
else:
    st.info("Aguardando lançamentos para gerar o balanço.")
