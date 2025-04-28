#%%
import streamlit as st
import pandas as pd
from io import BytesIO
def main():
    st.title("🔎 Verificador de BND")

    st.header("1. Upload dos arquivos")
    uploaded_peps = st.file_uploader("Arquivo de PEPs", type=["csv", "xlsx"])
    uploaded_bsns = st.file_uploader("Arquivo de BSNs/Demands", type=["csv", "xlsx"])
    uploaded_terceiro = st.file_uploader("Arquivo Terceiro", type=["csv", "xlsx"])

    # Só processar após os arquivos serem carregados
    if uploaded_peps and uploaded_bsns and uploaded_terceiro:
        # Verificar se o arquivo de PEPs é CSV ou Excel e carregar corretamente
        if uploaded_peps.name.endswith('.xlsx'):
            peps_df = pd.read_excel(uploaded_peps)
        else:
            peps_df = pd.read_csv(uploaded_peps)

        # Verificar se o arquivo de BSNs é CSV ou Excel e carregar corretamente
        if uploaded_bsns.name.endswith('.xlsx'):
            bsns_df = pd.read_excel(uploaded_bsns)
        else:
            bsns_df = pd.read_csv(uploaded_bsns)

        # Verificar se o arquivo Terceiro é CSV ou Excel e carregar corretamente
        if uploaded_terceiro.name.endswith('.xlsx'):
            terceiro_df = pd.read_excel(uploaded_terceiro)
        else:
            terceiro_df = pd.read_csv(uploaded_terceiro)

        st.success("Arquivos carregados com sucesso!")

        # Configurações de colunas
        st.header("2. Configurações de colunas")
        coluna_pep_bsn = st.selectbox("Escolha a coluna de PEP no arquivo de BSNs:", bsns_df.columns)
        colunas_bnd = st.multiselect("Escolha as colunas para trazer do BSNs:", bsns_df.columns)
        coluna_chave_terceiro = st.selectbox("Escolha a coluna para cruzar no Terceiro Arquivo:", terceiro_df.columns)
        colunas_terceiro = st.multiselect("Escolha as colunas para trazer do Terceiro Arquivo:", terceiro_df.columns)

        # Adicionando o botão de processamento
        if st.button("🔍 Processar"):
            try:
                # Primeiro merge: PEP x BSNs
                resultado = pd.merge(
                    peps_df,
                    bsns_df[[coluna_pep_bsn] + colunas_bnd],
                    left_on=peps_df.columns[0],
                    right_on=coluna_pep_bsn,
                    how='left'
                )

                # Segundo merge: resultado x Terceiro
                resultado = pd.merge(
                    resultado,
                    terceiro_df[[coluna_chave_terceiro] + colunas_terceiro],
                    left_on=colunas_bnd[0],
                    right_on=coluna_chave_terceiro,
                    how='left'
                )

                # Remover duplicados com base no PEP
                resultado_final = resultado.drop_duplicates(subset=[peps_df.columns[0]])

                # Organizar
                colunas_final = [peps_df.columns[0]] + colunas_bnd + colunas_terceiro
                resultado_final = resultado_final[colunas_final]
                resultado_final = resultado_final.fillna("Não encontrado")

                st.success("Consulta finalizada! Veja abaixo o resultado:")

                st.dataframe(resultado_final)

                # Gerar download do resultado
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    resultado_final.to_excel(writer, index=False, sheet_name='Resultado')
                output.seek(0)

                st.download_button(
                    label="📥 Baixar resultado como Excel",
                    data=output,
                    file_name="resultado_final.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"Erro durante o processamento: {str(e)}")

if __name__ == "__main__":
    main()