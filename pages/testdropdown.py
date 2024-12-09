import streamlit as st
import pandas as pd
import requests

uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.write(df)










# Base URL for the API
BASE_URL = "https://driverjoao_pessoa.phoenix.comeialabs.com/scale/guide"

# Fetch data from the API with a search query
def fetch_data(search_query):
    params = {"page": 1, "fields": "", "q": search_query}
    try:
        if not search_query or search_query == "No results found":
            params.pop("q")
        st.write(params)
        
        req = requests.Request('GET', BASE_URL, params=params)
        prepared = req.prepare()
        st.write(f"Full URL: {prepared.url}")
        
        response = requests.get(BASE_URL, params=params, verify=False)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"An error occurred: {e}")
        return []

# Parse the response data into a dictionary of nicknames and IDs
def parse_nicknames_and_ids(data):
    return {item["nickname"]: item["id"] for item in data}

# Streamlit app
st.title("Dynamic Nickname Selector")

# Text input for search query
search_query = st.text_input("Search for a nickname", value="", key="search_query")

# Fetch data dynamically based on the search query
data = fetch_data(search_query)
nicknames_and_ids = parse_nicknames_and_ids(data) if data else {}

# Ensure there is always an option to display
options = list(nicknames_and_ids.keys()) or ["No results found"]

# Selectbox with search functionality
selected_nickname = st.selectbox(
    "Select a nickname",
    options=options,
    format_func=lambda x: x if x != "No results found" else "",
)

# Display and handle submission
if selected_nickname and selected_nickname != "No results found":
    selected_id = nicknames_and_ids[selected_nickname]
    if st.button("Submit"):
        st.success(f"Selected Nickname: {selected_nickname}, ID: {selected_id}")
        # Add backend logic here if needed (e.g., sending the ID to a server)
else:
    st.warning("Please type and select a valid nickname.")