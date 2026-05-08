import streamlit as st
import pandas as pd
from github import Github
import json
from datetime import datetime
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ian & Iara Finanças", layout="wide")

# --- CONEXÃO COM GITHUB ---
try:
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])
except Exception as e:
    st.error("Erro nos Secrets! Verifique o GITHUB_TOKEN e o REPO_NAME.")
    st.stop()

# --- FUNÇÕES DE NUVEM (AUTO-SAVE) ---
def carregar_dados():
    try:
        contents = repo.get_contents("dados.json")
        return json.loads(contents.decoded_content.decode())
    except:
        return {
            "contas": [], 
            "total_poupado": 357.47, 
            "renda_ian": 0.0, 
            "renda_iara": 0.0, 
            "renda_extra": 0.0, 
            "investido_feito": False
        }

def salvar_dados_auto():
    dados = st.session_state.db
    conteudo_json = json.dumps(dados, indent=4)
    contents = repo.get_contents("dados.json")
    repo.update_file(contents.path, "Auto-save Finanças", conteudo_json, contents.sha)

def salvar_no_historico_github(dados):
    arquivo_hist = "historico_gastos.csv"
    df_novo = pd.DataFrame(dados)
    df_novo['Data_Fechamento'] = datetime.now().strftime("%m/%Y") # Mês/Ano
    
    try:
        contents = repo.get_contents(arquivo_hist)
        df_antigo = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
        df_final = pd.concat([df_antigo, df_novo], ignore_index=True)
        repo.update_file(contents.path, "Update Histórico", df_final.to_csv(index=False), contents.sha)
    except:
        repo.create_file(arquivo_hist, "Create Histórico", df_novo.to_csv(index=False))

# --- INICIALIZAÇÃO ---
if 'db' not in st.session_state:
    st.session_state.db = carregar_dados()

# --- SIDEBAR ---
st.sidebar.header("💰 Rendas")

nova_ian = st.sidebar.number_input("Renda Ian", value=float(st.session_state.db["renda_ian"]), format="%.2f")
if nova_ian != st.session_state.db["renda_ian"]:
    st.session_state.db["renda_ian"] = nova_ian
    salvar_dados_auto()

nova_iara = st.sidebar.number_input("Renda Iara", value=float(st.session_state.db["renda_iara"]), format="%.2f")
if nova_iara != st.session_state.db["renda_iara"]:
    st.session_state.db["renda_iara"] = nova_iara
    salvar_dados_auto()

nova_extra = st.sidebar.number_input("➕ Renda Extra", value=float(st.session_state.db["renda_extra"]), format="%.2f")
if nova_extra != st.session_state.db["renda_extra"]:
    st.session_state.db["renda_extra"] = nova_extra
    salvar_dados_auto()

st.sidebar.divider()
st.sidebar.header("📥 Exportar")
if st.session_state.db["contas"]:
    csv_data = pd.DataFrame(st.session_state.db["contas"]).to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(label="Baixar Gastos do Mês (CSV)", data=csv_data, file_name=f"gastos_{datetime.now().strftime('%m_%Y')}.csv", mime='text/csv')

st.sidebar.divider()
st.sidebar.header("💸 Novo Gasto")
nome = st.sidebar.text_input("O que é?")
valor_gasto = st.sidebar.number_input("Valor R$", min_value=0.0, format="%.2f")

if st.sidebar.button("Adicionar Gasto"):
    if nome and valor_gasto > 0:
        st.session_state.db["contas"].append({'Descrição': nome, 'Valor': valor_gasto})
        salvar_dados_auto()
        st.rerun()

# --- CÁLCULOS ---
renda_t = st.session_state.db["renda_ian"] + st.session_state.db["renda_iara"] + st.session_state.db["renda_extra"]
gasto_t = sum(item['Valor'] for item in st.session_state.db["contas"])
sobra = renda_t - gasto_t

if st.session_state.db["investido_feito"]:
    inv, livre = 0.00, 60.95
else:
    inv = sobra / 2 if sobra > 0 else 0.0
    livre = sobra / 2 if sobra > 0 else 0.0

# --- INTERFACE PRINCIPAL ---
st.title("☀️ Ian & Iara Finanças")

c1, c2, c3 = st.columns(3)
c1.metric("💰 ORÇAMENTO", f"R$ {renda_t:,.2f}")
c2.metric("💸 GASTOS", f"R$ {gasto_t:,.2f}")
c3.metric("📉 SOBRA", f"R$ {sobra:,.2f}")

st.markdown("---")
d1, d2, d3 = st.columns(3)
d1.metric("💜 INVESTIR", f"R$ {inv:,.2f}")
d2.metric("✅ LIVRE", f"R$ {livre:,.2f}")
d3.metric("🏦 TOTAL POUPADO", f"R$ {st.session_state.db['total_poupado']:,.2f}")

col_btns = st.columns(2)
with col_btns[0]:
    if st.button("🚀 CONFIRMAR INVESTIMENTO"):
        if not st.session_state.db["investido_feito"] and inv > 0:
            st.session_state.db["total_poupado"] += inv
            st.session_state.db["investido_feito"] = True
            salvar_dados_auto()
            st.rerun()

with col_btns[1]:
    if st.button("🔒 FECHAR MÊS (SALVAR HISTÓRICO)"):
        if st.session_state.db["contas"]:
            salvar_no_historico_github(st.session_state.db["contas"])
            st.session_state.db["contas"] = []
            st.session_state.db["investido_feito"] = False
            salvar_dados_auto()
            st.success("Mês fechado e salvo no histórico!")
            st.rerun()

# --- GRÁFICO DE EVOLUÇÃO ---
st.divider()
st.subheader("📊 Evolução de Gastos (Mês a Mês)")
try:
    contents = repo.get_contents("historico_gastos.csv")
    df_hist = pd.read_csv(io.StringIO(contents.decoded_content.decode()))
    if not df_hist.empty:
        # Agrupa gastos por mês
        resumo_mensal = df_hist.groupby('Data_Fechamento')['Valor'].sum().reset_index()
        st.bar_chart(data=resumo_mensal, x='Data_Fechamento', y='Valor')
    else:
        st.info("Ainda não há dados históricos para mostrar o gráfico.")
except:
    st.info("O gráfico aparecerá aqui após você fechar o primeiro mês.")

# --- TABELA DE GASTOS ---
if st.session_state.db["contas"]:
    st.write("### 📄 Gastos do Mês Atual")
    st.dataframe(pd.DataFrame(st.session_state.db["contas"]), use_container_width=True, hide_index=True)
