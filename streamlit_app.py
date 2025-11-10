import streamlit as st
from openai import OpenAI
import streamlit as st
import pandas as pd
import folium
from folium import Popup, PolyLine
from geopy.distance import geodesic
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from googletrans import Translator
import random
from itertools import permutations
import urllib.parse

# --- Traductor ---
translator = Translator()

# --- Datos de atractivos turísticos ---
atractivos = [
    {"nombre": "Playa Chinchorro", "lat": -18.4726, "lon": -70.3128, "zona": "Arica", "tipo": "playa", "tiempo": 2,
     "descripcion": "Amplia playa urbana ideal para nadar y disfrutar del sol.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/b/b9/Playa_Chinchorro_Arica.jpg"},
    {"nombre": "Playa El Laucho", "lat": -18.4872, "lon": -70.3232, "zona": "Arica", "tipo": "playa", "tiempo": 1.5,
     "descripcion": "Playa céntrica de aguas calmadas, ideal para familias.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/3/3f/Playa_El_Laucho%2C_Arica.jpg"},
    {"nombre": "Morro de Arica", "lat": -18.4806, "lon": -70.3273, "zona": "Arica", "tipo": "historia", "tiempo": 2,
     "descripcion": "Histórico morro con museo y mirador panorámico.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/8/8d/Morro_de_Arica.jpg"},
    {"nombre": "Museo de Sitio Colón 10 (Momias Chinchorro)", "lat": -18.4770, "lon": -70.3183, "zona": "Arica",
     "tipo": "cultura", "tiempo": 1.5,
     "descripcion": "Museo con las momias más antiguas del mundo, cultura Chinchorro.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/f/f3/Museo_de_Sitio_Col%C3%B3n_10_-_Arica.jpg"},
    {"nombre": "Humedal del Río Lluta", "lat": -18.4395, "lon": -70.3170, "zona": "Arica", "tipo": "naturaleza", "tiempo": 1.5,
     "descripcion": "Santuario de aves migratorias con senderos y miradores naturales.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/b/bd/Humedal_del_R%C3%ADo_Lluta_-_Arica.jpg"},
    {"nombre": "Putre", "lat": -18.1977, "lon": -69.5593, "zona": "Altiplano", "tipo": "pueblo", "tiempo": 3,
     "descripcion": "Encantador pueblo altiplánico y base para visitar el Parque Lauca.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Putre_-_Chile.jpg"},
    {"nombre": "Parque Nacional Lauca", "lat": -18.2333, "lon": -69.1667, "zona": "Altiplano", "tipo": "naturaleza",
     "tiempo": 4, "descripcion": "Paisaje de altura con lagos, volcanes y fauna andina.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/1/1d/Lago_Chungara_y_volcan_Parinacota.jpg"},
    {"nombre": "Termas de Jurasi", "lat": -18.2255, "lon": -69.5250, "zona": "Altiplano", "tipo": "relajo", "tiempo": 2,
     "descripcion": "Piscinas naturales de aguas termales cerca de Putre.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/5/57/Termas_de_Jurasi_Putre.jpg"},
    {"nombre": "Socoroma", "lat": -18.2242, "lon": -69.5870, "zona": "Altiplano", "tipo": "pueblo", "tiempo": 2,
     "descripcion": "Pintoresco pueblo precordillerano con arquitectura tradicional.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/b/b9/Socoroma_Arica_y_Parinacota.jpg"},
    {"nombre": "Cuevas de Anzota", "lat": -18.5358, "lon": -70.3511, "zona": "Arica", "tipo": "naturaleza", "tiempo": 1.5,
     "descripcion": "Formaciones rocosas y miradores junto al mar.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/7/7d/Cuevas_de_Anzota_-_Arica.jpg"}
]

# --- Funciones auxiliares ---
def distancia(a, b):
    return geodesic((a["lat"], a["lon"]), (b["lat"], b["lon"])).km

def ordenar_por_distancia(destinos):
    if len(destinos) <= 1:
        return destinos
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
            "Zona": d["zona"],
            "lat": d["lat"],
            "lon": d["lon"]
        })
    return itinerario

def generar_pdf(itinerario, idioma="es"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    title = "Tour Itinerary - Arica & Parinacota" if idioma=="en" else "Itinerario Turístico - Arica y Parinacota"
    elementos = [Paragraph(title, styles['Title']), Spacer(1,12)]
    data = [["Día","Destino","Zona","Tiempo estimado (h)","Descripción"]]
    for item in itinerario:
        desc = item["Descripción"]
        if idioma=="en": desc = translator.translate(desc, src="es", dest="en").text
        data.append([item["Día"], item["Destino"], item["Zona"], item["Tiempo estimado (h)"], desc])
    tabla = Table(data)
    tabla.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.lightblue),
                               ("GRID",(0,0),(-1,-1),1,colors.black)]))
    elementos.append(tabla)
    doc.build(elementos)
    buffer.seek(0)
    return buffer

# --- Chatbot con memoria ---
if "memoria" not in st.session_state: st.session_state.memoria = {"preferencias": set()}
if "chat_hist" not in st.session_state: st.session_state.chat_hist = []

def responder_chat(pregunta):
    p = pregunta.lower()
    memoria = st.session_state.memoria
    if "playa" in p: memoria["preferencias"].add("playa"); return "Perfecto 🌊, te gustan las playas."
    if "naturaleza" in p or "paisaje" in p: memoria["preferencias"].add("naturaleza"); return "Genial 🌿, te gusta la naturaleza."
    if "historia" in p or "cultura" in p or "museo" in p: memoria["preferencias"].add("cultura"); return "Interesante 🏛️, te gusta la cultura."
    if "pueblo" in p: memoria["preferencias"].add("pueblo"); return "Maravilloso 🏘️, te gustan los pueblos."
    if "gracias" in p: return "¡De nada! 😄"
    if "hola" in p: return "¡Hola! 👋 Soy tu asistente turístico. ¿Qué tipo de lugares te interesa?"
    if "recomienda" in p or "sugerencia" in p:
        if memoria["preferencias"]:
            tipo = random.choice(list(memoria["preferencias"]))
            sugeridos = [a["nombre"] for a in atractivos if a["tipo"]==tipo]
            return f"Como te interesa {tipo}, te recomiendo: {', '.join(sugeridos)}."
        else: return "Dime qué tipo de lugares prefieres: playa, cultura, pueblos o naturaleza."
    return "Puedo recomendarte playas, cultura, naturaleza o pueblos. ¿Cuál prefieres?"

# --- Interfaz Streamlit ---
st.set_page_config(page_title="Asistente Turístico Arica y Parinacota", layout="wide")
st.title("🏔️ Asistente Turístico Final - Rutas Optimizadas")
st.markdown("Planifica tu viaje, genera itinerarios optimizados, chat inteligente, traducción automática y comparte fácilmente 📱✉️")

# --- Chat ---
st.sidebar.header("💬 Chat con tu Asistente")
pregunta = st.sidebar.text_input("Escribe tu pregunta:")
if st.sidebar.button("Enviar"):
    if pregunta:
        respuesta = responder_chat(pregunta)
        st.session_state.chat_hist.append(("Tú", pregunta))
        st.session_state.chat_hist.append(("Asistente", respuesta))
for autor, texto in st.session_state.chat_hist:
    if autor=="Tú": st.sidebar.markdown(f"**🧍‍♂️ {autor}:** {texto}")
    else: st.sidebar.markdown(f"**🤖 {autor}:** {texto}")

# --- Planificador de viaje ---
st.header("🗓️ Genera tu Itinerario Optimizado")
dias = st.number_input("Cantidad de días de visita", min_value=1, max_value=10, value=3)
st.subheader("Atractivos Turísticos")
seleccionados = []
cols = st.columns(2)
for i,a in enumerate(atractivos):
    with cols[i%2]:
        st.image(a["imagen"], caption=a["nombre"], use_container_width=True)
        if st.checkbox(f"Seleccionar: {a['nombre']}"): seleccionados.append(a)

# Recomendaciones según memoria
if st.session_state.memoria["preferencias"]:
    tipo_pref = list(st.session_state.memoria["preferencias"])
    sugerencias = [a for a in atractivos if a["tipo"] in tipo_pref and a not in seleccionados]
    if sugerencias:
        st.markdown("✨ Basado en tus gustos, también te recomiendo:")
        for s in sugerencias[:3]:
            st.image(s["imagen"], caption=f"{s['nombre']} (Sugerido)", use_container_width=True)
            if st.checkbox(f"Agregar sugerido: {s['nombre']}"): seleccionados.append(s)

if st.button("Generar Itinerario Optimizado"):
    if not seleccionados: st.warning("Selecciona al menos un destino.")
    else:
        itinerario = generar_itinerario_optimizado(seleccionados,dias)
        df = pd.DataFrame(itinerario)
        st.success("✅ Itinerario generado con rutas optimizadas")
        st.dataframe(df)

        mapa = folium.Map(location=[-18.48, -70.32], zoom_start=8)
        line_coords = []
        for dest in itinerario:
            folium.Marker([dest["lat"], dest["lon"]],
                          popup=Popup(f"<b>{dest['Destino']}</b><br>{dest['Descripción']}", max_width=250),
                          tooltip=dest["Destino"]).add_to(mapa)
            line_coords.append((dest["lat"], dest["lon"]))
        if len(line_coords)>1: PolyLine(line_coords,color="blue",weight=3).add_to(mapa)
        st.components.v1.html(mapa._repr_html_(), height=500)

        # PDF español e inglés
        pdf_buffer_es = generar_pdf(itinerario, idioma="es")
        pdf_buffer_en = generar_pdf(itinerario, idioma="en")
        st.download_button("📄 Descargar PDF en Español", pdf_buffer_es, "itinerario_arica.pdf")
        st.download_button("📄 Descargar PDF en Inglés", pdf_buffer_en, "itinerario_arica_en.pdf")

        # WhatsApp
        resumen = "\n".join([f"{i['Día']}: {i['Destino']} ({i['Tiempo estimado (h)']}h)" for i in itinerario])
        wa_link = f"https://api.whatsapp.com/send?text={urllib.parse.quote(resumen)}"
        st.markdown(f"[📱 Compartir por WhatsApp]({wa_link})")

        # Email
        subject = urllib.parse.quote("Mi Itinerario de Viaje - Arica y Parinacota")
        body = urllib.parse.quote(resumen)
        mail_link = f"mailto:?subject={subject}&body={body}"
        st.markdown(f"[✉️ Compartir por Email]({mail_link})")

