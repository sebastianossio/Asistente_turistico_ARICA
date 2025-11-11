import streamlit as st
import openai
import os

# streamlit_app.py
import streamlit as st
import pandas as pd
import folium
from folium import PolyLine
from geopy.distance import geodesic
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
import requests
from PIL import Image as PILImage
import tempfile
import os

st.set_page_config(page_title="App Turística — Arica y Parinacota", layout="wide")
st.title("🌄 App Turística — Arica y Parinacota (sin chatbot)")

# ----------------------
# LISTA DE ATRACTIVOS
# ----------------------
atractivos = [
    {"nombre": "Playa Chinchorro", "lat": -18.4726, "lon": -70.3128, "tiempo": 2,
     "descripcion": "Amplia playa urbana ideal para nadar y disfrutar del sol.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/1/11/Playa_Chinchorro_Arica_2020.jpg"},
    {"nombre": "Playa El Laucho", "lat": -18.4872, "lon": -70.3232, "tiempo": 1.5,
     "descripcion": "Playa céntrica de aguas calmadas, ideal para familias.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Playa_El_Laucho_Arica.jpg"},
    {"nombre": "Humedal del Río Lluta", "lat": -18.4395, "lon": -70.3170, "tiempo": 1.5,
     "descripcion": "Santuario de aves migratorias con senderos y miradores naturales.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/b/bd/Humedal_del_R%C3%ADo_Lluta_-_Arica.jpg"},
    {"nombre": "Morro de Arica", "lat": -18.4806, "lon": -70.3273, "tiempo": 2,
     "descripcion": "Histórico morro con museo y mirador panorámico.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/8/8d/Morro_de_Arica.jpg"},
    {"nombre": "Museo de Sitio Colón 10", "lat": -18.4770, "lon": -70.3183, "tiempo": 1.5,
     "descripcion": "Museo con las momias de la cultura Chinchorro.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/f/f3/Museo_de_Sitio_Col%C3%B3n_10_-_Arica.jpg"},
    {"nombre": "Cuevas de Anzota", "lat": -18.5358, "lon": -70.3511, "tiempo": 1.5,
     "descripcion": "Formaciones rocosas junto al mar y miradores.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/7/7d/Cuevas_de_Anzota_-_Arica.jpg"},
    {"nombre": "Valle de Azapa", "lat": -18.481, "lon": -70.308, "tiempo": 2,
     "descripcion": "Valle agrícola famoso por olivos y aceitunas.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Valle_de_Azapa.jpg"},
    {"nombre": "Geoglifos de Lluta", "lat": -18.20, "lon": -70.30, "tiempo": 1.5,
     "descripcion": "Dibujos prehispánicos visibles desde miradores en el valle de Lluta.",
     "imagen_url": "https://images.visitchile.com/destinos/283_6702_la_ruta_altiplanca.jpg"},
    {"nombre": "Parque Nacional Lauca", "lat": -18.2333, "lon": -69.1667, "tiempo": 4,
     "descripcion": "Lagunas y volcanes en la altura, fauna altiplánica.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/1/1d/Lago_Chungara_y_volcan_Parinacota.jpg"},
    {"nombre": "Putre", "lat": -18.1977, "lon": -69.5593, "tiempo": 3,
     "descripcion": "Pueblo altiplánico, puerta al Parque Lauca.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Putre_-_Chile.jpg"},
    {"nombre": "Termas de Jurasi", "lat": -18.2255, "lon": -69.5250, "tiempo": 2,
     "descripcion": "Aguas termales cerca de Putre.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/5/57/Termas_de_Jurasi_Putre.jpg"},
    {"nombre": "Salar de Surire", "lat": -19.366, "lon": -69.383, "tiempo": 3,
     "descripcion": "Salar con flamencos y paisaje altoandino.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/5/57/Salar_de_Surire.jpg"},
    {"nombre": "Codpa", "lat": -18.1928, "lon": -69.8819, "tiempo": 2,
     "descripcion": "Valle tradicional con vinos artesanales y arquitectura típica.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/9/91/Codpa_Arica.jpg"},
    {"nombre": "Camarones (pueblo)", "lat": -18.200, "lon": -70.500, "tiempo": 2,
     "descripcion": "Pueblo costero con gastronomía basada en mariscos.",
     "imagen_url": "https://upload.wikimedia.org/wikipedia/commons/9/9f/Camarones_Arica.jpg"}
]

# ----------------------
# FUNCIONES DE ITINERARIO
# ----------------------
def distancia_km(a, b):
    return geodesic((a["lat"], a["lon"]), (b["lat"], b["lon"])).km

def agrupar_por_dia(destinos, dias):
    # Distribuye destinos en 'dias' grupos intentando balancear y luego optimizar orden por cercanía
    grupos = [[] for _ in range(dias)]
    destinos_sorted = sorted(destinos, key=lambda x: (x["lat"], x["lon"]))
    for idx, d in enumerate(destinos_sorted):
        grupos[idx % dias].append(d)
    # Dentro de cada grupo ordenar por ruta aproximada (nearest neighbor)
    for i, g in enumerate(grupos):
        if len(g) > 1:
            ordenado = [g[0]]
            resto = g[1:]
            while resto:
                last = ordenado[-1]
                siguiente = min(resto, key=lambda x: distancia_km(last, x))
                ordenado.append(siguiente)
                resto.remove(siguiente)
            grupos[i] = ordenado
    return grupos

def generar_itinerario_con_distancias(destinos_seleccionados, dias):
    grupos = agrupar_por_dia(destinos_seleccionados, dias)
    itinerario = []
    for dia_index, grupo in enumerate(grupos, start=1):
        if not grupo:
            continue
        # calcular distancias entre par consecutivos del día
        for i, lugar in enumerate(grupo):
            fila = {
                "Día": dia_index,
                "Orden en día": i+1,
                "Destino": lugar["nombre"],
                "Descripción": lugar["descripcion"],
                "Tiempo estimado (h)": lugar["tiempo"],
                "Lat": lugar["lat"],
                "Lon": lugar["lon"],
                "Imagen": lugar["imagen_url"]
            }
            # distancia desde anterior en el mismo día
            if i == 0:
                fila["Distancia desde anterior (km)"] = 0.0
            else:
                prev = grupo[i-1]
                fila["Distancia desde anterior (km)"] = round(distancia_km(prev, lugar), 2)
            itinerario.append(fila)
    return itinerario

# ----------------------
# INTERFAZ STREAMLIT
# ----------------------
st.sidebar.markdown("### Configuración de la visita")
dias = st.sidebar.number_input("Cantidad de días", min_value=1, max_value=10, value=3)
st.sidebar.markdown("Selecciona los atractivos en la pantalla principal y luego haz click en 'Generar Itinerario'.")

st.subheader("Atractivos disponibles (selecciona varios)")
# Mostrar en columnas con imagenes
num_cols = 3
cols = st.columns(num_cols)
seleccionados = []
for i, a in enumerate(atractivos):
    with cols[i % num_cols]:
        try:
            resp = requests.get(a["imagen_url"], timeout=6)
            img = PILImage.open(BytesIO(resp.content))
            st.image(img, caption=a["nombre"], use_column_width=True)
        except Exception:
            st.write("🖼️", a["nombre"])
        if st.checkbox(label=f"Seleccionar: {a['nombre']}", key=a["nombre"]):
            seleccionados.append(a)

# Botón generar
if st.button("Generar Itinerario"):
    if not seleccionados:
        st.warning("Selecciona al menos un destino.")
    else:
        # generar itinerario ordenado por día y por cercanía
        itinerario = generar_itinerario_con_distancias(seleccionados, dias)
        df = pd.DataFrame(itinerario)
        # ordenar la tabla por día y orden en dia
        if not df.empty:
            df = df.sort_values(["Día", "Orden en día"]).reset_index(drop=True)
        st.markdown("### Itinerario sugerido (ordenado por día)")
        st.dataframe(df[["Día", "Orden en día", "Destino", "Tiempo estimado (h)", "Distancia desde anterior (km)"]])

        # MAPA: trazar ruta en orden (día por día concatenado)
        mapa = folium.Map(location=[-18.48, -70.32], zoom_start=8)
        # acumulador para ruta completa (por orden de aparición en df)
        coords_ruta = []
        for _, row in df.iterrows():
            lat = row["Lat"]
            lon = row["Lon"]
            folium.Marker([lat, lon], popup=row["Destino"], tooltip=row["Destino"]).add_to(mapa)
            coords_ruta.append((lat, lon))
        if len(coords_ruta) > 1:
            PolyLine(coords_ruta, color="blue", weight=3).add_to(mapa)
        st.markdown("### Mapa de la ruta sugerida")
        st.components.v1.html(mapa._repr_html_(), height=520)

        # Generar PDF con fotos y la ruta por día
        def generar_pdf_bytes(itinerario_df):
            buf = BytesIO()
            doc = SimpleDocTemplate(buf, pagesize=letter)
            styles = getSampleStyleSheet()
            elems = []
            elems.append(Paragraph("Itinerario Turístico - Arica y Parinacota", styles["Title"]))
            elems.append(Spacer(1, 12))
            current_day = None
            # vamos a guardar imágenes temporales en un dir temporal para que reportlab las lea
            with tempfile.TemporaryDirectory() as tmpdir:
                for _, r in itinerario_df.iterrows():
                    dia = int(r["Día"])
                    if dia != current_day:
                        current_day = dia
                        elems.append(Paragraph(f"Día {current_day}", styles["Heading2"]))
                        elems.append(Spacer(1, 6))
                    elems.append(Paragraph(f"{r['Orden en día']}. {r['Destino']} ({r['Tiempo estimado (h)']} h)", styles["Heading3"]))
                    elems.append(Paragraph(r["Descripción"], styles["BodyText"]))
                    # imagen
                    img_url = r["Imagen"]
                    try:
                        resp = requests.get(img_url, timeout=8)
                        img_pil = PILImage.open(BytesIO(resp.content))
                        # conservar proporcionalidad: ancho 400 px máximo
                        w, h = img_pil.size
                        max_w = 400
                        if w > max_w:
                            ratio = max_w / float(w)
                            new_size = (int(w * ratio), int(h * ratio))
                            img_pil = img_pil.resize(new_size, PILImage.LANCZOS)
                        # guardar temporalmente
                        filename = os.path.join(tmpdir, f"{r['Destino']}.png")
                        img_pil.save(filename, format="PNG")
                        elems.append(RLImage(filename, width=400, height=None))
                    except Exception:
                        elems.append(Paragraph("Imagen no disponible", styles["BodyText"]))
                    # distancia desde anterior (si aplica)
                    elems.append(Paragraph(f"Distancia desde anterior (km): {r.get('Distancia desde anterior (km)', 0)}", styles["BodyText"]))
                    elems.append(Spacer(1, 12))
                # Ruta textual final
                ruta_texto = " -> ".join(itinerario_df["Destino"].tolist())
                elems.append(Spacer(1, 8))
                elems.append(Paragraph("Ruta sugerida (orden completo):", styles["Heading3"]))
                elems.append(Paragraph(ruta_texto, styles["BodyText"]))
                doc.build(elems)
                buf.seek(0)
                return buf.getvalue()

        pdf_bytes = generar_pdf_bytes(df)
        st.download_button("📄 Descargar PDF con fotos y ruta", data=pdf_bytes, file_name="itinerario_arica_parinacota.pdf", mime="application/pdf")

# footer / ayuda
st.markdown("---")
st.markdown("**Notas:**")
st.markdown("- Las distancias mostradas son geodésicas (línea recta entre puntos). Para distancias por carretera se necesita una API de rutas.")
st.markdown("- Las imágenes se cargan desde URLs públicas; si alguna no carga, se mostrará un texto alternativo.")
st.markdown("- Ajusta la cantidad de días para que el algoritmo agrupe los destinos de forma conveniente.")


