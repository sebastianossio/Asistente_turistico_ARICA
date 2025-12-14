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
     "imagen": img("Playa el Laucho.jpg")},

    {"nombre": "Playa La Lisera", "lat": -18.489, "lon": -70.327, "tipo": "Playa", "tiempo": 2,
     "region": "Costa", "descripcion": "Playa muy visitada, ideal para baño y descanso cerca del centro.",
     "imagen": img("Playa-La-Lisera-Arica.jpg")},

    {"nombre": "Cuevas de Anzota", "lat": -18.533, "lon": -70.353, "tipo": "Naturaleza", "tiempo": 1.5,
     "region": "Costa", "descripcion": "Cuevas naturales con formaciones rocosas únicas.",
     "imagen": img("Cuevas de Anzota.jpg")},

    {"nombre": "Playa Chinchorro", "lat": -18.466, "lon": -70.307, "tipo": "Playa", "tiempo": 2.5,
     "region": "Costa", "descripcion": "Famosa playa con actividades de pesca y deportes acuáticos.",
     "imagen": img("Playa-Chinchorro.jpg")},

    {"nombre": "Humedal del Río Lluta", "lat": -18.425, "lon": -70.324, "tipo": "Naturaleza", "tiempo": 2,
     "region": "Costa", "descripcion": "Ecosistema protegido, ideal para observación de aves.",
     "imagen": img("Humedal-Rio-Lluta-Region-de-Arica-y-Parinacota.jpg")},

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
     "imagen": img("Catedral-San-Marcos.jpg")},

    {"nombre": "La Ex Aduana", "lat": -18.479, "lon": -70.329, "tipo": "Cultura", "tiempo": 1,
     "region": "Ciudad", "descripcion": "Edificio histórico que albergó la aduana de la ciudad.",
     "imagen": img("Ex-Aduana-Casa-de-la-Cultura-Arica.jpg")},

    {"nombre": "Putre", "lat": -18.195, "lon": -69.559, "tipo": "Cultura", "tiempo": 3,
     "region": "Altiplano", "descripcion": "Pueblo tradicional a orillas del altiplano con cultura Aymara.",
     "imagen": img("Putre.jpg")},

    {"nombre": "Parque Nacional Lauca", "lat": -18.243, "lon": -69.352, "tipo": "Naturaleza", "tiempo": 4,
     "region": "Altiplano", "descripcion": "Parque con volcanes, lagunas y fauna típica de la zona.",
     "imagen": img("Parque nacional Lauca.jpg")},

    {"nombre": "Salar de Surire", "lat": -18.85, "lon": -69.05, "tipo": "Naturaleza", "tiempo": 3.5,
     "region": "Altiplano", "descripcion": "Salar impresionante con fauna típica del altiplano.",
     "imagen": img("Salar_de_Surire.jpg")},
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
    # ---------- Helpers ---------- #
    def limpiar_texto(texto):
        # FPDF clásico no soporta Unicode: convertimos a latin-1 compatible
        if texto is None:
            return ""
        return str(texto).encode("latin-1", "ignore").decode("latin-1")

    colores_region_local = {
        "Ciudad":   "#FFB199",
        "Costa":    "#9AD9FF",
        "Valle":    "#A6F3A6",
        "Altiplano":"#E0B3FF",
    }

    def hex_to_rgb(h):
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    def imagen_a_jpg_temp(ruta_o_url):
        """Convierte cualquier imagen (local o URL) a JPG RGB compatible con FPDF."""
        try:
            if isinstance(ruta_o_url, str) and ruta_o_url.startswith("http"):
                r = requests.get(ruta_o_url, timeout=15)
                r.raise_for_status()
                img_pil = Image.open(BytesIO(r.content))
            else:
                img_pil = Image.open(ruta_o_url)

            img_pil = img_pil.convert("RGB")
            img_pil.thumbnail((1200, 1200))

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            tmp_path = tmp.name
            tmp.close()

            img_pil.save(tmp_path, "JPEG", quality=88)
            return tmp_path
        except:
            return None

    # ---------- PDF class with footer ---------- #
    class PDF(FPDF):
        def footer(self):
            self.set_y(-12)
            self.set_draw_color(220, 220, 220)
            self.line(10, self.get_y(), 200, self.get_y())
            self.set_font("Arial", "I", 9)
            self.set_text_color(120, 120, 120)
            self.cell(0, 10, f"Página {self.page_no()}", align="C")

    pdf = PDF("P", "mm", "A4")
    pdf.set_auto_page_break(auto=True, margin=14)

    # ---------- PORTADA ---------- #
    pdf.add_page()

    # Fondo suave
    pdf.set_fill_color(248, 248, 248)
    pdf.rect(0, 0, 210, 297, style="F")

    # Título
    pdf.set_text_color(25, 25, 25)
    pdf.set_font("Arial", "B", 30)
    pdf.ln(18)
    pdf.cell(0, 12, limpiar_texto("Itinerario Turístico"), ln=True, align="C")

    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 10, limpiar_texto("Arica y Parinacota"), ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 7, limpiar_texto("Guía personalizada con mapa y tiempos estimados"), ln=True, align="C")

    # Fecha
    from datetime import datetime
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 7, limpiar_texto(f"Generado el {datetime.now().strftime('%d-%m-%Y')}"), ln=True, align="C")

    # Imagen hero (primer destino disponible)
    hero_img = None
    for _, lugares in itinerario.items():
        if lugares:
            hero_img = imagen_a_jpg_temp(lugares[0].get("imagen"))
            break

    if hero_img:
        # Tarjeta blanca para imagen
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(235, 235, 235)
        pdf.rounded_rect = getattr(pdf, "rounded_rect", None)  # compat
        # Marco simple
        x, y, w, h = 18, 80, 174, 135
        pdf.rect(x, y, w, h, style="FD")
        try:
            pdf.image(hero_img, x=x+6, y=y+6, w=w-12)
        except:
            pass

    # Banda inferior
    pdf.set_y(270)
    pdf.set_fill_color(30, 30, 30)
    pdf.rect(0, 270, 210, 27, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, limpiar_texto("Naturaleza • Cultura • Aventura"), ln=True, align="C")

    # ---------- ITINERARIO POR DÍA ---------- #
    for dia, lugares in itinerario.items():
        pdf.add_page()

        # Header del día
        pdf.set_fill_color(30, 30, 30)
        pdf.rect(0, 0, 210, 22, style="F")
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 18)
        pdf.set_xy(10, 6)
        pdf.cell(0, 10, limpiar_texto(dia), ln=False)

        pdf.ln(26)
        pdf.set_text_color(60, 60, 60)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 6, limpiar_texto("Recomendación: sigue el orden propuesto para reducir traslados."))

        pdf.ln(2)

        # Cards de destinos
        for i, lugar in enumerate(lugares):
            region = lugar.get("region", "")
            color_hex = colores_region_local.get(region, "#FFFFFF")
            r, g, b = hex_to_rgb(color_hex)

            # Medidas de tarjeta
            card_x = 10
            card_w = 190
            card_h = 62  # altura base
            start_y = pdf.get_y()

            # Si no cabe, nueva página
            if start_y + card_h > 280:
                pdf.add_page()
                pdf.ln(8)
                start_y = pdf.get_y()

            # Fondo tarjeta
            pdf.set_draw_color(230, 230, 230)
            pdf.set_fill_color(255, 255, 255)
            pdf.rect(card_x, start_y, card_w, card_h, style="FD")

            # Banda color región
            pdf.set_fill_color(r, g, b)
            pdf.rect(card_x, start_y, 6, card_h, style="F")

            # Imagen a la izquierda
            img_temp = imagen_a_jpg_temp(lugar.get("imagen"))
            img_x = card_x + 10
            img_y = start_y + 8
            img_w = 52
            img_h = 46

            # Marco de imagen
            pdf.set_draw_color(240, 240, 240)
            pdf.rect(img_x, img_y, img_w, img_h, style="D")

            if img_temp:
                try:
                    pdf.image(img_temp, x=img_x, y=img_y, w=img_w, h=img_h)
                except:
                    pass

            # Texto a la derecha
            text_x = img_x + img_w + 10
            text_y = start_y + 8
            pdf.set_xy(text_x, text_y)

            # Nombre
            pdf.set_text_color(25, 25, 25)
            pdf.set_font("Arial", "B", 13)
            pdf.multi_cell(0, 6, limpiar_texto(lugar.get("nombre", "")))

            # Meta info
            pdf.set_text_color(80, 80, 80)
            pdf.set_font("Arial", "", 10)
            tipo = limpiar_texto(lugar.get("tipo", ""))
            tiempo = limpiar_texto(lugar.get("tiempo", ""))
            reg = limpiar_texto(region)
            pdf.set_x(text_x)
            pdf.cell(0, 5, f"Tipo: {tipo}   |   Tiempo: {tiempo} hrs   |   Zona: {reg}", ln=True)

            # Descripción (2–3 líneas)
            desc = limpiar_texto(lugar.get("descripcion", ""))
            pdf.set_x(text_x)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, desc[:220])  # corta para que no se desborde

            # Distancia al siguiente (si aplica)
            if i < len(lugares) - 1:
                try:
                    dist = geodesic(
                        (lugar["lat"], lugar["lon"]),
                        (lugares[i + 1]["lat"], lugares[i + 1]["lon"])
                    ).km
                    pdf.set_x(text_x)
                    pdf.set_text_color(60, 60, 60)
                    pdf.set_font("Arial", "I", 9)
                    pdf.cell(0, 5, limpiar_texto(f"Distancia al siguiente: {dist:.1f} km"), ln=True)
                except:
                    pass

            pdf.ln(6)

    # ---------- CIERRE ---------- #
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(25, 25, 25)
    pdf.ln(20)
    pdf.cell(0, 10, limpiar_texto("¡Buen viaje!"), ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(
        0, 7,
        limpiar_texto("Este itinerario fue generado automáticamente en base a los destinos seleccionados y un criterio de cercanía."),
        align="C"
    )
    pdf.ln(6)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 8, limpiar_texto("Arica y Parinacota • Turismo inteligente"), ln=True, align="C")

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

