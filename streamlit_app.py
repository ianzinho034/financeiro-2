import streamlit as st
import pandas as pd
from github import Github # Certifique-se de colocar PyGithub no seu arquivo requirements.txt
import json
from datetime import datetime

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Ian & Iara Finanças", layout="wide")

# --- CONEXÃO COM GITHUB ---
try:
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])
except Exception as e:
    st.error("Erro na conexão com GitHub. Verifique os Secrets!")
    st.stop()

# --- FUNÇÕES DE NUVEM ---
def carregar_dados():
    try:
        contents = repo.get_contents("dados.json")
        return json.loads(contents.decoded_content.decode())
    except:
        return {"contas": [], "total_poupado": 357.47, "renda_ian": 0.0, "renda_iara": 0.0, "renda_extra": 0.0, "investido_feito": False}

def salvar_dados(dados):
    conteudo_json = json.dumps(dados, indent=4)
    contents = repo.get_contents("dados.json")
    repo.update_file(contents.path, "Atualização de saldo", conteudo_json, contents.sha)

# --- INICIALIZAÇÃO ---
if 'db' not in st.session_state:
    st.session_state.db = carregar_dados()

# --- SIDEBAR ---
st.sidebar.header("💰 Rendas")
st.session_state.db["renda_ian"] = st.sidebar.number_input("Renda Ian", value=float(st.session_state.db["renda_ian"]), format="%.2f")
st.session_state.db["renda_iara"] = st.sidebar.number_input("Renda Iara", value=float(st.session_state.db["renda_iara"]), format="%.2f")
st.session_state.db["renda_extra"] = st.sidebar.number_input("➕ Renda Extra", value=float(st.session_state.db["renda_extra"]), format="%.2f")

if st.sidebar.button("💾 SALVAR TUDO NA NUVEM"):
    salvar_dados(st.session_state.db)
    st.toast("Dados guardados com segurança!")

st.sidebar.divider()
st.sidebar.header("💸 Novo Gasto")
nome = st.sidebar.text_input("O que é?")
valor_gasto = st.sidebar.number_input("Valor R$", min_value=0.0, format="%.2f")

if st.sidebar.button("Adicionar Gasto"):
    if nome and valor_gasto > 0:
        st.session_state.db["contas"].append({'Descrição': nome, 'Valor': valor_gasto})
        salvar_dados(st.session_state.db)
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

# --- INTERFACE ---
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

if st.button("🚀 CONFIRMAR INVESTIMENTO"):
    if not st.session_state.db["investido_feito"] and inv > 0:
        st.session_state.db["total_poupado"] += inv
        st.session_state.db["investido_feito"] = True
        salvar_dados(st.session_state.db)
        st.rerun()

if st.button("🔒 FECHAR MÊS (LIMPAR)"):
    st.session_state.db["contas"] = []
    st.session_state.db["investido_feito"] = False
    salvar_dados(st.session_state.db)
    st.rerun()

st.divider()
if st.session_state.db["contas"]:
    st.dataframe(pd.DataFrame(st.session_state.db["contas"]), use_container_width=True)
