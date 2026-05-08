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
    st.error("Erro nos Secrets! Verifique o GITHUB_TOKEN e o REPO_NAME no Streamlit.")
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
    df_novo['Data_Fechamento'] = datetime.now().strftime("%m/%Y")
    
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

# Rendas com salvamento automático
n_ian = st.sidebar.number_input("Renda Ian", value=float(st.session_state.db["renda_ian"]), format="%.2f")
if n_ian != st.session_state.db["renda_ian"]:
    st.session_state.db["renda_ian"] = n_ian
    salvar_dados_auto()

n_iara = st.sidebar.number_input("Renda Iara", value=float(st.session_state.db["renda_iara"]), format="%.2f")
if n_iara != st.session_state.db["renda_iara"]:
    st.session_state.db["renda_iara"] = n_iara
    salvar_dados_auto()

n_extra = st.sidebar.number_input("➕ Renda Extra", value=float(st.session_state.db["renda_extra"]), format="%.2f")
if n_extra != st.session_state.db["renda_extra"]:
    st.session_state.db["renda_extra"] = n_extra
    salvar_dados_auto()

st.sidebar.divider()
st.sidebar.header("📥 Exportar")
if st.session_state.db["contas"]:
    csv_data = pd.DataFrame(st.session_state.db["contas"]).to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(label="Baixar Gastos (CSV)", data=csv_data, file_name=f"gastos_{datetime.now().strftime('%m_%Y')}.csv", mime='text/csv')

st.sidebar.divider()
st.sidebar.header("💸 Novo Gasto")
nome_novo = st.sidebar.text_input("O que é?")
valor_novo = st.sidebar.number_input("Valor R$", min_value=0.0, format="%.2f")

if st.sidebar.button("Adicionar Gasto"):
    if nome_novo and valor_novo > 0:
        st.session_state.db["contas"].append({'Descrição': nome_novo, 'Valor': valor_novo})
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
        else:
            st.warning("Adicione gastos antes de fechar o mês.")

# --- GRÁFICO DE EVOLUÇÃO ---
st.divider()
st.subheader("📊 Evolução de Gastos (Mês a Mês)")
try:
    contents_h = repo.get_contents("historico_gastos.csv")
    df_hist = pd.read_csv(io.StringIO(contents_h.decoded_content.decode()))
    if not df_hist.empty:
        resumo_mensal = df_hist.groupby('Data_Fechamento')['Valor'].sum().reset_index()
        st.bar_chart(data=resumo_mensal, x='Data_Fechamento', y='Valor')
except:
    st.info("O gráfico aparecerá aqui após o primeiro 'Fechar Mês'.")

# --- TABELA DE GASTOS EDITÁVEL ---
st.divider()
if st.session_state.db["contas"]:
    st.write("### 📄 Gastos do Mês Atual")
    st.caption("💡 Edite os valores abaixo ou marque 'Excluir' e clique no botão de salvar para corrigir erros.")
    
    df_edit = pd.DataFrame(st.session_state.db["contas"])
    df_edit["Excluir"] = False
    
    # Tabela editável
    edited_df = st.data_editor(
        df_edit, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Excluir": st.column_config.CheckboxColumn(help="Marque para remover")
        }
    )

    if st.button("💾 SALVAR ALTERAÇÕES NA TABELA"):
        # Filtra apenas quem não foi marcado para excluir e remove a coluna de controle
        nova_lista = edited_df[edited_df["Excluir"] == False].drop(columns=["Excluir"]).to_dict('records')
        st.session_state.db["contas"] = nova_lista
        salvar_dados_auto()
        st.success("Alterações salvas!")
        st.rerun()
else:
    st.info("Nenhum gasto registado.")
