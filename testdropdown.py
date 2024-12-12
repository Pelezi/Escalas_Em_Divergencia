import streamlit as st
import mysql.connector
import decimal
import pandas as pd
import requests

st.set_page_config(layout='wide')


config = {
    'user': 'user_automation_jpa',
    'password': 'luck_jpa_2024',
    'host': 'comeia.cixat7j68g0n.us-east-1.rds.amazonaws.com',
    'database': 'test_phoenix_joao_pessoa'
}

def bd_phoenix(vw_name):
    conexao = mysql.connector.connect(**config)
    cursor = conexao.cursor()
    request_name = f'SELECT * FROM {vw_name}'
    cursor.execute(request_name)
    resultado = cursor.fetchall()
    cabecalho = [desc[0] for desc in cursor.description]
    cursor.close()
    conexao.close()
    df = pd.DataFrame(resultado, columns=cabecalho)
    df = df.applymap(lambda x: float(x) if isinstance(x, decimal.Decimal) else x)
    return df


if not 'df_scales' in st.session_state:
    with st.spinner('Puxando dados do Phoenix...'):
        st.session_state.df_scales = bd_phoenix('vw_scales')

dataframe_escalas = st.session_state.df_scales
st.title('Edição de escala')
st.divider()

uploaded_file = st.file_uploader("Escolha um arquivo")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, delimiter=";")
    st.dataframe(df)

def generate_template():
    data = {
        'Escala': ['Exemplo 1', 'Exemplo 2'],
        'Guia': ['Guia 1', 'Guia 2'],
        'Motorista': ['Motorista 1', 'Motorista 2'],
        'Veiculo': ['Veiculo 1', 'Veiculo 2'],
    }
    df_template = pd.DataFrame(data)
    return df_template

template = generate_template()

csv = template.to_csv(index=False, sep=';')

st.download_button(
    label="Baixar planilha modelo",
    data=csv,
    file_name="planilha_modelo.csv",
    mime="text/csv"
)

BASE_URL_GET = "https://driverjoao_pessoa.phoenix.comeialabs.com/scale/"
BASE_URL_POST = "https://httpbin.org/post"
# BASE_URL_POST = 'https://driverjoao_pessoa.phoenix.comeialabs.com/scale/roadmap/allocate'

def fetch_data(search_query, object):
    params = {"page": 1, "fields": "", "q": search_query}
    try:
        if not search_query:
            params.pop("q")
        response = requests.get(BASE_URL_GET + object, params=params, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Ocorreu um erro: {e}")
        return []

def handle_selection(row, column_name, object_name, dataframe_escala, id_column_name):
    api_data = fetch_data(row[column_name], object_name)
    if not api_data:
        st.warning(f"Nenhum resultado encontrado para o {column_name.lower()} fornecido, será utilizado o {column_name.lower()} já existente na escala.")
        return dataframe_escala[id_column_name].values[0]
    elif len(api_data) > 1:
        if object_name == 'vehicle':
            options = {f"{item['name']} ({item['model']}) - {item['plate']}": item["id"] for item in api_data}
        else:
            options = {f"{item['nickname']} ({item['name']})": item["id"] for item in api_data}
        selected_option = st.selectbox(f"Selecione um {column_name}", options=list(options.keys()))
        return options[selected_option]
    else:
        return api_data[0]['id']

def update_scale(payload):
    try:
        response = requests.post(BASE_URL_POST, json=payload, verify=False)
        response.raise_for_status()
        return 'Escala atualizada com sucesso!'
    except requests.RequestException as e:
        st.error(f"Ocorreu um erro: {e}")
        return 'Erro ao atualizar a escala'

def get_codigo_antigo(reserve_service_id):
    codigo_antigo = dataframe_escalas[
        (dataframe_escalas['ID Servico'] == reserve_service_id) 
    ]
    if codigo_antigo.empty:
        return 'Escala não encontrada'
    return codigo_antigo['Escala'].values[0]

def get_novo_codigo(reserve_service_id):
    novo_codigo = novo_dataframe_escalas[
        (novo_dataframe_escalas['ID Servico'] == reserve_service_id) 
    ]
    if novo_codigo.empty:
        return 'Escala não encontrada'
    return novo_codigo['Escala'].values[0]

st.header('Escalas para edição')
st.divider()

if uploaded_file is not None:
    escalas_para_atualizar = []
    for index, row in df.iterrows():
        dataframe_escala = dataframe_escalas[dataframe_escalas['Escala'] == row['Escala']]
        st.header(f'{dataframe_escala["Escala"].values[0]}')
        st.dataframe(dataframe_escala, hide_index=True)
        id_escala = dataframe_escala['ID Escala'].values[0]
        id_servicos = dataframe_escala['ID Servico'].tolist()
        try:
            id_guia = handle_selection(row, 'Guia', 'guide', dataframe_escala, 'ID Guia')
            id_motorista = handle_selection(row, 'Motorista', 'driver', dataframe_escala, 'ID Motorista')
            id_veiculo = handle_selection(row, 'Veiculo', 'vehicle', dataframe_escala, 'ID Veiculo')
        except Exception as e:
            st.error(f"Ocorreu um erro: {e}")
        
        date_str = dataframe_escala['Data da Escala'].values[0].strftime('%Y-%m-%d')
        codigo_escala = dataframe_escala['Escala'].values[0]
        payload = {
            "date": date_str,
            "vehicle_id": id_veiculo,
            "reserve_service_ids": id_servicos,
            "guide_id": id_guia,
            "driver_id": id_motorista,
            "roadmap_id": id_escala,
            "codigo_antigo": codigo_escala
        }
        guia = dataframe_escalas[dataframe_escalas['ID Guia'] == id_guia]['Guia'].values[0]
        motorista = dataframe_escalas[dataframe_escalas['ID Motorista'] == id_motorista]['Motorista'].values[0]
        veiculo = dataframe_escalas[dataframe_escalas['ID Veiculo'] == id_veiculo]['Veiculo'].values[0]
        st.write(f"Novo guia: {guia}")
        st.write(f"Novo motorista: {motorista}")
        st.write(f"Novo veículo: {veiculo}")
        escalas_para_atualizar.append(payload)
        st.divider()
    
    placeholder = st.empty()
    placeholder.dataframe(escalas_para_atualizar)
    if st.button("Atualizar escalas"):
        for escala in escalas_para_atualizar:
            escala_atual = escala.copy()
            escala_atual.pop('codigo_antigo')
            if escala_atual['guide_id'] == None:
                escala['status'] = 'Erro: Guia não selecionado'
                placeholder.dataframe(escalas_para_atualizar)
                continue
            if escala_atual['driver_id'] == None:
                escala['status'] = 'Erro: Motorista não selecionado'
                placeholder.dataframe(escalas_para_atualizar)
                continue
            if escala_atual['vehicle_id'] == None:
                escala['status'] = 'Erro: Veículo não selecionado'
                placeholder.dataframe(escalas_para_atualizar)
                continue
            status = update_scale(escala_atual)
            escala['status'] = status
            placeholder.dataframe(escalas_para_atualizar)
        novo_dataframe_escalas = bd_phoenix('vw_scales')
        for escala in escalas_para_atualizar:
            novo_codigo = get_novo_codigo(escala['reserve_service_ids'][0])
            escala['novo_codigo'] = novo_codigo
            placeholder.dataframe(escalas_para_atualizar)