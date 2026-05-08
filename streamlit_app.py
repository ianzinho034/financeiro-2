# --- 7. HISTÓRICO E EXPORTAÇÃO ---
st.divider()
if st.session_state.contas:
    st.write("### 📝 Detalhamento Mensal")
    
    # Criamos um DataFrame para exibição
    df_exibicao = pd.DataFrame(st.session_state.contas)
    
    # CORREÇÃO AQUI: Formata a coluna 'Valor' para exibir 2 casas decimais e vírgula
    df_exibicao['Valor'] = df_exibicao['Valor'].map('R$ {:,.2f}'.format)
    
    # Exibe a tabela formatada
    st.table(df_exibicao)
    
    # Botões de Ação
    col_del, col_exp = st.columns(2)
    
    with col_exp:
        # Para o download, usamos o DataFrame original (com números) para não dar erro no Excel
        df_para_download = pd.DataFrame(st.session_state.contas)
        csv = df_para_download.to_csv(index=False).encode('utf-8')
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
