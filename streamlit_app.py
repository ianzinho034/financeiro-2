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
    st.error("Erro nos Secrets! Verifique o GITHUB_TOKEN e o REPO_NAME no Streamlit.")
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

def salvar_historico_csv(dados):
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

# --- MENU LATERAL ---
st.sidebar.title("🍱 Menu Principal")
aba = st.sidebar.radio("Escolha a ferramenta:", ["💰 Finanças Mensais", "🛒 Lista de Compras"])

# Botão de Download do Histórico na Sidebar
st.sidebar.divider()
try:
    contents_hist = repo.get_contents("historico_gastos.csv")
    df_hist_download = pd.read_csv(io.StringIO(contents_hist.decoded_content.decode()))
    csv_hist = df_hist_download.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(label="📥 Baixar Histórico Geral", data=csv_hist, file_name='historico_financeiro.csv', mime='text/csv')
except:
    pass

# ---------------------------------------------------------
# ABA 1: FINANÇAS MENSAIS
# ---------------------------------------------------------
if aba == "💰 Finanças Mensais":
    if 'db' not in st.session_state:
        st.session_state.db = carregar_json("dados.json", {
            "contas": [], 
            "total_poupado": 989.93, 
            "renda_ian": 0.0, 
            "renda_iara": 0.0, 
            "renda_extra": 0.0, 
            "investido_feito": False,
            "valor_investido_travado": 0.0
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

    # --- LÓGICA DE CÁLCULOS MATEMÁTICOS ---
    renda_total = st.session_state.db["renda_ian"] + st.session_state.db["renda_iara"] + st.session_state.db["renda_extra"]
    gastos_total = sum(item['Valor'] for item in st.session_state.db["contas"])
    sobra_atual = renda_total - gastos_total

    # Se ainda não investiu, a metade é calculada sobre a sobra do momento
    if not st.session_state.db["investido_feito"]:
        valor_investir = sobra_atual / 2 if sobra_atual > 0 else 0.0
        sobra_exibida = sobra_atual
        livre_exibido = valor_investir
    else:
        # SE JÁ INVESTIU: O valor travado é o que "saiu" da sobra
        valor_investir = 0.00
        # Sobra exibida = Orçamento - Gastos - Valor que já foi para a poupança
        # Isso garante que 398.11 - 64.82 = 333.29
        sobra_exibida = sobra_atual - st.session_state.db.get("valor_investido_travado", 0.0)
        livre_exibido = sobra_exibida

    # Dashboard
    c1, c2, c3 = st.columns(3)
    c1.metric("💰 ORÇAMENTO", f"R$ {renda_total:,.2f}")
    c2.metric("💸 GASTOS", f"R$ {gastos_total:,.2f}")
    c3.metric("📉 SOBRA", f"R$ {sobra_exibida:,.2f}")

    st.markdown("---")
    d1, d2, d3 = st.columns(3)
    d1.metric("💜 INVESTIR", f"R$ {valor_investir:,.2f}")
    d2.metric("✅ LIVRE", f"R$ {livre_exibido:,.2f}")
    d3.metric("🏦 TOTAL POUPADO", f"R$ {st.session_state.db['total_poupado']:,.2f}")

    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        if st.button("🚀 CONFIRMAR INVESTIMENTO"):
            if not st.session_state.db["investido_feito"] and sobra_atual > 0:
                metade = sobra_atual / 2
                st.session_state.db["total_poupado"] += metade
                st.session_state.db["valor_investido_travado"] = metade
                st.session_state.db["investido_feito"] = True
                salvar_json("dados.json", st.session_state.db)
                st.rerun()
    
    with btn_col2:
        if st.button("🔒 FECHAR MÊS"):
            if st.session_state.db["contas"]:
                salvar_historico_csv(st.session_state.db["contas"])
                st.session_state.db["contas"] = []
                st.session_state.db["investido_feito"] = False
                st.session_state.db["valor_investido_travado"] = 0.0
                salvar_json("dados.json", st.session_state.db)
                st.rerun()

    # Tabela Editável
    st.divider()
    if st.session_state.db["contas"]:
        st.subheader("📄 Edição de Gastos Atuais")
        df_e = pd.DataFrame(st.session_state.db["contas"])
        df_e["Excluir"] = False
        ed_df = st.data_editor(df_e, use_container_width=True, hide_index=True)
        if st.button("💾 SALVAR CORREÇÕES DA TABELA"):
            st.session_state.db["contas"] = ed_df[ed_df["Excluir"] == False].drop(columns=["Excluir"]).to_dict('records')
            salvar_json("dados.json", st.session_state.db)
            st.rerun()

# ---------------------------------------------------------
# ABA 2: LISTA DE COMPRAS
# ---------------------------------------------------------
else:
    if 'compras' not in st.session_state:
        st.session_state.compras = carregar_json("compras.json", [])

    st.title("🛒 Comparador de Compras")
    
    with st.expander("➕ Adicionar Novo Produto"):
        cp1, cp2, cp3, cp4 = st.columns(4)
        p_nome = cp1.text_input("Nome do Produto")
        m_a = cp2.number_input("Mercado A (R$)", min_value=0.0)
        m_b = cp3.number_input("Mercado B (R$)", min_value=0.0)
        m_c = cp4.number_input("Mercado C (R$)", min_value=0.0)
        
        if st.button("Adicionar à Lista"):
            if p_nome:
                precos = {"Mercado A": m_a, "Mercado B": m_b, "Mercado C": m_c}
                validos = {k: v for k, v in precos.items() if v > 0}
                melhor = min(validos, key=validos.get) if validos else "N/A"
                preco_m = validos[melhor] if validos else 0.0
                st.session_state.compras.append({"Produto": p_nome, "Mercado A": m_a, "Mercado B": m_b, "Mercado C": m_c, "Onde comprar": melhor, "Menor Preço": preco_m})
                salvar_json("compras.json", st.session_state.compras)
                st.rerun()

    if st.session_state.compras:
        df_c = pd.DataFrame(st.session_state.compras)
        df_c["Excluir"] = False
        ed_c = st.data_editor(df_c, use_container_width=True, hide_index=True)
        
        if st.button("💾 ATUALIZAR LISTA DE COMPRAS"):
            nova_l = []
            for _, r in ed_c.iterrows():
                if not r["Excluir"]:
                    ps = {"Mercado A": r["Mercado A"], "Mercado B": r["Mercado B"], "Mercado C": r["Mercado C"]}
                    vs = {k: v for k, v in ps.items() if v > 0}
                    m_top = min(vs, key=vs.get) if vs else "N/A"
                    p_top = vs[m_top] if vs else 0.0
                    nova_l.append({"Produto": r["Produto"], "Mercado A": r["Mercado A"], "Mercado B": r["Mercado B"], "Mercado C": r["Mercado C"], "Onde comprar": m_top, "Menor Preço": p_top})
            st.session_state.compras = nova_l
            salvar_json("compras.json", st.session_state.compras)
            st.rerun()

        st.metric("💰 Total da Compra (Menores Preços)", f"R$ {df_c['Menor Preço'].sum():,.2f}")
        if st.button("🗑️ LIMPAR LISTA COMPLETA"):
            st.session_state.compras = []
            salvar_json("compras.json", [])
            st.rerun()
