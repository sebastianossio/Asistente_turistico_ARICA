import streamlit as st
import openai
import os

# streamlit_app.py

import streamlit as st
from geopy.distance import geodesic
from fpdf import FPDF
import math
import folium
from streamlit_folium import st_folium
import requests
from PIL import Image
from io import BytesIO

# ---------- CONFIGURACIÓN DE LA APP ---------- #
st.set_page_config(page_title="App Turística - Arica y Parinacota", layout="wide")

# ---------- DATOS DE LOS DESTINOS ---------- #
destinos = [
    {"nombre": "Morro de Arica", "lat": -18.477, "lon": -70.330, "tipo": "Cultura", "tiempo": 1.5,
     "region": "Ciudad", "descripcion": "Icono histórico con vista panorámica de la ciudad.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/2/2c/Morro_de_Arica.jpg"},

    {"nombre": "Playa El Laucho", "lat": -18.486, "lon": -70.318, "tipo": "Playa", "tiempo": 2,
     "region": "Costa", "descripcion": "Playa tranquila ideal para relajarse y tomar sol.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Playa_El_Laucho_Arica.jpg"},

    {"nombre": "Cuevas de Anzota", "lat": -18.533, "lon": -70.353, "tipo": "Naturaleza", "tiempo": 1.5,
     "region": "Costa", "descripcion": "Cuevas naturales con formaciones rocosas únicas.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Cuevas_de_Anzota.jpg"},

    {"nombre": "Playa Chinchorro", "lat": -18.466, "lon": -70.307, "tipo": "Playa", "tiempo": 2.5,
     "region": "Costa", "descripcion": "Famosa playa con actividades de pesca y deportes acuáticos.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/3/3c/Playa_Chinchorro_Arica.jpg"},

    {"nombre": "Museo de Sitio Colón 10", "lat": -18.480, "lon": -70.317, "tipo": "Cultura", "tiempo": 1,
     "region": "Ciudad", "descripcion": "Museo arqueológico con vestigios de culturas prehispánicas.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/8/8c/Museo_de_Sitio_Colon_10_Arica.jpg"},

    {"nombre": "Humedal del Río Lluta", "lat": -18.425, "lon": -70.324, "tipo": "Naturaleza", "tiempo": 2,
     "region": "Valle", "descripcion": "Ecosistema protegido, ideal para observación de aves.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/1/1e/Humedal_del_Rio_Lluta_Arica.jpg"},

    {"nombre": "Putre", "lat": -18.195, "lon": -69.559, "tipo": "Cultura", "tiempo": 3,
     "region": "Altiplano", "descripcion": "Pueblo tradicional a orillas del altiplano con cultura Aymara.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Putre_village.jpg"},

    {"nombre": "Parque Nacional Lauca", "lat": -18.243, "lon": -69.352, "tipo": "Naturaleza", "tiempo": 4,
     "region": "Altiplano", "descripcion": "Parque con volcanes, lagunas y fauna típica de la zona.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/2/2c/Parque_Nacional_Lauca_Chile.jpg"},

    {"nombre": "Lago Chungará", "lat": -18.25, "lon": -69.15, "tipo": "Naturaleza", "tiempo": 2,
     "region": "Altiplano", "descripcion": "Lago a gran altitud con vistas espectaculares y flamencos.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/5/5c/Lago_Chungara.jpg"},

    {"nombre": "Salar de Surire", "lat": -18.85, "lon": -69.05, "tipo": "Naturaleza", "tiempo": 3.5,
     "region": "Altiplano", "descripcion": "Salar impresionante con fauna típica del altiplano.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/7/74/Salar_de_Surire.jpg"}
]

# Colores por sección
colores_region = {
    "Ciudad": "#FFA07A",
    "Costa": "#87CEEB",
    "Valle": "#98FB98",
    "Altiplano": "#DDA0DD"
}

# ---------- FUNCIONES AUXILIARES ---------- #
def calcular_distancia(d1, d2):
    return geodesic((d1["lat"], d1["lon"]), (d2["lat"], d2["lon"])).km

def generar_itinerario_por_cercania(destinos_seleccionados, dias):
    itinerario = {f"Día {i+1}": [] for i in range(dias)}
    if not destinos_seleccionados:
        return itinerario
    pendientes = destinos_seleccionados.copy()
    dia = 0
    actual = pendientes.pop(0)
    while pendientes:
        itinerario[f"Día {dia+1}"].append(actual)
        if len(itinerario[f"Día {dia+1}"]) >= math.ceil(len(destinos_seleccionados) / dias):
            dia = (dia + 1) % dias
        siguiente = min(pendientes, key=lambda x: calcular_distancia(actual, x))
        pendientes.remove(siguiente)
        actual = siguiente
    itinerario[f"Día {dia+1}"].append(actual)
    return itinerario

def generar_link_google_maps(destinos_seleccionados):
    base_url = "https://www.google.com/maps/dir/"
    for d in destinos_seleccionados:
        base_url += f"{d['lat']},{d['lon']}/"
    return base_url

def generar_pdf(itinerario):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 20, "Itinerario Turístico - Arica y Parinacota", ln=True, align="C")

    for dia, lugares in itinerario.items():
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, dia, ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.ln(5)
        for i, lugar in enumerate(lugares):
            color = colores_region.get(lugar["region"], "#FFFFFF")
            pdf.set_fill_color(int(color[1:3],16), int(color[3:5],16), int(color[5:7],16))
            pdf.multi_cell(0, 8, f"{lugar['nombre']} ({lugar['tipo']}) - {lugar['tiempo']} hrs\n{lugar['descripcion']}", fill=True)
            try:
                response = requests.get(lugar["imagen"])
                img = Image.open(BytesIO(response.content))
                img_path = f"/tmp/{lugar['nombre']}.jpg"
                img.save(img_path)
                pdf.image(img_path, w=90)
            except:
                pass
            if i < len(lugares) - 1:
                dist = calcular_distancia(lugares[i], lugares[i+1])
                pdf.multi_cell(0, 8, f"Distancia al siguiente: {dist:.1f} km")
            pdf.ln(5)
        pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Visita Arica y Parinacota - Naturaleza, cultura y aventura.", ln=True, align="C")
    filename = "/mount/data/Itinerario_Turistico_Arica.pdf"
    pdf.output(filename)
    return filename

# ---------- INTERFAZ STREAMLIT ---------- #
st.title("🌅 Guía Turística - Arica y Parinacota")
st.markdown("Explora la región de la eterna primavera con itinerarios personalizados por secciones geográficas.")

st.sidebar.header("🧭 Configura tu viaje")
dias = st.sidebar.slider("Días de visita", 1, 7, 3)

# Mostrar atracciones por sección como "tarjetas"
destinos_seleccionados = []
for seccion in ["Ciudad", "Costa", "Valle", "Altiplano"]:
    st.subheader(f"{seccion}")
    cols = st.columns(3)
    for i, lugar in enumerate([d for d in destinos if d["region"] == seccion]):
        with cols[i % 3]:
            st.markdown(f"<div style='background-color:{colores_region[seccion]};padding:10px;border-radius:10px;'>", unsafe_allow_html=True)
            st.image(lugar["imagen"], use_container_width=True)
            st.markdown(f"**{lugar['nombre']}** ({lugar['tipo']})")
            st.markdown(f"🕓 {lugar['tiempo']} hrs")
            st.markdown(f"📖 {lugar['descripcion']}")
            if st.checkbox(f"Añadir al itinerario", key=lugar["nombre"]):
                destinos_seleccionados.append(lugar)
            st.markdown("</div>", unsafe_allow_html=True)

if destinos_seleccionados:
    itinerario = generar_itinerario_por_cercania(destinos_seleccionados, dias)

    st.subheader("🗺️ Mapa de tu ruta turística")
    mapa = folium.Map(location=[-18.48, -70.32], zoom_start=9)
    for d in destinos_seleccionados:
        folium.Marker([d["lat"], d["lon"]], popup=d["nombre"]).add_to(mapa)
    st_folium(mapa, width=700, height=450)

    st.subheader("🗓️ Itinerario sugerido")
    for dia, lugares in itinerario.items():
        st.markdown(f"### {dia}")
        cols = st.columns(len(lugares))
        for i, lugar in enumerate(lugares):
            with cols[i]:
                st.image(lugar["imagen"], use_container_width=True)
                st.markdown(f"**{lugar['nombre']}**")
                st.markdown(f"🕓 {lugar['tiempo']} hrs")
                st.markdown(f"📖 {lugar['descripcion']}")
        st.divider()

    ruta_url = generar_link_google_maps(destinos_seleccionados)
    st.markdown(f"🚗 [Ver ruta completa en Google Maps]({ruta_url})", unsafe_allow_html=True)

    if st.button("📄 Generar PDF con imágenes"):
        pdf_path = generar_pdf(itinerario)
        with open(pdf_path, "rb") as f:
            st.download_button("Descargar Itinerario en PDF", f, file_name="Itinerario_Turistico_Arica.pdf")
else:
    st.info("Selecciona al menos un atractivo turístico para generar tu itinerario.")
