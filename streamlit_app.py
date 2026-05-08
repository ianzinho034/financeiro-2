import streamlit as st
import pandas as pd  # Corrigido: o nome da biblioteca é pandas
from datetime import datetime
import os

# --- FUNÇÕES DE APOIO (PERSISTÊNCIA) ---

def salvar_poupado(valor):
    """Salva o valor acumulado em um arquivo de texto para não perder ao reiniciar."""
    with open("total_poupado.txt", "w") as f:
        f.write(str(valor))

def carregar_poupado():
    """Carrega o valor acumulado do arquivo ou inicia com o valor padrão."""
    if os.path.exists("total_poupado.txt"):
        with open("total_poupado.txt", "r") as f:
            return float(f.read())
    return 357.47

def salvar_no_historico(dados):
    """Salva os gastos do mês em uma planilha CSV."""
    arquivo = 'historico_gastos.csv'
    df_novo = pd.DataFrame(dados)
    df_novo['Data_Fechamento'] = datetime.now().strftime("%d/%m/%Y %H:%M")
    if os.path.exists(arquivo):
        df_antigo = pd.read_csv(arquivo)
        df_final = pd.concat([df_antigo, df_novo], ignore_index=True)
    else:
        df_final = df_novo
    df_final.to_csv(arquivo, index=False)

# 1. Configuração da Página
st.set_page_config(page_title="Ian & Iara Finanças", layout="wide")

# 2. Estado da Sessão
if 'contas' not in st.session_state:
    st.session_state.contas = []
if 'total_poupado' not in st.session_state:
    st.session_state.total_poupado = carregar_poupado()
if 'investido_feito' not in st.session_state:
    st.session_state.investido_feito = False

# 3. Sidebar (Entradas)
st.sidebar.header("💰 Renda Mensal")
sal_ian = st.sidebar.number_input("Renda Ian", value=0.0, format="%.2f")
sal_iara = st.sidebar.number_input("Renda Iara", value=0.0, format="%.2f")
renda_extra = st.sidebar.number_input("➕ Renda Extra", value=0.0, format="%.2f")

st.sidebar.divider()
st.sidebar.header("💸 Novo Gasto")
nome = st.sidebar.text_input("O que é?")
valor_gasto = st.sidebar.number_input("Valor R$", min_value=0.0, format="%.2f")

if st.sidebar.button("Adicionar"):
    if nome and valor_gasto > 0:
        st.session_state.contas.append({'Categoria': 'Geral', 'Descrição': nome, 'Valor': valor_gasto})
        st.rerun()

# 4. Cálculos de Orçamento
renda_total = sal_ian + sal_iara + renda_extra
gasto_total = sum(item['Valor'] for item in st.session_state.contas)
sobra_conta = renda_total - gasto_total

# Lógica da Divisão da Sobra
valor_sugerido_investimento = sobra_conta / 2 if sobra_conta > 0 else 0.0

if st.session_state.investido_feito:
    exibir_investir = 0.00
    exibir_livre = 60.95  # Valor fixo solicitado por você
else:
    exibir_investir = valor_sugerido_investimento
    exibir_livre = valor_sugerido_investimento

# 5. Interface Principal
st.title("☀️ Ian & Iara Finanças")

# Linha 1: Métricas de Orçamento
c1, c2, c3 = st.columns(3)
c1.metric("💰 ORÇAMENTO TOTAL", f"R$ {renda_total:,.2f}")
c2.metric("💸 GASTO CONTA", f"R$ {gasto_total:,.2f}")
c3.metric("📉 SOBRA CONTA", f"R$ {sobra_conta:,.2f}")

st.markdown("---")
st.subheader("🎯 Divisão da Sobra")

# Linha 2: Divisão e Poupança
d1, d2, d3 = st.columns(3)
d1.metric("💜 INVESTIR", f"R$ {exibir_investir:,.2f}")
d2.metric("✅ LIVRE P/ GASTAR", f"R$ {exibir_livre:,.2f}")
d3.metric("🏦 TOTAL POUPADO", f"R$ {st.session_state.total_poupado:,.2f}")

# --- BOTÕES DE AÇÃO ---
col_btn1, col_btn2 = st.columns(2)

with col_btn1:
    if st.button("🚀 CONFIRMAR INVESTIMENTO"):
        if not st.session_state.investido_feito and exibir_investir > 0:
            # Soma ao total, salva no arquivo e zera o card visualmente
            st.session_state.total_poupado += exibir_investir
            salvar_poupado(st.session_state.total_poupado)
            st.session_state.investido_feito = True
            st.success(f"R$ {exibir_investir:.2f} somados ao Total Poupado!")
            st.rerun()
        elif st.session_state.investido_feito:
            st.info("O investimento deste mês já foi processado.")
        else:
            st.warning("Não há valor positivo para investir.")

with col_btn2:
    if st.button("🔒 FECHAR MÊS E SALVAR"):
        if st.session_state.contas:
            salvar_no_historico(st.session_state.contas)
            st.session_state.contas = []
            st.session_state.investido_feito = False
            st.success("Mês fechado e salvo no histórico CSV!")
            st.rerun()
        else:
            st.warning("Adicione gastos antes de fechar o mês.")

# 6. Tabela de Gastos
st.divider()
st.write("### 📄 Gastos do Mês Atual")
if st.session_state.contas:
    df = pd.DataFrame(st.session_state.contas)
    st.dataframe(df, use_container_width=True, hide_index=True)
    
    if st.button("Limpar Gastos Atuais"):
        st.session_state.contas = []
        st.session_state.investido_feito = False
        st.rerun()
else:
    st.info("Nenhum gasto registrado para este período.")
