import streamlit as st
import pandas as pd
from datetime import datetime
import os

# 1. Configuração
st.set_page_config(page_title="Ian & Iara Finanças", layout="wide")

# Função para salvar no histórico (arquivo CSV)
def salvar_no_historico(dados):
    arquivo = 'historico_gastos.csv'
    df_novo = pd.DataFrame(dados)
    df_novo['Data_Fechamento'] = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    if os.path.exists(arquivo):
        df_antigo = pd.read_csv(arquivo)
        df_final = pd.concat([df_antigo, df_novo], ignore_index=True)
    else:
        df_final = df_novo
    
    df_final.to_csv(arquivo, index=False)

# 2. Estado da Sessão
if 'contas' not in st.session_state:
    st.session_state.contas = [{'Categoria': '💳 Geral', 'Descrição': 'Gastos Atuais', 'Valor': 3322.26}]

if 'total_poupado' not in st.session_state:
    st.session_state.total_poupado = 357.47

# 3. Sidebar
st.sidebar.header("💰 Ajustar Renda")
sal_ian = st.sidebar.number_input("Renda Ian", value=1894.34, format="%.2f")
sal_iara = st.sidebar.number_input("Renda Iara", value=1894.34, format="%.2f")

st.sidebar.divider()
st.sidebar.header("💸 Novo Gasto")
nome = st.sidebar.text_input("O que é?")
valor_gasto = st.sidebar.number_input("Valor R$", min_value=0.0, format="%.2f")

if st.sidebar.button("Adicionar"):
    if nome and valor_gasto > 0:
        st.session_state.contas.append({'Categoria': 'Variável', 'Descrição': nome, 'Valor': valor_gasto})
        st.rerun()

# 4. Cálculos
renda_total = sal_ian + sal_iara
gasto_total = sum(item['Valor'] for item in st.session_state.contas)
sobra_conta = renda_total - gasto_total
valor_investir = 0.00
valor_livre = 60.95

# 5. Dashboard
st.title("☀️ Ian & Iara Finanças")

c1, c2, c3, c4 = st.columns(4)
c1.metric("💰 ORÇAMENTO", f"R$ {renda_total:,.2f}")
c2.metric("💸 GASTO CONTA", f"R$ {gasto_total:,.2f}")
c3.metric("📉 SOBRA CONTA", f"R$ {sobra_conta:,.2f}")
c4.metric("🍱 SALDO VR", "R$ 0,00")

st.markdown("---")
st.subheader("🎯 Divisão da Sobra")

d1, d2, d3 = st.columns(3)
d1.metric("💜 INVESTIR", f"R$ {valor_investir:,.2f}")
d2.metric("✅ LIVRE P/ GASTAR", f"R$ {valor_livre:,.2f}")
d3.metric("🏦 TOTAL POUPADO", f"R$ {st.session_state.total_poupado:,.2f}")

# BOTÃO FECHAR MÊS (SAlva os dados)
if st.button("🔒 FECHAR MÊS E SALVAR HISTÓRICO"):
    if st.session_state.contas:
        salvar_no_historico(st.session_state.contas)
        st.session_state.contas = [] # Limpa o mês atual
        st.success("Mês fechado! Os gastos foram movidos para o histórico (Planilha).")
        st.rerun()
    else:
        st.warning("Não há gastos para salvar.")

# 6. Tabela e Histórico
st.divider()
col_atual, col_hist = st.columns(2)

with col_atual:
    st.write("### 📄 Gastos do Mês Atual")
    df = pd.DataFrame(st.session_state.contas)
    st.dataframe(df, use_container_width=True, hide_index=True)

with col_hist:
    st.write("### 📜 Histórico Acumulado (Planilha)")
    if os.path.exists('historico_gastos.csv'):
        df_hist = pd.read_csv('historico_gastos.csv')
        st.dataframe(df_hist, use_container_width=True, hide_index=True)
        
        # Botão para baixar a planilha real
        csv_download = df_hist.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Baixar Planilha Excel (.csv)", data=csv_download, file_name="historico_financeiro.csv", mime="text/csv")
    else:
        st.info("O histórico aparecerá aqui após o primeiro fechamento.")
