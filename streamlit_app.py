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
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import requests
from PIL import Image as PILImage

# --- Datos con URLs de las primeras fotos que entregué ---
atractivos = [
    {"nombre": "Playa Chinchorro", "lat": -18.4726, "lon": -70.3128, "tiempo": 2,
     "descripcion": "Amplia playa urbana ideal para nadar y disfrutar del sol.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/b/b9/Playa_Chinchorro_Arica.jpg"},
     
    {"nombre": "Playa El Laucho", "lat": -18.4872, "lon": -70.3232, "tiempo": 1.5,
     "descripcion": "Playa céntrica de aguas calmadas, ideal para familias.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Playa_El_Laucho_Arica.jpg"},

    {"nombre": "Morro de Arica", "lat": -18.4806, "lon": -70.3273, "tiempo": 2,
     "descripcion": "Histórico morro con museo y mirador panorámico.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/8/8d/Morro_de_Arica.jpg"},

    {"nombre": "Museo de Sitio Colón 10", "lat": -18.4770, "lon": -70.3183, "tiempo": 1.5,
     "descripcion": "Museo con las momias más antiguas del mundo, cultura Chinchorro.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/f/f3/Museo_de_Sitio_Col%C3%B3n_10_-_Arica.jpg"},

    {"nombre": "Humedal del Río Lluta", "lat": -18.4395, "lon": -70.3170, "tiempo": 1.5,
     "descripcion": "Santuario de aves migratorias con senderos y miradores naturales.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/b/bd/Humedal_del_R%C3%ADo_Lluta_-_Arica.jpg"},

    {"nombre": "Valle de Azapa", "lat": -18.481, "lon": -70.308, "tiempo": 2,
     "descripcion": "Famoso valle de olivos y cultura agrícola.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Valle_de_Azapa.jpg"},

    {"nombre": "Putre", "lat": -18.1977, "lon": -69.5593, "tiempo": 3,
     "descripcion": "Encantador pueblo altiplánico y base para visitar el Parque Lauca.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Putre_-_Chile.jpg"},

    {"nombre": "Parque Nacional Lauca", "lat": -18.2333, "lon": -69.1667, "tiempo": 4,
     "descripcion": "Paisajes de altura con lagos y volcanes.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/1/1d/Lago_Chungara_y_volcan_Parinacota.jpg"},

    {"nombre": "Termas de Jurasi", "lat": -18.2255, "lon": -69.5250, "tiempo": 2,
     "descripcion": "Piscinas naturales de aguas termales cerca de Putre.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/5/57/Termas_de_Jurasi_Putre.jpg"},

    {"nombre": "Socoroma", "lat": -18.2242, "lon": -69.5870, "tiempo": 2,
     "descripcion": "Pintoresco pueblo precordillerano con arquitectura tradicional.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/b/b9/Socoroma_Arica_y_Parinacota.jpg"},

    {"nombre": "Cuevas de Anzota", "lat": -18.5358, "lon": -70.3511, "tiempo": 1.5,
     "descripcion": "Formaciones rocosas y miradores junto al mar.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/7/7d/Cuevas_de_Anzota_-_Arica.jpg"},

    {"nombre": "Salar de Surire", "lat": -19.366, "lon": -69.383, "tiempo": 3,
     "descripcion": "Salar con flamencos y geografía única.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/5/57/Salar_de_Surire.jpg"},

    {"nombre": "Camarones", "lat": -18.200, "lon": -70.500, "tiempo": 2,
     "descripcion": "Pueblo costero tradicional, conocido por su gastronomía.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Camarones_Arica.jpg"},

    {"nombre": "Geoglifos de Lluta", "lat": -18.2, "lon": -70.3, "tiempo": 1.5,
     "descripcion": "Antiguos geoglifos prehispánicos visibles desde miradores.",
     "imagen_url": "https://images.visitchile.com/destinos/283_6702_la_ruta_altiplanca.jpg"}
]

# --- Funciones ---
def distancia(a, b):
    return geodesic((a["lat"], a["lon"]), (b["lat"], b["lon"])).km

def agrupar_por_dia(destinos, dias):
    if dias >= len(destinos):
        return [[d] for d in destinos]
    grupos = [[] for _ in range(dias)]
    destinos = sorted(destinos, key=lambda x: (x["lat"], x["lon"]))
    for idx, d in enumerate(destinos):
        grupos[idx % dias].append(d)
    for i, grupo in enumerate(grupos):
        if len(grupo) > 1:
            ordenado = [grupo[0]]
            resto = grupo[1:]
            while resto:
                last = ordenado[-1]
                next_dest = min(resto, key=lambda x: distancia(last, x))
                ordenado.append(next_dest)
                resto.remove(next_dest)
            grupos[i] = ordenado
    return grupos

def generar_itinerario_por_dia(destinos, dias):
    grupos = agrupar_por_dia(destinos, dias)
    itinerario = []
    for i, dia_grupo in enumerate(grupos):
        for d in dia_grupo:
            itinerario.append({
                "Día": i+1,
                "Destino": d["nombre"],
                "Descripción": d["descripcion"],
                "Tiempo estimado (h)": d["tiempo"],
                "lat": d["lat"],
                "lon": d["lon"],
                "imagen_url": d["imagen_url"]
            })
    return itinerario

def generar_pdf(itinerario):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elementos = [Paragraph("Itinerario Turístico - Arica y Parinacota", styles['Title']), Spacer(1,12)]
    itinerario = sorted(itinerario, key=lambda x: x["Día"])
    for item in itinerario:
        elementos.append(Paragraph(f"Día {item['Día']}: {item['Destino']} ({item['Tiempo estimado (h)']}h)", styles['Heading2']))
        elementos.append(Paragraph(item['Descripción'], styles['BodyText']))
        try:
            # Cargar imagen desde URL
            response = requests.get(item["imagen_url"])
            img_pil = PILImage.open(BytesIO(response.content))
            img_pil.save(f"/tmp/{item['Destino']}.png")
            elementos.append(Image(f"/tmp/{item['Destino']}.png", width=400, height=300))
        except:
            elementos.append(Paragraph("Imagen no disponible", styles['BodyText']))
        elementos.append(Spacer(1,12))
    ruta_texto = " -> ".join([i['Destino'] for i in itinerario])
    elementos.append(Paragraph(f"Ruta sugerida: {ruta_texto}", styles['Normal']))
    doc.build(elementos)
    buffer.seek(0)
    return buffer

# --- Interfaz Streamlit ---
st.set_page_config(page_title="Asistente Turístico Arica y Parinacota", layout="wide")
st.title("🏔️ Asistente Turístico")
dias = st.number_input("Cantidad de días de visita", min_value=1, max_value=10, value=3)

st.subheader("Atractivos Turísticos")
seleccionados = []
cols = st.columns(2)
for i, a in enumerate(atractivos):
    with cols[i % 2]:
        try:
            response = requests.get(a["imagen_url"])
            img_pil = PILImage.open(BytesIO(response.content))
            st.image(img_pil, caption=a["nombre"], use_column_width=True)
        except:
            st.text(a["nombre"])
        if st.checkbox(f"Seleccionar: {a['nombre']}", key=a["nombre"]):
            seleccionados.append(a)

if st.button("Generar Itinerario"):
    if not seleccionados:
        st.warning("Selecciona al menos un destino.")
    else:
        itinerario = generar_itinerario_por_dia(seleccionados,dias)
        st.dataframe(pd.DataFrame(itinerario))
        # Mapa
        mapa = folium.Map(location=[-18.48, -70.32], zoom_start=8)
        line_coords = []
        for dest in itinerario:
            folium.Marker([dest["lat"], dest["lon"]], popup=dest["Destino"], tooltip=dest["Destino"]).add_to(mapa)
            line_coords.append((dest["lat"], dest["lon"]))
        if len(line_coords) > 1:
            PolyLine(line_coords,color="blue",weight=3).add_to(mapa)
        st.components.v1.html(mapa._repr_html_(), height=500)
        # PDF
        pdf_buffer = generar_pdf(itinerario)
        st.download_button("📄 Descargar PDF con fotos y ruta", pdf_buffer, "itinerario_arica.pdf")

