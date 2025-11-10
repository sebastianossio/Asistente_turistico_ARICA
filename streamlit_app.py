import streamlit as st
import openai
import os

# Configura tu API Key
openai.api_key = os.getenv("OPENAI_API_KEY")
"},
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
import openai
import json
import re
with open("atractivos.json", "r", encoding="utf-8") as f:
    atractivos = json.load(f)
# --- Configuración OpenAI ---
openai.api_key = st.secrets["OPENAI_API_KEY"]

# --- Leer atractivos desde JSON ---
with open("atractivos.json","r",encoding="utf-8") as f:
    atractivos = json.load(f)

# --- Funciones ---
def distancia(a,b):
    return geodesic((a["lat"], a["lon"]),(b["lat"],b["lon"])).km

def agrupar_por_dia(destinos,dias):
    grupos = [[] for _ in range(dias)]
    destinos = sorted(destinos,key=lambda x:(x["lat"],x["lon"]))
    for idx,d in enumerate(destinos):
        grupos[idx%dias].append(d)
    for i,grupo in enumerate(grupos):
        if len(grupo)>1:
            ordenado = [grupo[0]]
            resto = grupo[1:]
            while resto:
                last = ordenado[-1]
                next_dest = min(resto,key=lambda x: distancia(last,x))
                ordenado.append(next_dest)
                resto.remove(next_dest)
            grupos[i] = ordenado
    return grupos

def generar_itinerario(destinos,dias):
    grupos = agrupar_por_dia(destinos,dias)
    itinerario=[]
    for i,dia_grupo in enumerate(grupos):
        for d in dia_grupo:
            itinerario.append({"Día":i+1,"Destino":d["nombre"],"Descripción":d["descripcion"],
                               "Tiempo estimado (h)":d["tiempo"],"lat":d["lat"],"lon":d["lon"],
                               "imagen_url":d["imagen_url"]})
    return itinerario

def responder_pregunta(pregunta):
    prompt = f"Actúa como guía turístico experto en Arica y Parinacota y responde claramente: {pregunta}. Menciona los nombres de los destinos tal como están en la lista."
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.6,
        max_tokens=400
    )
    texto = response.choices[0].text.strip()
    resultado=[]
    for linea in texto.split('\n'):
        encontrado=False
        for a in atractivos:
            if re.search(rf"\b{re.escape(a['nombre'])}\b", linea, re.IGNORECASE):
                resultado.append((linea,a["imagen_url"]))
                encontrado=True
                break
        if not encontrado:
            resultado.append((linea,None))
    return resultado

# --- Streamlit ---
st.set_page_config(page_title="Asistente Turístico Arica y Parinacota", layout="wide")
st.title("🏔️ Asistente Turístico Interactivo + Chatbot")

dias = st.number_input("Cantidad de días de visita", min_value=1, max_value=10, value=3)

st.subheader("Atractivos Turísticos")
seleccionados=[]
num_cols=3
cols = st.columns(num_cols)
for i,a in enumerate(atractivos):
    with cols[i%num_cols]:
        try:
            response=requests.get(a["imagen_url"])
            img_pil=PILImage.open(BytesIO(response.content))
            st.image(img_pil, caption=a["nombre"], use_column_width=True)
        except:
            st.text(a["nombre"])
        if st.checkbox(f"Seleccionar", key=a["nombre"]):
            seleccionados.append(a)

if st.button("Generar Itinerario"):
    if not seleccionados:
        st.warning("Selecciona al menos un destino.")
    else:
        itinerario=generar_itinerario(seleccionados,dias)
        st.dataframe(pd.DataFrame(itinerario))
        mapa=folium.Map(location=[-18.48,-70.32], zoom_start=8)
        line_coords=[]
        for dest in itinerario:
            folium.Marker([dest["lat"],dest["lon"]],popup=dest["Destino"],tooltip=dest["Destino"]).add_to(mapa)
            line_coords.append((dest["lat"],dest["lon"]))
        if len(line_coords)>1:
            PolyLine(line_coords,color="blue",weight=3).add_to(mapa)
        st.components.v1.html(mapa._repr_html_(),height=500)
        
        def generar_pdf(itinerario):
            buffer=BytesIO()
            doc=SimpleDocTemplate(buffer,pagesize=letter)
            styles=getSampleStyleSheet()
            elems=[Paragraph("Itinerario Turístico - Arica y Parinacota",styles['Title']),Spacer(1,12)]
            for item in itinerario:
                elems.append(Paragraph(f"Día {item['Día']}: {item['Destino']} ({item['Tiempo estimado (h)']}h)",styles['Heading2']))
                elems.append(Paragraph(item['Descripción'],styles['BodyText']))
                try:
                    response=requests.get(item["imagen_url"])
                    img_pil=PILImage.open(BytesIO(response.content))
                    img_pil.save(f"/tmp/{item['Destino']}.png")
                    elems.append(Image(f"/tmp/{item['Destino']}.png", width=400,height=300))
                except:
                    elems.append(Paragraph("Imagen no disponible",styles['BodyText']))
                elems.append(Spacer(1,12))
            ruta_texto=" -> ".join([i['Destino'] for i in itinerario])
            elems.append(Paragraph(f"Ruta sugerida: {ruta_texto}",styles['Normal']))
            doc.build(elems)
            buffer.seek(0)
            return buffer
        
        pdf_buffer=generar_pdf(itinerario)
        st.download_button("📄 Descargar PDF con fotos y ruta",pdf_buffer,"itinerario_arica.pdf")

st.subheader("💬 Chatbot turístico con imágenes")
pregunta = st.text_input("Escribe tu pregunta sobre Arica y Parinacota:")
if st.button("Responder"):
    if pregunta:
        respuesta=responder_pregunta(pregunta)
        for linea,img_url in respuesta:
            st.markdown(linea)
            if img_url:
                try:
                    response=requests.get(img_url)
                    img_pil=PILImage.open(BytesIO(response.content))
                    st.image(img_pil,width=300)
                except:
                    pass


