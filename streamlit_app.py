import streamlit as st
from openai import OpenAI
ip install folium streamlit pandas geopy reportlab
import streamlit as st
import pandas as pd
import math
import folium
from streamlit_folium import st_folium
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime, timedelta
import io
import openai
import os

# ===========================
# CONFIGURACIÓN DE LA APP
# ===========================
st.set_page_config(page_title="Chatbot Turístico - Arica y Parinacota 🌄", layout="wide")
st.title("🤖 Chatbot Turístico - Región de Arica y Parinacota 🌋")
st.markdown("Planifica tu visita seleccionando los atractivos turísticos que desees visitar. El itinerario se optimizará automáticamente según la cercanía de los destinos y los días disponibles.")

# ===========================
# FUNCIONES AUXILIARES
# ===========================
def haversine(lat1, lon1, lat2, lon2):
    """Calcula la distancia geodésica (km) entre dos coordenadas."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def tiempo_viaje(distancia_km):
    """Calcula tiempo estimado de viaje en horas, asumiendo velocidad promedio según zona."""
    if distancia_km < 20:
        return 0.5  # viaje urbano
    elif distancia_km < 100:
        return distancia_km / 60  # velocidad promedio 60 km/h
    else:
        return distancia_km / 80  # carretera larga

def generar_pdf(df):
    """Genera PDF del itinerario."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    estilos = getSampleStyleSheet()
    contenido = [Paragraph("Itinerario Turístico - Región de Arica y Parinacota", estilos['Title']), Spacer(1, 12)]

    data = [["Día", "Fecha", "Zona", "Destino", "Distancia (km)", "Tiempo visita", "Tiempo viaje"]]
    for _, row in df.iterrows():
        data.append([
            row["Día"], row["Fecha"], row["Zona"], row["Destino"],
            f"{row['Distancia (km)']:.1f}", row["Tiempo estimado de visita"],
            f"{row['Tiempo de viaje (h)']:.1f} h"
        ])

    tabla = Table(data, colWidths=[40, 80, 80, 140, 80, 80, 80])
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightblue),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey)
    ]))
    contenido.append(tabla)
    doc.build(contenido)
    buffer.seek(0)
    return buffer

# ===========================
# BASE DE DATOS DE DESTINOS
# ===========================
destinos = [
    {"nombre": "Playa Chinchorro", "lat": -18.4530, "lon": -70.3125, "zona": "Arica",
     "info": "Playa urbana ideal para nadar y practicar deportes acuáticos.",
     "foto": "https://upload.wikimedia.org/wikipedia/commons/5/59/Playa_Chinchorro%2C_Arica.jpg", "tiempo": "2 horas"},
    {"nombre": "Playa El Laucho", "lat": -18.4872, "lon": -70.3210, "zona": "Arica",
     "info": "Playa pequeña y tranquila, ideal para disfrutar el atardecer.",
     "foto": "https://upload.wikimedia.org/wikipedia/commons/1/16/Playa_El_Laucho_Arica_Chile.JPG", "tiempo": "2 horas"},
    {"nombre": "Cuevas de Anzota", "lat": -18.5506, "lon": -70.3414, "zona": "Arica",
     "info": "Formaciones rocosas junto al mar con arte rupestre.",
     "foto": "https://upload.wikimedia.org/wikipedia/commons/f/f2/Cuevas_de_Anzota%2C_Arica%2C_Chile.jpg", "tiempo": "1.5 horas"},
    {"nombre": "Morro de Arica", "lat": -18.4835, "lon": -70.3245, "zona": "Arica",
     "info": "Mirador histórico con museo y vistas panorámicas.",
     "foto": "https://upload.wikimedia.org/wikipedia/commons/8/86/Morro_de_Arica_-_vista_sur.jpg", "tiempo": "1.5 horas"},
    {"nombre": "Humedal del Río Lluta", "lat": -18.4098, "lon": -70.3090, "zona": "Arica",
     "info": "Zona protegida con gran biodiversidad de aves migratorias.",
     "foto": "https://upload.wikimedia.org/wikipedia/commons/1/1f/Humedal_del_R%C3%ADo_Lluta%2C_Arica.jpg", "tiempo": "1.5 horas"},
    {"nombre": "Putre", "lat": -18.1950, "lon": -69.5595, "zona": "Altiplano",
     "info": "Pueblo andino pintoresco y base para explorar el Parque Nacional Lauca.",
     "foto": "https://upload.wikimedia.org/wikipedia/commons/2/22/Putre%2C_Chile.jpg", "tiempo": "2 horas"},
    {"nombre": "Parinacota", "lat": -18.2000, "lon": -69.1500, "zona": "Altiplano",
     "info": "Pueblo altiplánico con arquitectura tradicional y cercanía a volcanes.",
     "foto": "https://upload.wikimedia.org/wikipedia/commons/3/3b/Parinacota_-_Chile.jpg", "tiempo": "1.5 horas"},
    {"nombre": "Lago Chungará", "lat": -18.2503, "lon": -69.1478, "zona": "Altiplano",
     "info": "Uno de los lagos más altos del mundo, rodeado de volcanes nevados.",
     "foto": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Lago_Chungar%C3%A1.jpg", "tiempo": "2 horas"},
]

# ===========================
# INTERFAZ DE SELECCIÓN
# ===========================
st.subheader("📍 Atractivos turísticos")

cols = st.columns(3)
seleccion = []
for i, d in enumerate(destinos):
    with cols[i % 3]:
        st.image(d["foto"], caption=d["nombre"], use_container_width=True)
        st.write(d["info"])
        if st.checkbox(f"Visitar {d['nombre']}"):
            seleccion.append(d)

dias = st.number_input("Días de viaje disponibles", min_value=1, max_value=10, value=3)

# ===========================
# GENERAR ITINERARIO
# ===========================
if st.button("🗺️ Generar Itinerario Optimizado"):
    if not seleccion:
        st.warning("Selecciona al menos un destino.")
    else:
        origen = (-18.4783, -70.3126)  # Arica Centro
        recorrido = []
        for d in seleccion:
            dist = haversine(origen[0], origen[1], d["lat"], d["lon"])
            tiempo_conduccion = tiempo_viaje(dist)
            recorrido.append((d["nombre"], d["zona"], round(dist, 1), d["tiempo"], round(tiempo_conduccion, 1), d["lat"], d["lon"]))

        # Agrupar destinos por zona
        grupos = {}
        for r in recorrido:
            grupos.setdefault(r[1], []).append(r)

        # Distribuir por días
        itinerario = []
        fecha_inicio = datetime.now().date()
        dia_actual = 1

        for zona, lugares in grupos.items():
            for l in lugares:
                fecha = fecha_inicio + timedelta(days=dia_actual - 1)
                itinerario.append({
                    "Día": dia_actual,
                    "Fecha": fecha.strftime("%d/%m/%Y"),
                    "Zona": zona,
                    "Destino": l[0],
                    "Distancia (km)": l[2],
                    "Tiempo estimado de visita": l[3],
                    "Tiempo de viaje (h)": l[4]
                })
            dia_actual += 1
            if dia_actual > dias:
                dia_actual = dias  # si sobran destinos, se agregan al último día

        df = pd.DataFrame(itinerario).sort_values(["Día", "Zona"])
        st.dataframe(df, use_container_width=True)

        # Crear mapa
        mapa = folium.Map(location=origen, zoom_start=8)
        folium.Marker(origen, tooltip="Inicio: Arica Centro", icon=folium.Icon(color='green')).add_to(mapa)
        for _, row in df.iterrows():
            folium.Marker([seleccion[0]['lat'], seleccion[0]['lon']],
                          popup=row["Destino"], icon=folium.Icon(color="red")).add_to(mapa)
        st_folium(mapa, width=700, height=500)

        # PDF descargable
        pdf_buffer = generar_pdf(df)
        st.download_button(
            label="📄 Descargar Itinerario en PDF",
            data=pdf_buffer,
            file_name="Itinerario_Arica_Parinacota.pdf",
            mime="application/pdf"
        )
