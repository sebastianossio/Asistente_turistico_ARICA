import streamlit as st
import openai
import os

# Configura tu API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

import streamlit as st
import pandas as pd
import folium
from folium import PolyLine
from geopy.distance import geodesic
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from googletrans import Translator
from itertools import permutations
import urllib.parse
import openai
import os

# --- Configurar OpenAI ---
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- Traductor ---
translator = Translator()

# --- Datos de atractivos turísticos ---
atractivos = [
    {"nombre": "Playa Chinchorro", "lat": -18.4726, "lon": -70.3128, "tiempo": 2, "descripcion": "Amplia playa urbana ideal para nadar y disfrutar del sol.", "imagen_local": "chinchorro.jpg"},
    {"nombre": "Playa El Laucho", "lat": -18.4872, "lon": -70.3232, "tiempo": 1.5, "descripcion": "Playa céntrica de aguas calmadas, ideal para familias.", "imagen_local": "el_laucho.jpg"},
    {"nombre": "Morro de Arica", "lat": -18.4806, "lon": -70.3273, "tiempo": 2, "descripcion": "Histórico morro con museo y mirador panorámico.", "imagen_local": "morro_arica.jpg"},
    {"nombre": "Museo de Sitio Colón 10", "lat": -18.4770, "lon": -70.3183, "tiempo": 1.5, "descripcion": "Museo con las momias más antiguas del mundo, cultura Chinchorro.", "imagen_local": "museo_colon10.jpg"},
    {"nombre": "Humedal del Río Lluta", "lat": -18.4395, "lon": -70.3170, "tiempo": 1.5, "descripcion": "Santuario de aves migratorias con senderos y miradores naturales.", "imagen_local": "humedal_lluta.jpg"},
    {"nombre": "Valle de Azapa", "lat": -18.481, "lon": -70.308, "tiempo": 2, "descripcion": "Famoso valle de olivos y cultura agrícola.", "imagen_local": "valle_azapa.jpg"},
    {"nombre": "Putre", "lat": -18.1977, "lon": -69.5593, "tiempo": 3, "descripcion": "Encantador pueblo altiplánico y base para visitar el Parque Lauca.", "imagen_local": "putre.jpg"},
    {"nombre": "Parque Nacional Lauca", "lat": -18.2333, "lon": -69.1667, "tiempo": 4, "descripcion": "Paisajes de altura con lagos y volcanes.", "imagen_local": "parque_lauca.jpg"},
    {"nombre": "Termas de Jurasi", "lat": -18.2255, "lon": -69.5250, "tiempo": 2, "descripcion": "Piscinas naturales de aguas termales cerca de Putre.", "imagen_local": "termas_jurasi.jpg"},
    {"nombre": "Socoroma", "lat": -18.2242, "lon": -69.5870, "tiempo": 2, "descripcion": "Pintoresco pueblo precordillerano con arquitectura tradicional.", "imagen_local": "socoroma.jpg"},
    {"nombre": "Cuevas de Anzota", "lat": -18.5358, "lon": -70.3511, "tiempo": 1.5, "descripcion": "Formaciones rocosas y miradores junto al mar.", "imagen_local": "cuevas_anzota.jpg"},
    {"nombre": "Salar de Surire", "lat": -19.366, "lon": -69.383, "tiempo": 3, "descripcion": "Salar con flamencos y geografía única.", "imagen_local": "salar_surire.jpg"},
    {"nombre": "Camarones", "lat": -18.200, "lon": -70.500, "tiempo": 2, "descripcion": "Pueblo costero tradicional, conocido por su gastronomía.", "imagen_local": "camarones.jpg"}
]

# --- Funciones ---
def distancia(a, b):
    return geodesic((a["lat"], a["lon"]), (b["lat"], b["lon"])).km

def ordenar_por_distancia(destinos):
    if len(destinos) <= 1: return destinos
    min_dist = float("inf")
    mejor_ruta = destinos
    for perm in permutations(destinos):
        d = sum(distancia(perm[i], perm[i+1]) for i in range(len(perm)-1))
        if d < min_dist:
            min_dist = d
            mejor_ruta = perm
    return list(mejor_ruta)

def generar_itinerario_optimizado(destinos, dias):
    if not destinos: return []
    ruta = ordenar_por_distancia(destinos)
    itinerario = []
    for idx, d in enumerate(ruta):
        dia = (idx % dias) + 1
        itinerario.append({
            "Día": dia,
            "Destino": d["nombre"],
            "Descripción": d["descripcion"],
            "Tiempo estimado (h)": d["tiempo"],
            "lat": d["lat"],
            "lon": d["lon"],
            "imagen_local": d["imagen_local"]
        })
    return itinerario

def generar_pdf_con_fotos(itinerario):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elementos = [Paragraph("Itinerario Turístico - Arica y Parinacota", styles['Title']), Spacer(1,12)]

    # Ordenar por día
    itinerario = sorted(itinerario, key=lambda x: x["Día"])

    for item in itinerario:
        elementos.append(Paragraph(f"Día {item['Día']}: {item['Destino']} ({item['Tiempo estimado (h)']}h)", styles['Heading2']))
        elementos.append(Paragraph(item['Descripción'], styles['BodyText']))
        # Agregar imagen
        try:
            img = Image(f"./imagenes/{item['imagen_local']}", width=400, height=300)
            elementos.append(img)
        except:
            pass
        elementos.append(Spacer(1,12))
    
    # Agregar ruta
    ruta_texto = " -> ".join([i['Destino'] for i in itinerario])
    elementos.append(Paragraph(f"Ruta sugerida: {ruta_texto}", styles['Normal']))
    
    doc.build(elementos)
    buffer.seek(0)
    return buffer

# --- Interfaz Streamlit ---
st.set_page_config(page_title="Asistente Turístico Arica y Parinacota", layout="wide")
st.title("🏔️ Asistente Turístico")
st.markdown("Selecciona tus destinos, genera itinerario con fotos y PDF, y visualiza la ruta en el mapa.")

# --- Selección de destinos ---
dias = st.number_input("Cantidad de días de visita", min_value=1, max_value=10, value=3)
st.subheader("Atractivos Turísticos")
seleccionados = []
cols = st.columns(2)
for i, a in enumerate(atractivos):
    with cols[i % 2]:
        st.image(f"./imagenes/{a['imagen_local']}", caption=a["nombre"], use_container_width=True)
        if st.checkbox(f"Seleccionar: {a['nombre']}", key=a["nombre"]):
            seleccionados.append(a)

# --- Generar itinerario ---
if st.button("Generar Itinerario"):
    if not seleccionados: st.warning("Selecciona al menos un destino.")
    else:
        itinerario = generar_itinerario_optimizado(seleccionados,dias)
        df = pd.DataFrame(itinerario)
        st.dataframe(df)

        # Mapa
        mapa = folium.Map(location=[-18.48, -70.32], zoom_start=8)
        line_coords = []
        for dest in itinerario:
            folium.Marker([dest["lat"], dest["lon"]], popup=dest["Destino"], tooltip=dest["Destino"]).add_to(mapa)
            line_coords.append((dest["lat"], dest["lon"]))
        if len(line_coords)>1: PolyLine(line_coords,color="blue",weight=3).add_to(mapa)
        st.components.v1.html(mapa._repr_html_(), height=500)

        # PDF
        pdf_buffer = generar_pdf_con_fotos(itinerario)
        st.download_button("📄 Descargar PDF con fotos y ruta", pdf_buffer, "itinerario_arica.pdf")
