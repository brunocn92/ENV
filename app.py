import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Formulário com Mapa", layout="wide")

st.title("📍 Coleta de Localização e Respostas")

# Inicializar variáveis de sessão para coordenadas (Padrão: São Paulo)
if 'lat' not in st.session_state:
    st.session_state.lat = -23.5505
if 'lon' not in st.session_state:
    st.session_state.lon = -46.6333

# 1. Mapa Interativo com Clique (Leaflet.js via HTML)
st.subheader("1. Clique no mapa para selecionar a localização")

st.markdown("""
    <style>
    #map-container {
        height: 400px;
        width: 100%;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    }
    </style>
    <div id="map-container"></div>
    <p style="text-align: center; color: #666;">👆 Clique em qualquer lugar do mapa para colocar o pino</p>
""", unsafe_allow_html=True)

# Componente HTML/JS com Leaflet
st.components.v1.html("""
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    
    <div id="map" style="height: 400px; width: 100%;"></div>
    
    <script>
        // Inicializa o mapa
        var map = L.map('map').setView([-23.5505, -46.6333], 13);
        
        // Adiciona camada do OpenStreetMap (Gratuito)
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap'
        }).addTo(map);
        
        // Variável para armazenar o marcador
        var marker = null;
        
        // Função para atualizar o Streamlit com as coordenadas
        function updateStreamlit(lat, lon) {
            window.parent.postMessage({
                type: "location_update",
                latitude: lat,
                longitude: lon
            }, "*");
        }
        
        // Evento de clique no mapa
        map.on('click', function(e) {
            var lat = e.latlng.lat;
            var lon = e.latlng.lng;
            
            // Remove marcador anterior se existir
            if (marker) {
                map.removeLayer(marker);
            }
            
            // Adiciona novo marcador
            marker = L.marker([lat, lon]).addTo(map);
            
            // Envia coordenadas para o Python
            updateStreamlit(lat, lon);
        });
        
        // Adiciona marcador inicial
        marker = L.marker([-23.5505, -46.6333]).addTo(map);
    </script>
""", height=450)

# Capturar dados do JavaScript (Streamlit não lê postMessage diretamente de forma simples)
# Por isso, usamos inputs numéricos que o usuário pode ver/ajustar
st.info("💡 As coordenadas abaixo são atualizadas quando você clica no mapa. Se necessário, ajuste manualmente.")

col1, col2 = st.columns(2)
with col1:
    lat_input = st.number_input("Latitude", value=st.session_state.lat, format="%.6f", key="lat_input")
with col2:
    lon_input = st.number_input("Longitude", value=st.session_state.lon, format="%.6f", key="lon_input")

# Atualiza session state com os valores dos inputs
st.session_state.lat = lat_input
st.session_state.lon = lon_input

# 2. Exibir Confirmação da Localização
st.subheader("2. Visualizar Localização Selecionada")
map_data = pd.DataFrame({
    'lat': [st.session_state.lat],
    'lon': [st.session_state.lon]
})
st.map(map_data, zoom=13)
st.caption(f"📍 Coordenadas: {st.session_state.lat}, {st.session_state.lon}")

# 3. Formulário de Respostas
st.subheader("3. Preencha os Dados")

with st.form("formulario_dados"):
    nome = st.text_input("Nome")
    resposta = st.text_area("Sua Resposta")
    
    col1, col2 = st.columns(2)
    with col1:
        lat_final = st.number_input("Latitude Final", value=st.session_state.lat, format="%.6f", key="lat_form")
    with col2:
        lon_final = st.number_input("Longitude Final", value=st.session_state.lon, format="%.6f", key="lon_form")
    
    enviado = st.form_submit_button("Enviar Resposta")

# 4. Lógica de Salvamento
if enviado:
    if nome:
        novo_dado = {
            "Data": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Nome": nome,
            "Resposta": resposta,
            "Latitude": lat_final,
            "Longitude": lon_final
        }
        
        df_novo = pd.DataFrame([novo_dado])
        if not os.path.isfile("dados_coletados.csv"):
            df_novo.to_csv("dados_coletados.csv", index=False)
        else:
            df_novo.to_csv("dados_coletados.csv", mode='a', header=False, index=False)
            
        st.balloons()
        st.success("✅ Dados enviados com sucesso!")
    else:
        st.error("⚠️ Por favor, preencha pelo menos o nome.")

# 5. Visualizar dados salvos
st.divider()
if st.checkbox("Ver dados coletados (sessão atual)"):
    if os.path.isfile("dados_coletados.csv"):
        df = pd.read_csv("dados_coletados.csv")
        st.dataframe(df)
    else:
        st.info("Nenhum dado coletado ainda.")
