import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Ian & Iara Finanças", layout="centered")

# --- ESTILO CUSTOMIZADO ---
st.markdown("""
    <style>
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
    div[data-testid="stMetricValue"] { color: #2e7d32; }
    </style>
    """, unsafe_allow_html=True)

# --- INICIALIZAÇÃO DO ESTADO ---
if 'contas' not in st.session_state:
    st.session_state.contas = []

# --- SIDEBAR (CONFIGURAÇÕES) ---
st.sidebar.header("⚙️ Configurações")
sal_ian = st.sidebar.number_input("Renda Ian", value=1894.34, step=100.0)
sal_iara = st.sidebar.number_input("Renda Iara", value=1894.34, step=100.0)
renda_total = sal_ian + sal_iara

# --- ÁREA DE LANÇAMENTO ---
st.title("☀️ Ian & Iara Finanças")
st.subheader("💸 Novo Gasto")

with st.container():
    col_n, col_v, col_b = st.columns([2, 1, 1])
    nome = col_n.text_input("O que é?", placeholder="Ex: Aluguel")
    valor = col_v.number_input("Valor R$", min_value=0.0, step=10.0)
    if col_b.button("✅ Adicionar", use_container_width=True):
        if nome and valor > 0:
            st.session_state.contas.append({'Descrição': nome, 'Valor': valor})
            st.rerun()

st.divider()

# --- CÁLCULOS ---
gasto_total = sum(item['Valor'] for item in st.session_state.contas)
sobra_total = renda_total - gasto_total

# Divisão 50/50 (Só calcula se sobrar dinheiro)
if sobra_total > 0:
    valor_investir = sobra_total / 2
    valor_gastar = sobra_total / 2
else:
    valor_investir = 0.0
    valor_gastar = 0.0

# --- DASHBOARD DE RESULTADOS ---
c1, c2 = st.columns(2)
c1.metric("💰 RENDA TOTAL", f"R$ {renda_total:,.2f}")
c2.metric("📉 TOTAL GASTOS", f"R$ {gasto_total:,.2f}", delta=f"-{gasto_total:,.2f}", delta_color="inverse")

st.markdown("---")
st.subheader("🎯 Destino da Sobra")

d1, d2 = st.columns(2)
with d1:
    st.success(f"**💜 INVESTIR (50%)**\n\n R$ {valor_investir:,.2f}")
with d2:
    st.info(f"**🛍️ GASTAR (50%)**\n\n R$ {valor_gastar:,.2f}")

# --- LISTA DE GASTOS COM OPÇÃO DE DELETAR ---
st.divider()
st.subheader("📝 Detalhes do Mês")

if st.session_state.contas:
    df = pd.DataFrame(st.session_state.contas)
    
    # Exibe a tabela
    st.table(df)
    
    # Botão para limpar o mês
    if st.button("🗑️ Limpar Mês / Novo Ciclo"):
        st.session_state.contas = []
        st.rerun()
else:
    st.info("Nenhum gasto lançado ainda. Comece adicionando acima!")
