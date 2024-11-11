import streamlit as st
import mysql.connector
import decimal
import pandas as pd
import time

config = {
    'user': 'user_automation_jpa',
    'password': 'luck_jpa_2024',
    'host': 'comeia.cixat7j68g0n.us-east-1.rds.amazonaws.com',
    'database': 'test_phoenix_joao_pessoa'
}
def bd_phoenix(vw_name):
    # Parametros de Login AWS
    # Conexão às Views
    conexao = mysql.connector.connect(**config)
    cursor = conexao.cursor()

    request_name = f'SELECT * FROM {vw_name}'

    # Script MySQL para requests
    cursor.execute(request_name)
    # Coloca o request em uma variavel
    resultado = cursor.fetchall()
    # Busca apenas os cabeçalhos do Banco
    cabecalho = [desc[0] for desc in cursor.description]

    # Fecha a conexão
    cursor.close()
    conexao.close()

    # Coloca em um dataframe e converte decimal para float
    df = pd.DataFrame(resultado, columns=cabecalho)
    df = df.applymap(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
    return df

if not 'df_scale_date_divergence' in st.session_state:
    # Carrega os dados da view `vw_vehicle_ocupation`
    st.session_state.df_scale_date_divergence = bd_phoenix('vw_scale_date_divergence')

st.title('Escalas com divergência de data')

st.divider()

# Input de intervalo de data
row0 = st.columns(4)
with row0[0]:
    periodo = st.date_input('Período', value=[], format='DD/MM/YYYY')

# Filtra os dados conforme o intervalo de tempo informado
if len(periodo) == 2:  # Verifica se o intervalo está completo
    data_inicial, data_final = periodo

    df_filtrado = st.session_state.df_scale_date_divergence[
        (st.session_state.df_scale_date_divergence['Data Execucao'] >= data_inicial) &
        (st.session_state.df_scale_date_divergence['Data Execucao'] <= data_final)
    ].reset_index(drop=True)
            
    # Exibe o dataframe completo
    st.divider()
    st.dataframe(df_filtrado, hide_index=True, use_container_width=True)
else:
    
    df = st.session_state.df_scale_date_divergence
    
    st.divider()
    st.subheader('Ocupação Média por Tipo de Veículo')
    st.dataframe(df, hide_index=True, use_container_width=True)