import streamlit as st
import os
from pathlib import Path

from geopy.distance import geodesic
from fpdf import FPDF
import math
import folium
from streamlit_folium import st_folium
import requests
from PIL import Image
from io import BytesIO
import tempfile
import re

# ---------- CONFIGURACIÓN ---------- #
st.set_page_config(page_title="App Turística - Arica y Parinacota", layout="wide")

# ---------- RUTAS DE IMÁGENES LOCALES (GitHub) ---------- #
BASE_DIR = Path(__file__).resolve().parent

def img(filename: str) -> str:
    """Devuelve la ruta absoluta a una imagen dentro de /images.
    Si no existe, avisa para detectar errores en GitHub/Streamlit Cloud.
    """
    path = BASE_DIR / "images" / filename
    if not path.exists():
        st.warning(f"⚠️ Falta imagen en repo: images/{filename}")
    return str(path)

def cargar_imagen_para_ui(path_or_url: str):
    """Carga imagen para UI. Soporta ruta local o URL."""
    try:
        if path_or_url.startswith("http"):
            r = requests.get(path_or_url, timeout=10)
            r.raise_for_status()
            return Image.open(BytesIO(r.content)).convert("RGB")
        else:
            return Image.open(path_or_url).convert("RGB")
    except:
        return None

# ---------- DATOS DE DESTINOS ---------- #
destinos = [
    {"nombre": "Morro de Arica", "lat": -18.477, "lon": -70.330, "tipo": "Cultura", "tiempo": 1.5,
     "region": "Ciudad", "descripcion": "Icono histórico con vista panorámica de la ciudad.",
     "imagen": img("morro-de-arica-1.jpg")},

    {"nombre": "Playa El Laucho", "lat": -18.486, "lon": -70.318, "tipo": "Playa", "tiempo": 2,
     "region": "Costa", "descripcion": "Playa tranquila ideal para relajarse y tomar sol.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Playa_El_Laucho_Arica.jpg"},

    {"nombre": "Playa La Lisera", "lat": -18.489, "lon": -70.327, "tipo": "Playa", "tiempo": 2,
     "region": "Costa", "descripcion": "Playa muy visitada, ideal para baño y descanso cerca del centro.",
     "imagen": img("Playa-La-Lisera-Arica.jpg")},

    {"nombre": "Cuevas de Anzota", "lat": -18.533, "lon": -70.353, "tipo": "Naturaleza", "tiempo": 1.5,
     "region": "Costa", "descripcion": "Cuevas naturales con formaciones rocosas únicas.",
     "imagen": img("Cuevas de Anzota.jpg")},

    {"nombre": "Playa Chinchorro", "lat": -18.466, "lon": -70.307, "tipo": "Playa", "tiempo": 2.5,
     "region": "Costa", "descripcion": "Famosa playa con actividades de pesca y deportes acuáticos.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/3/3c/Playa_Chinchorro_Arica.jpg"},

    {"nombre": "Humedal del Río Lluta", "lat": -18.425, "lon": -70.324, "tipo": "Naturaleza", "tiempo": 2,
     "region": "Costa", "descripcion": "Ecosistema protegido, ideal para observación de aves.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/1/1e/Humedal_del_Rio_Lluta_Arica.jpg"},

    {"nombre": "Museo de Azapa", "lat": -18.52, "lon": -70.33, "tipo": "Cultura", "tiempo": 1.5,
     "region": "Valle", "descripcion": "Museo arqueológico con momias y cultura Chinchorro.",
     "imagen": img("Museo arqueologico San Miguel de Azapa.jpg")},

    {"nombre": "Valle de Lluta", "lat": -18.43, "lon": -70.32, "tipo": "Naturaleza", "tiempo": 2,
     "region": "Valle", "descripcion": "Hermoso valle con agricultura tradicional y paisajes naturales.",
     "imagen": img("Valle de lluta.jpg")},

    {"nombre": "Valle de Azapa", "lat": -18.52, "lon": -70.17, "tipo": "Naturaleza", "tiempo": 2,
     "region": "Valle", "descripcion": "Valle destacado por su agricultura y patrimonio cultural.",
     "imagen": img("Valle de Azapa.jpeg")},

    {"nombre": "Catedral de San Marcos", "lat": -18.478, "lon": -70.328, "tipo": "Cultura", "tiempo": 1,
     "region": "Ciudad", "descripcion": "Catedral histórica del centro de Arica.",
     "imagen": img("Catedral de San Marcos.jpeg")},

    {"nombre": "La Ex Aduana", "lat": -18.479, "lon": -70.329, "tipo": "Cultura", "tiempo": 1,
     "region": "Ciudad", "descripcion": "Edificio histórico que albergó la aduana de la ciudad.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Ex_Aduana_Arica.jpg"},

    {"nombre": "Putre", "lat": -18.195, "lon": -69.559, "tipo": "Cultura", "tiempo": 3,
     "region": "Altiplano", "descripcion": "Pueblo tradicional a orillas del altiplano con cultura Aymara.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Putre_village.jpg"},

    {"nombre": "Parque Nacional Lauca", "lat": -18.243, "lon": -69.352, "tipo": "Naturaleza", "tiempo": 4,
     "region": "Altiplano", "descripcion": "Parque con volcanes, lagunas y fauna típica de la zona.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/2/2c/Parque_Nacional_Lauca_Chile.jpg"},

    # ✅ Lago Chungará ELIMINADO

    {"nombre": "Salar de Surire", "lat": -18.85, "lon": -69.05, "tipo": "Naturaleza", "tiempo": 3.5,
     "region": "Altiplano", "descripcion": "Salar impresionante con fauna típica del altiplano.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/7/74/Salar_de_Surire.jpg"},
]



# ---------- FUNCIONES ---------- #
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

        if pendientes:
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

def generar_pdf_lujo(itinerario):
    pdf = FPDF('P', 'mm', 'A4')
    pdf.set_auto_page_break(auto=True, margin=15)

    def limpiar_texto(texto):
        texto = re.sub(r'[^\x00-\x7F]+', ' ', texto)
        return texto

    # Portada
    pdf.add_page()
    pdf.set_font("Arial", "B", 28)
    pdf.cell(0, 20, "Itinerario Turístico", ln=True, align="C")
    pdf.set_font("Arial", "B", 22)
    pdf.cell(0, 15, "Arica y Parinacota", ln=True, align="C")

    # Imagen portada (si existe local, la usa; si no, intenta URL)
    portada_local = img("morro-de-arica-1.jpg")
    try:
        if os.path.exists(portada_local):
            pdf.image(portada_local, x=30, y=60, w=150)
        else:
            portada_url = "https://upload.wikimedia.org/wikipedia/commons/2/2c/Morro_de_Arica.jpg"
            response = requests.get(portada_url, timeout=10)
            img_pil = Image.open(BytesIO(response.content)).convert("RGB")
            temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
            img_pil.thumbnail((500, 500))
            img_pil.save(temp_path)
            pdf.image(temp_path, x=30, y=60, w=150)
    except:
        pass

    pdf.add_page()

    # Tabla de contenido
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 10, "Tabla de Contenido", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "", 14)
    for idx, dia in enumerate(itinerario.keys()):
        pdf.cell(0, 8, f"{idx+1}. {dia}", ln=True)
    pdf.add_page()

    # Itinerario por día
    for dia, lugares in itinerario.items():
        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 10, limpiar_texto(dia), ln=True)
        pdf.ln(5)

        for lugar in lugares:
            color = colores_region.get(lugar["region"], "#FFFFFF")
            pdf.set_fill_color(int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16))
            pdf.set_font("Arial", "B", 16)
            pdf.multi_cell(0, 8, limpiar_texto(f"{lugar['nombre']} ({lugar['region']})"), border=1, fill=True)

            # Imagen (local o URL)
            try:
                if isinstance(lugar["imagen"], str) and lugar["imagen"].startswith("http"):
                    response = requests.get(lugar["imagen"], timeout=10)
                    img_pil = Image.open(BytesIO(response.content)).convert("RGB")
                    temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg").name
                    img_pil.thumbnail((400, 400))
                    img_pil.save(temp_path)
                    pdf.image(temp_path, w=120)
                else:
                    if os.path.exists(lugar["imagen"]):
                        pdf.image(lugar["imagen"], w=120)
            except:
                pass

            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 6, limpiar_texto(f"{lugar['tipo']} - {lugar['tiempo']} hrs\n{lugar['descripcion']}"))
            pdf.ln(2)

            idx_actual = lugares.index(lugar)
            if idx_actual < len(lugares) - 1:
                dist = geodesic(
                    (lugar["lat"], lugar["lon"]),
                    (lugares[idx_actual + 1]["lat"], lugares[idx_actual + 1]["lon"])
                ).km
                pdf.multi_cell(0, 6, f"Distancia al siguiente: {dist:.1f} km")
            pdf.ln(5)

        pdf.add_page()

    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Visita Arica y Parinacota - Naturaleza, cultura y aventura.", ln=True, align="C")

    filename = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    pdf.output(filename)
    return filename

# ---------- INTERFAZ ---------- #
st.title("🌅 Guía Turística - Arica y Parinacota")
st.markdown("Explora la región con itinerarios personalizados por secciones geográficas.")

st.sidebar.header("🧭 Configura tu viaje")
dias = st.sidebar.slider("Días de visita", 1, 7, 3)

destinos_seleccionados = []

# Mostrar destinos por secciones
for seccion in ["Ciudad", "Costa", "Valle", "Altiplano"]:
    st.subheader(f"{seccion}")
    lugares_seccion = [d for d in destinos if d["region"] == seccion]
    cols_por_fila = 3

    for i in range(0, len(lugares_seccion), cols_por_fila):
        fila = st.columns(min(cols_por_fila, len(lugares_seccion) - i))
        for j, lugar in enumerate(lugares_seccion[i:i + cols_por_fila]):
            with fila[j]:
                img_pil = cargar_imagen_para_ui(lugar["imagen"])
                if img_pil is not None:
                    st.image(img_pil, use_column_width=True)
                else:
                    st.warning(f"No se pudo cargar la imagen de {lugar['nombre']}")

                st.markdown(f"**{lugar['nombre']}** ({lugar['tipo']})")
                st.markdown(f"🕓 {lugar['tiempo']} hrs")
                st.markdown(f"📖 {lugar['descripcion']}")

                if st.checkbox("Añadir al itinerario", key=f"chk_{lugar['nombre']}"):
                    destinos_seleccionados.append(lugar)

# Generar itinerario y mapa
if destinos_seleccionados:
    itinerario = generar_itinerario_por_cercania(destinos_seleccionados, dias)

    st.subheader("🗺️ Mapa de tu ruta turística con recorrido")
    mapa = folium.Map(location=[-18.48, -70.32], zoom_start=9)
    colores_dia = ["blue", "red", "green", "orange", "purple", "darkred", "cadetblue"]

    for idx_dia, (dia, lugares) in enumerate(itinerario.items()):
        coords_dia = []
        for lugar in lugares:
            folium.Marker(
                [lugar["lat"], lugar["lon"]],
                popup=f"{lugar['nombre']} ({dia})",
                icon=folium.Icon(color=colores_dia[idx_dia % len(colores_dia)])
            ).add_to(mapa)
            coords_dia.append((lugar["lat"], lugar["lon"]))

        if len(coords_dia) > 1:
            folium.PolyLine(
                coords_dia,
                color=colores_dia[idx_dia % len(colores_dia)],
                weight=3,
                opacity=0.7,
                tooltip=dia
            ).add_to(mapa)

    st_folium(mapa, width=700, height=450)

    st.subheader("🗓️ Itinerario sugerido")
    for dia, lugares in itinerario.items():
        st.markdown(f"### {dia}")

        # Mostrar en filas de 3 para que no se aplaste
        for i in range(0, len(lugares), 3):
            cols = st.columns(3)
            for j, lugar in enumerate(lugares[i:i + 3]):
                with cols[j]:
                    img_pil = cargar_imagen_para_ui(lugar["imagen"])
                    if img_pil is not None:
                        st.image(img_pil, use_column_width=True)
                    else:
                        st.warning(f"No se pudo cargar la imagen de {lugar['nombre']}")

                    st.markdown(f"**{lugar['nombre']}**")
                    st.markdown(f"🕓 {lugar['tiempo']} hrs")
                    st.markdown(f"📖 {lugar['descripcion']}")
        st.divider()

    ruta_url = generar_link_google_maps(destinos_seleccionados)
    st.markdown(f"🚗 [Ver ruta completa en Google Maps]({ruta_url})", unsafe_allow_html=True)

    if st.button("📄 Generar PDF de Lujo"):
        pdf_path = generar_pdf_lujo(itinerario)
        with open(pdf_path, "rb") as f:
            st.download_button(
                "Descargar PDF Turístico Profesional",
                f,
                file_name="Itinerario_Turistico_Arica_Lujo.pdf"
            )
else:
    st.info("Selecciona al menos un atractivo turístico para generar tu itinerario.")

