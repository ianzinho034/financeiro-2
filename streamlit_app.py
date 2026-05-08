import streamlit as st
import pandas as pd
from github import Github
import json
from datetime import datetime
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Gestão Ian & Iara", layout="wide", page_icon="💰")

# --- CONEXÃO COM GITHUB ---
try:
    g = Github(st.secrets["GITHUB_TOKEN"])
    repo = g.get_repo(st.secrets["REPO_NAME"])
except Exception as e:
    st.error("Erro nos Secrets!")
    st.stop()

# --- FUNÇÕES DE NUVEM ---
def carregar_json(nome_arquivo, default_value):
    try:
        contents = repo.get_contents(nome_arquivo)
        return json.loads(contents.decoded_content.decode())
    except:
        return default_value

def salvar_json(nome_arquivo, dados):
    conteudo_json = json.dumps(dados, indent=4)
    contents = repo.get_contents(nome_arquivo)
    repo.update_file(contents.path, f"Auto-save {nome_arquivo}", conteudo_json, contents.sha)

# --- MENU LATERAL ---
st.sidebar.title("🍱 Menu Principal")
aba = st.sidebar.radio("Escolha a ferramenta:", ["💰 Finanças Mensais", "🛒 Lista de Compras"])

# ---------------------------------------------------------
# ABA 1: FINANÇAS MENSAIS
# ---------------------------------------------------------
if aba == "💰 Finanças Mensais":
    if 'db' not in st.session_state:
        # ALTERADO AQUI: Valor inicial ajustado para 989.93 conforme solicitado
        st.session_state.db = carregar_json("dados.json", {
            "contas": [], 
            "total_poupado": 989.93, 
            "renda_ian": 0.0, 
            "renda_iara": 0.0, 
            "renda_extra": 0.0, 
            "investido_feito": False
        })

    st.title("☀️ Ian & Iara Finanças")
    
    # Rendas na Sidebar
    st.sidebar.subheader("💵 Ajustar Rendas")
    n_ian = st.sidebar.number_input("Renda Ian", value=float(st.session_state.db["renda_ian"]), format="%.2f")
    if n_ian != st.session_state.db["renda_ian"]:
        st.session_state.db["renda_ian"] = n_ian
        salvar_json("dados.json", st.session_state.db)

    n_iara = st.sidebar.number_input("Renda Iara", value=float(st.session_state.db["renda_iara"]), format="%.2f")
    if n_iara != st.session_state.db["renda_iara"]:
        st.session_state.db["renda_iara"] = n_iara
        salvar_json("dados.json", st.session_state.db)

    n_extra = st.sidebar.number_input("Renda Extra", value=float(st.session_state.db["renda_extra"]), format="%.2f")
    if n_extra != st.session_state.db["renda_extra"]:
        st.session_state.db["renda_extra"] = n_extra
        salvar_json("dados.json", st.session_state.db)

    # Novo Gasto
    st.sidebar.divider()
    st.sidebar.subheader("💸 Novo Gasto")
    ng_nome = st.sidebar.text_input("O que é?")
    ng_valor = st.sidebar.number_input("Valor R$", min_value=0.0, format="%.2f")
    if st.sidebar.button("Adicionar Gasto"):
        if ng_nome and ng_valor > 0:
            st.session_state.db["contas"].append({'Descrição': ng_nome, 'Valor': ng_valor})
            salvar_json("dados.json", st.session_state.db)
            st.rerun()

    # --- CÁLCULOS ---
    renda_t = st.session_state.db["renda_ian"] + st.session_state.db["renda_iara"] + st.session_state.db["renda_extra"]
    gasto_t = sum(item['Valor'] for item in st.session_state.db["contas"])
    sobra = renda_t - gasto_t
    metade_sobra = sobra / 2 if sobra > 0 else 0.0

    # Dashboard
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 ORÇAMENTO", f"R$ {renda_t:,.2f}")
    c2.metric("💸 GASTOS", f"R$ {gasto_t:,.2f}")
    c3.metric("📉 SOBRA", f"R$ {sobra:,.2f}")

    st.markdown("---")
    d1, d2, d3 = st.columns(3)
    # Investir zera se o botão for clicado, Livre mantém sempre a metade da sobra
    d1.metric("💜 INVESTIR", f"R$ {0.00 if st.session_state.db['investido_feito'] else metade_sobra:,.2f}")
    d2.metric("✅ LIVRE", f"R$ {metade_sobra:,.2f}")
    d3.metric("🏦 TOTAL POUPADO", f"R$ {st.session_state.db['total_poupado']:,.2f}")

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("🚀 CONFIRMAR INVESTIMENTO"):
            if not st.session_state.db["investido_feito"]:
                st.session_state.db["total_poupado"] += metade_sobra
                st.session_state.db["investido_feito"] = True
                salvar_json("dados.json", st.session_state.db)
                st.rerun()
    
    with btn_col2:
        if st.button("🔒 FECHAR MÊS"):
            st.session_state.db["contas"] = []
            st.session_state.db["investido_feito"] = False
            salvar_json("dados.json", st.session_state.db)
            st.rerun()

    # Tabela Editável
    st.divider()
    if st.session_state.db["contas"]:
        st.subheader("📄 Edição de Gastos")
        df_e = pd.DataFrame(st.session_state.db["contas"])
        df_e["Excluir"] = False
        ed_df = st.data_editor(df_e, use_container_width=True, hide_index=True)
        if st.button("💾 SALVAR ALTERAÇÕES"):
            st.session_state.db["contas"] = ed_df[ed_df["Excluir"] == False].drop(columns=["Excluir"]).to_dict('records')
            salvar_json("dados.json", st.session_state.db)
            st.rerun()

# ---------------------------------------------------------
# ABA 2: LISTA DE COMPRAS (Mantida igual)
# ---------------------------------------------------------
else:
    st.title("🛒 Comparador de Compras")
    st.write("Sua lista de compras aparecerá aqui.")
