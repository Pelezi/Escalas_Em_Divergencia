import streamlit as st
import pandas as pd
import mysql.connector
import decimal
import requests

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

# Configuração da página Streamlit
st.set_page_config(layout='wide')

if not 'df_scales' in st.session_state:
    # Carrega os dados da view `vw_vehicle_ocupation`
    st.session_state.df_scales = bd_phoenix('vw_scales')

dataframe_escalas = st.session_state.df_scales
st.title('Edição de escala')

st.divider()


uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, delimiter=";")
    # separate collumns by comma    
    st.write(df)

# Base URL for the guide API
BASE_URL = "https://driverjoao_pessoa.phoenix.comeialabs.com/scale/"

# Fetch data from the API with a search query
def fetch_data(search_query, object):
    params = {"page": 1, "fields": "", "q": search_query}
    try:
        if not search_query or search_query == "No results found":
            params.pop("q")
        response = requests.get(BASE_URL + object, params=params, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"An error occurred: {e}")
        return []
    
if uploaded_file is not None:
    for index, row in df.iterrows():
        dataframe_escala = dataframe_escalas[dataframe_escalas['Escala'] == row['Escala']]
        st.dataframe(dataframe_escala)
        id_escala = dataframe_escala['ID Escala'].values[0]
        id_servicos = dataframe_escala['ID Servico'].tolist()
        try:
            guia_api = fetch_data(row['Guia'], "guide")
            id_guia = guia_api[0]['id']
            st.write(id_guia)
            
            
        except Exception as e:
            st.error(f"An error occurred: {e}")
        
        payload = {
            "id_escala": id_escala,
            "id_guia": id_guia,
            "id_servicos": id_servicos
        }
        st.write(payload)
        guia = row['Guia']
        motorista = row['Motorista']
        veiculo = row['Veiculo']
        


# Parse the response data into a dictionary of nicknames and IDs
def parse_nicknames_and_ids(data):
    return {item["nickname"]: item["id"] for item in data}

# Streamlit app
st.title("Dynamic Nickname Selector")

# Text input for search query
search_query = st.text_input("Search for a nickname", value="", key="search_query")

# Fetch data dynamically based on the search query
# data = fetch_data(search_query)
# nicknames_and_ids = parse_nicknames_and_ids(data) if data else {}

# Ensure there is always an option to display
# options = list(nicknames_and_ids.keys()) or ["No results found"]

# Selectbox with search functionality
# selected_nickname = st.selectbox(
#     "Select a nickname",
#     options=options,
#     format_func=lambda x: x if x != "No results found" else "",
# )

# # Display and handle submission
# if selected_nickname and selected_nickname != "No results found":
#     selected_id = nicknames_and_ids[selected_nickname]
#     if st.button("Submit"):
#         st.success(f"Selected Nickname: {selected_nickname}, ID: {selected_id}")
#         # Add backend logic here if needed (e.g., sending the ID to a server)
# else:
#     st.warning("Please type and select a valid nickname.")