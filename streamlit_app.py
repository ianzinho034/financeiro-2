import streamlit as st
import pandas as pd
import os

# Configuração da Página para Celular
st.set_page_config(page_title="Controle Ian & Iara", layout="centered")

# --- FUNÇÕES DE PERSISTÊNCIA ---
def salvar_dados(renda_ian, renda_iara, gastos_lista):
    # Salva os valores atuais para não perder ao fechar o app
    df = pd.DataFrame(gastos_lista)
    df['renda_ian'] = renda_ian
    df['renda_iara'] = renda_iara
    df.to_csv('dados_atuais.csv', index=False)

def carregar_dados():
    if os.path.exists('dados_atuais.csv'):
        df = pd.read_csv('dados_atuais.csv')
        rendas = (df['renda_ian'][0], df['renda_iara'][0])
        contas = df[['Descrição', 'Valor']].to_dict('records')
        return rendas, contas
    return (0.0, 0.0), []

# --- INICIALIZAÇÃO ---
rendas_salvas, contas_salvas = carregar_dados()

if 'contas' not in st.session_state:
    st.session_state.contas = contas_salvas

# --- INTERFACE ---
st.title("💰 Controle Ian & Iara")

# 1. ENTRADA DE RENDAS
with st.expander("💵 Ajustar Salários", expanded=False):
    col1, col2 = st.columns(2)
    sal_ian = col1.number_input("Ian R$", value=rendas_salvas[0], step=100.0)
    sal_iara = col2.number_input("Iara R$", value=rendas_salvas[1], step=100.0)
    renda_total = sal_ian + sal_iara

# 2. ADICIONAR CONTA/GASTO
st.subheader("💸 Adicionar Conta")
c_nome = st.text_input("Descrição (ex: Aluguel, Luz...)")
c_valor = st.number_input("Valor da Conta R$", min_value=0.0, step=10.0)

if st.button("➕ Adicionar à Lista"):
    if c_nome and c_valor > 0:
        st.session_state.contas.append({'Descrição': c_nome, 'Valor': c_valor})
        salvar_dados(sal_ian, sal_iara, st.session_state.contas)
        st.rerun()

st.divider()

# 3. CÁLCULOS
total_gastos = sum(item['Valor'] for item in st.session_state.contas)
sobra_total = renda_total - total_gastos

# Regra dos 50/50 solicitada
valor_investir = sobra_total / 2 if sobra_total > 0 else 0
valor_gastar = sobra_total / 2 if sobra_total > 0 else 0

# 4. EXIBIÇÃO DOS RESULTADOS (DASHBOARD)
st.metric("📊 RENDA TOTAL", f"R$ {renda_total:,.2f}")
st.metric("📉 TOTAL DE CONTAS", f"R$ {total_gastos:,.2f}", delta=f"-{total_gastos:,.2f}", delta_color="inverse")

st.markdown("---")
st.subheader("🎯 Destino da Sobra")

col_inv, col_gas = st.columns(2)
with col_inv:
    st.success(f"**PARA INVESTIR**\n\n R$ {valor_investir:,.2f}")
with col_gas:
    st.info(f"**PARA GASTAR**\n\n R$ {valor_gastar:,.2f}")

# 5. LISTA DE CONTAS LANÇADAS
st.divider()
st.write("### 📝 Detalhes das Contas")
if st.session_state.contas:
    df_contas = pd.DataFrame(st.session_state.contas)
    st.table(df_contas) # Table fica melhor que Dataframe no celular
    
    if st.button("🗑️ Limpar Tudo"):
        st.session_state.contas = []
        if os.path.exists('dados_atuais.csv'):
            os.remove('dados_atuais.csv')
        st.rerun()
else:
    st.info("Nenhuma conta lançada.")
