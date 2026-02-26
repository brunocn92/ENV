import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Formulário com Mapa", layout="wide")

st.title("📍 Coleta de Localização e Respostas")

# 1. Criar o Mapa Interativo
'''st.subheader("Selecione a localização no mapa")
m = folium.Map(location=[-22.969208, -43.179623], zoom_start=13)''' # Começa em Copa'''
# Em vez de usar folium, use o mapa nativo do streamlit
st.subheader("Selecione a localização no mapa")

# Mapa nativo do Streamlit (não requer folium)
map_data = pd.DataFrame({
    'lat': [-23.5505],
    'lon': [-46.6333]
})

# Exibe mapa interativo
st.map(map_data, zoom=13)

# Nota: O mapa nativo do Streamlit não permite clicar para pegar coordenadas
# diretamente sem folium. Se precisar do clique, teremos que usar outra abordagem.
# Captura o clique no mapa
mapa_interativo = st_folium(m, width=700, height=450, returned_objects=["last_object_clicked"])

# Variáveis para armazenar a lat/long clicada
lat = None
lon = None

if mapa_interativo["last_object_clicked"]:
    lat = mapa_interativo["last_object_clicked"]["lat"]
    lon = mapa_interativo["last_object_clicked"]["lng"]
    st.success(f"Local selecionado: {lat}, {lon}")
else:
    st.warning("Clique no mapa para definir o pino.")

# 2. Formulário de Respostas
st.subheader("Preencha os dados")
with st.form("formulario_dados"):
    nome = st.text_input("Nome")
    resposta = st.text_area("Sua Resposta")
    
    # Campos ocultos ou preenchidos automaticamente com a localização
    # O usuário vê, mas não edita (ou edita se quiser refinar)
    col1, col2 = st.columns(2)
    with col1:
        lat_input = st.number_input("Latitude", value=lat, format="%.6f")
    with col2:
        lon_input = st.number_input("Longitude", value=lon, format="%.6f")
    
    enviado = st.form_submit_button("Enviar Resposta")

# 3. Lógica de Salvamento
if enviado:
    if lat_input and lon_input and nome:
        # Criar um DataFrame com os dados
        novo_dado = {
            "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Nome": nome,
            "Resposta": resposta,
            "Latitude": lat_input,
            "Longitude": lon_input
        }
        
        # Salvar em CSV (persistência simples)
        df_novo = pd.DataFrame([novo_dado])
        if not os.path.isfile("dados_coletados.csv"):
            df_novo.to_csv("dados_coletados.csv", index=False)
        else:
            df_novo.to_csv("dados_coletados.csv", mode='a', header=False, index=False)
            
        st.balloons()
        st.success("Dados enviados com sucesso!")
    else:
        st.error("Por favor, selecione um local no mapa e preencha o nome.")

# 4. Visualizar dados salvos (Opcional)
if st.checkbox("Ver dados coletados"):
    if os.path.isfile("dados_coletados.csv"):
        df = pd.read_csv("dados_coletados.csv")
        st.dataframe(df)
    else:
        st.info("Nenhum dado coletado ainda.")
