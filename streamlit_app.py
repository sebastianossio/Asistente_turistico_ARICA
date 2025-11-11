import streamlit as st
import openai
import os

# streamlit_app.py

import streamlit as st
import pandas as pd
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
    {"nombre": "Morro de Arica", "lat": -18.477, "lon": -70.330, "tiempo": 1.5,
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/2/2c/Morro_de_Arica.jpg"},
    {"nombre": "Playa El Laucho", "lat": -18.486, "lon": -70.318, "tiempo": 2,
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Playa_El_Laucho_Arica.jpg"},
    {"nombre": "Cuevas de Anzota", "lat": -18.533, "lon": -70.353, "tiempo": 1.5,
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Cuevas_de_Anzota.jpg"},
    {"nombre": "Playa Chinchorro", "lat": -18.466, "lon": -70.307, "tiempo": 2.5,
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/3/3c/Playa_Chinchorro_Arica.jpg"},
    {"nombre": "Museo de Sitio Colón 10", "lat": -18.480, "lon": -70.317, "tiempo": 1,
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/8/8c/Museo_de_Sitio_Colon_10_Arica.jpg"},
    {"nombre": "Humedal del Río Lluta", "lat": -18.425, "lon": -70.324, "tiempo": 2,
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/1/1e/Humedal_del_Rio_Lluta_Arica.jpg"},
    {"nombre": "Putre", "lat": -18.195, "lon": -69.559, "tiempo": 3,
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Putre_village.jpg"},
    {"nombre": "Parque Nacional Lauca", "lat": -18.243, "lon": -69.352, "tiempo": 4,
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/2/2c/Parque_Nacional_Lauca_Chile.jpg"},
    {"nombre": "Lago Chungará", "lat": -18.25, "lon": -69.15, "tiempo": 2,
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/5/5c/Lago_Chungara.jpg"},
    {"nombre": "Salar de Surire", "lat": -18.85, "lon": -69.05, "tiempo": 3.5,
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/7/74/Salar_de_Surire.jpg"}
]

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

    # Portada
    pdf.add_page()
    pdf.set_fill_color(0, 102, 204)
    pdf.rect(0, 0, 210, 40, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 20, "Itinerario Turístico - Arica y Parinacota", ln=True, align="C")
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)

    # Cuerpo del itinerario
    for dia, lugares in itinerario.items():
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 12, dia, ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.ln(4)
        for i, lugar in enumerate(lugares):
            pdf.multi_cell(0, 8, f"• {lugar['nombre']} (Tiempo estimado: {lugar['tiempo']} hrs)")
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
                pdf.multi_cell(0, 8, f"   ↳ Distancia al siguiente: {dist:.1f} km")
            pdf.ln(8)
        pdf.ln(6)

    # Pie
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Visita Arica y Parinacota - Naturaleza, cultura y aventura.", ln=True, align="C")

    filename = "/mount/data/Itinerario_Turistico_Arica.pdf"
    pdf.output(filename)
    return filename

# ---------- INTERFAZ STREAMLIT ---------- #
st.title("🌅 App Turística - Arica y Parinacota")
st.markdown("Planifica tu viaje por la región de la eterna primavera 🌞")

st.sidebar.header("🧭 Configura tu viaje")
dias = st.sidebar.slider("Días de visita", 1, 7, 3)
seleccionados = st.sidebar.multiselect(
    "Selecciona los atractivos turísticos:",
    [d["nombre"] for d in destinos],
    default=["Morro de Arica", "Playa El Laucho", "Cuevas de Anzota"]
)

if seleccionados:
    destinos_seleccionados = [d for d in destinos if d["nombre"] in seleccionados]
    itinerario = generar_itinerario_por_cercania(destinos_seleccionados, dias)

    # Mapa general
    st.subheader("🗺️ Mapa de tu ruta turística")
    mapa = folium.Map(location=[-18.48, -70.32], zoom_start=9)
    for d in destinos_seleccionados:
        folium.Marker([d["lat"], d["lon"]], popup=d["nombre"]).add_to(mapa)
    st_folium(mapa, width=700, height=450)

    # Itinerario
    st.subheader("🗓️ Itinerario sugerido por cercanía")
    for dia, lugares in itinerario.items():
        st.markdown(f"### {dia}")
        cols = st.columns(len(lugares))
        for i, lugar in enumerate(lugares):
            with cols[i]:
                st.image(lugar["imagen"], caption=lugar["nombre"], use_container_width=True)
                st.markdown(f"🕓 {lugar['tiempo']} horas")

        st.divider()

    # Ruta Google Maps
    ruta_url = generar_link_google_maps(destinos_seleccionados)
    st.markdown(f"🚗 [Ver ruta completa en Google Maps]({ruta_url})", unsafe_allow_html=True)

    # PDF con imágenes
    if st.button("📄 Generar PDF con imágenes"):
        pdf_path = generar_pdf(itinerario)
        with open(pdf_path, "rb") as f:
            st.download_button("Descargar Itinerario en PDF", f, file_name="Itinerario_Turistico_Arica.pdf")

else:
    st.info("Selecciona al menos un atractivo turístico para generar tu itinerario.")


