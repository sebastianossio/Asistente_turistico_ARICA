import streamlit as st
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
import datetime

# =========================
# CONFIG
# =========================
st.set_page_config(page_title="Asistente Turístico - Arica", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "images"

# =========================
# i18n (TRADUCCIÓN TOTAL)
# =========================
I18N = {
    "Español": {
        "app_title": "🌅 Guía Turística - Arica y Parinacota",
        "app_subtitle": "Explora la región con itinerarios personalizados por secciones geográficas.",
        "sidebar_title": "🧭 Configura tu viaje",
        "days_label": "¿Cuántos días te quedarás en la región?",
        "language_label": "🌐 Idioma",
        "travelmode_label": "🚗 Modo de traslado",
        "travelmode_driving": "Auto",
        "travelmode_walking": "Caminando",
        "travelmode_transit": "Transporte público",
        "travelmode_bicycling": "Bicicleta",

        "currency_title": "💱 Conversor de divisas",
        "amount_label": "Monto",
        "from_label": "De",
        "to_label": "A",
        "convert_btn": "Convertir",
        "result_label": "Resultado",
        "rate_label": "Tasa",
        "currency_error": "No se pudo obtener la tasa. Intenta de nuevo.",

        "section_city": "Ciudad",
        "section_coast": "Costa",
        "section_valley": "Valle",
        "section_altiplano": "Altiplano",

        "add_to_itinerary": "Añadir al itinerario",
        "map_title": "🗺️ Mapa de tu ruta turística con recorrido",
        "itinerary_title": "🗓️ Itinerario sugerido",
        "open_gmaps": "🧭 Abrir ruta detallada en Google Maps",
        "generate_pdf": "📄 Generar PDF",
        "download_pdf": "Descargar PDF Turístico",
        "select_at_least_one": "Selecciona al menos un atractivo turístico para generar tu itinerario.",

        "hours": "hrs",
        "distance_next": "Distancia al siguiente",
        "recommendation": "Recomendación: sigue el orden propuesto para reducir traslados.",
        "footer_tagline": "Naturaleza • Cultura • Aventura",
        "generated_on": "Generado el",
        "good_trip": "¡Buen viaje!",
        "auto_summary": "Este itinerario fue generado automáticamente en base a los destinos seleccionados y un criterio de cercanía.",
    },
    "English": {
        "app_title": "🌅 Tourist Guide - Arica & Parinacota",
        "app_subtitle": "Explore the region with personalized itineraries by area.",
        "sidebar_title": "🧭 Trip settings",
        "days_label": "How many days will you stay in the region?",
        "language_label": "🌐 Language",
        "travelmode_label": "🚗 Travel mode",
        "travelmode_driving": "Driving",
        "travelmode_walking": "Walking",
        "travelmode_transit": "Public transit",
        "travelmode_bicycling": "Bicycling",

        "currency_title": "💱 Currency converter",
        "amount_label": "Amount",
        "from_label": "From",
        "to_label": "To",
        "convert_btn": "Convert",
        "result_label": "Result",
        "rate_label": "Rate",
        "currency_error": "Could not fetch the rate. Try again.",

        "section_city": "City",
        "section_coast": "Coast",
        "section_valley": "Valley",
        "section_altiplano": "Highlands",

        "add_to_itinerary": "Add to itinerary",
        "map_title": "🗺️ Route map",
        "itinerary_title": "🗓️ Suggested itinerary",
        "open_gmaps": "🧭 Open detailed route in Google Maps",
        "generate_pdf": "📄 Generate PDF",
        "download_pdf": "Download Tourist PDF",
        "select_at_least_one": "Select at least one place to generate your itinerary.",

        "hours": "hrs",
        "distance_next": "Distance to next",
        "recommendation": "Tip: follow the suggested order to reduce travel time.",
        "footer_tagline": "Nature • Culture • Adventure",
        "generated_on": "Generated on",
        "good_trip": "Have a great trip!",
        "auto_summary": "This itinerary was generated automatically based on your selected places and a proximity rule.",
    },
    "Português": {
        "app_title": "🌅 Guia Turístico - Arica e Parinacota",
        "app_subtitle": "Explore a região com roteiros personalizados por área.",
        "sidebar_title": "🧭 Configurar viagem",
        "days_label": "Quantos dias você ficará na região?",
        "language_label": "🌐 Idioma",
        "travelmode_label": "🚗 Modo de deslocamento",
        "travelmode_driving": "Carro",
        "travelmode_walking": "A pé",
        "travelmode_transit": "Transporte público",
        "travelmode_bicycling": "Bicicleta",

        "currency_title": "💱 Conversor de moedas",
        "amount_label": "Valor",
        "from_label": "De",
        "to_label": "Para",
        "convert_btn": "Converter",
        "result_label": "Resultado",
        "rate_label": "Taxa",
        "currency_error": "Não foi possível obter a taxa. Tente novamente.",

        "section_city": "Cidade",
        "section_coast": "Costa",
        "section_valley": "Vale",
        "section_altiplano": "Altiplano",

        "add_to_itinerary": "Adicionar ao roteiro",
        "map_title": "🗺️ Mapa da rota",
        "itinerary_title": "🗓️ Roteiro sugerido",
        "open_gmaps": "🧭 Abrir rota detalhada no Google Maps",
        "generate_pdf": "📄 Gerar PDF",
        "download_pdf": "Baixar PDF Turístico",
        "select_at_least_one": "Selecione pelo menos um lugar para gerar o roteiro.",

        "hours": "hrs",
        "distance_next": "Distância para o próximo",
        "recommendation": "Dica: siga a ordem sugerida para reduzir deslocamentos.",
        "footer_tagline": "Natureza • Cultura • Aventura",
        "generated_on": "Gerado em",
        "good_trip": "Boa viagem!",
        "auto_summary": "Este roteiro foi gerado automaticamente com base nos locais selecionados e um critério de proximidade.",
    },
}

REGION_MAP = {
    "Español": {"Ciudad": "Ciudad", "Costa": "Costa", "Valle": "Valle", "Altiplano": "Altiplano"},
    "English": {"Ciudad": "City", "Costa": "Coast", "Valle": "Valley", "Altiplano": "Highlands"},
    "Português": {"Ciudad": "Cidade", "Costa": "Costa", "Valle": "Vale", "Altiplano": "Altiplano"},
}
TYPE_MAP = {
    "Español": {"Cultura": "Cultura", "Playa": "Playa", "Naturaleza": "Naturaleza"},
    "English": {"Cultura": "Culture", "Playa": "Beach", "Naturaleza": "Nature"},
    "Português": {"Cultura": "Cultura", "Playa": "Praia", "Naturaleza": "Natureza"},
}

DESC_I18N = {
    "Morro de Arica": {
        "English": "Historic landmark with panoramic views of the city and coastline.",
        "Português": "Marco histórico com vista panorâmica da cidade e do litoral.",
    },
    "Cuevas de Anzota": {
        "English": "Coastal caves and rock formations along a scenic seaside trail.",
        "Português": "Grutas costeiras e formações rochosas em uma trilha cênica à beira-mar.",
    },
    "Museo de Azapa": {
        "English": "Archaeological museum featuring Chinchorro heritage and ancient artifacts.",
        "Português": "Museu arqueológico com patrimônio Chinchorro e artefatos antigos.",
    },
    "Valle de Lluta": {
        "English": "Traditional agricultural valley with rural scenery and local culture.",
        "Português": "Vale agrícola tradicional com paisagens rurais e cultura local.",
    },
    "Valle de Azapa": {
        "English": "Cultural and agricultural valley known for local products and heritage.",
        "Português": "Vale cultural e agrícola conhecido por produtos locais e patrimônio.",
    },
    "Catedral de San Marcos": {
        "English": "Historic cathedral in the city center, a key landmark in Arica.",
        "Português": "Catedral histórica no centro da cidade, um marco importante de Arica.",
    },
    "Playa El Laucho": {
        "English": "Calm beach near the city—great for relaxing and swimming.",
        "Português": "Praia tranquila perto da cidade—ideal para relaxar e nadar.",
    },
    "Playa La Lisera": {
        "English": "Popular beach close to downtown, ideal for a beach day.",
        "Português": "Praia popular perto do centro, ideal para passar o dia.",
    },
    "Humedal del Río Lluta": {
        "English": "Coastal wetland ideal for birdwatching and nature observation.",
        "Português": "Área úmida costeira ideal para observação de aves e natureza.",
    },
    "La Ex Aduana": {
        "English": "Historic customs building and landmark near the waterfront area.",
        "Português": "Antiga alfândega histórica e ponto turístico perto da orla.",
    },
    "Putre": {
        "English": "Andean town with Aymara culture, high-altitude landscapes and tradition.",
        "Português": "Cidade andina com cultura Aymara, paisagens de altitude e tradição.",
    },
    "Parque Nacional Lauca": {
        "English": "National park with volcanoes, lagoons and unique highland wildlife.",
        "Português": "Parque nacional com vulcões, lagoas e fauna típica do altiplano.",
    },
    "Salar de Surire": {
        "English": "Highland salt flat known for wildlife and striking landscapes.",
        "Português": "Salar do altiplano conhecido pela fauna e paisagens impressionantes.",
    },
}

def t(key: str) -> str:
    lang = st.session_state.get("lang", "Español")
    return I18N.get(lang, I18N["Español"]).get(key, key)

def tr_region(valor: str) -> str:
    lang = st.session_state.get("lang", "Español")
    return REGION_MAP.get(lang, REGION_MAP["Español"]).get(valor, valor)

def tr_type(valor: str) -> str:
    lang = st.session_state.get("lang", "Español")
    return TYPE_MAP.get(lang, TYPE_MAP["Español"]).get(valor, valor)

def tr_desc(nombre: str, descripcion_original: str) -> str:
    lang = st.session_state.get("lang", "Español")
    if lang == "Español":
        return descripcion_original
    return DESC_I18N.get(nombre, {}).get(lang, descripcion_original)

# =========================
# DIVISAS (Frankfurter)
# =========================
@st.cache_data(ttl=60 * 60)
def erapi_rates(base: str) -> dict:
    """
    Open Access ExchangeRate-API (sin key).
    Docs: https://open.er-api.com/v6/latest/USD (cambia USD por la base).  :contentReference[oaicite:2]{index=2}
    """
    url = f"https://open.er-api.com/v6/latest/{base}"
    r = requests.get(url, timeout=15)
    r.raise_for_status()
    data = r.json()
    if data.get("result") != "success":
        raise ValueError(f"ER-API error: {data.get('error-type', 'unknown')}")
    return data["rates"]  # dict: { "USD":1, "CLP":..., "ARS":..., ... }

def convertir_divisa(monto: float, moneda_origen: str, moneda_destino: str) -> tuple[float, str]:
    if moneda_origen == moneda_destino:
        return monto, f"1 {moneda_origen} = 1 {moneda_destino}"

    rates = erapi_rates(moneda_origen)
    if moneda_destino not in rates:
        raise ValueError(f"Moneda destino no soportada: {moneda_destino}")

    tasa = float(rates[moneda_destino])  # 1 ORIGEN = tasa DESTINO
    convertido = monto * tasa
    detalle = f"1 {moneda_origen} = {tasa:.6f} {moneda_destino} (open.er-api.com)"
    return convertido, detalle

@st.cache_data(ttl=60 * 60)
def monedas_disponibles() -> list[str]:
    # usamos USD solo para obtener el set completo de monedas soportadas por el endpoint
    rates = erapi_rates("USD")
    codigos = sorted(rates.keys())
    return codigos

# =========================
# IMÁGENES (URL o local)
# =========================
LOCAL_IMAGE_BY_NAME = {
    "Morro de Arica": "morro-de-arica-1.jpg",
    "Cuevas de Anzota": "Cuevas de Anzota.jpg",
    "Museo de Azapa": "Museo arqueologico San Miguel de Azapa.jpg",
    "Valle de Lluta": "Valle de lluta.jpg",
    "Valle de Azapa": "Valle de Azapa.jpeg",
    "Catedral de San Marcos": "Catedral de San Marcos.jpeg",
    "Playa La Lisera": "Playa-La-Lisera-Arica.jpg",
}

def image_override_path(nombre: str):
    fn = LOCAL_IMAGE_BY_NAME.get(nombre)
    if not fn:
        return None
    p = IMAGES_DIR / fn
    return str(p) if p.exists() else None

def cargar_imagen_para_ui(lugar: dict):
    ref = image_override_path(lugar.get("nombre", "")) or lugar.get("imagen", "")
    try:
        if isinstance(ref, str) and ref.startswith("http"):
            r = requests.get(ref, timeout=12)
            r.raise_for_status()
            return Image.open(BytesIO(r.content)).convert("RGB")
        return Image.open(ref).convert("RGB")
    except:
        return None

# =========================
# DATOS (DESTINOS)
# =========================

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "images"

def img(nombre_archivo):
    return str(IMAGES_DIR / nombre_archivo)
destinos = [
    {"nombre": "Morro de Arica", "lat": -18.47962, "lon": -70.32394, "tipo": "Cultura", "tiempo": 1.5,
     "region": "Ciudad", "descripcion": "Icono histórico con vista panorámica de la ciudad.",
     "imagen": img("morro-de-arica-1.jpg")},

    {"nombre": "Playa El Laucho", "lat": -18.488000, "lon": -70.327320, "tipo": "Playa", "tiempo": 2,
     "region": "Costa", "descripcion": "Playa tranquila ideal para relajarse y tomar sol.",
     "imagen": img("Playa el Laucho.jpg")},

    {"nombre": "Playa La Lisera", "lat": -18.49303, "lon": -70.32565, "tipo": "Playa", "tiempo": 2,
     "region": "Costa", "descripcion": "Playa muy visitada, ideal para baño y descanso cerca del centro.",
     "imagen": img("Playa-La-Lisera-Arica.jpg")},

    {"nombre": "Cuevas de Anzota", "lat": -18.549914, "lon": -70.331249, "tipo": "Naturaleza", "tiempo": 1.5,
     "region": "Costa", "descripcion": "Cuevas naturales con formaciones rocosas únicas.",
     "imagen": img("Cuevas de Anzota.jpg")},

    {"nombre": "Humedal del Río Lluta", "lat": -18.425, "lon": -70.324, "tipo": "Naturaleza", "tiempo": 2,
     "region": "Costa", "descripcion": "Ecosistema protegido, ideal para observación de aves.",
     "imagen": img("Humedal-Rio-Lluta-Region-de-Arica-y-Parinacota.jpg")},

    {"nombre": "Museo de Azapa", "lat": -18.516474, "lon": -70.181149, "tipo": "Cultura", "tiempo": 1.5,
     "region": "Valle", "descripcion": "Museo arqueológico con momias y cultura Chinchorro.",
     "imagen": img("Museo arqueologico San Miguel de Azapa.jpg")},

    {"nombre": "Valle de Lluta", "lat": -18.40130, "lon": -70.30010, "tipo": "Naturaleza", "tiempo": 2,
     "region": "Valle", "descripcion": "Hermoso valle con agricultura tradicional y paisajes naturales.",
     "imagen": img("Valle de lluta.jpg")},

    {"nombre": "Valle de Azapa", "lat": -18.51690, "lon": -70.18230, "tipo": "Naturaleza", "tiempo": 2,
     "region": "Valle", "descripcion": "Valle destacado por su agricultura y patrimonio cultural.",
     "imagen": img("Valle de Azapa.jpeg")},

    {"nombre": "Catedral de San Marcos", "lat": -18.47897, "lon": -70.32072, "tipo": "Cultura", "tiempo": 1,
     "region": "Ciudad", "descripcion": "Imponente catedral del centro de Arica, arquitectura neoclásica.",
     "imagen": img("Catedral-San-Marcos.jpeg")},

    {"nombre": "La Ex Aduana", "lat": -18.477185, "lon": -70.321130, "tipo": "Cultura", "tiempo": 1,
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


# =========================
# FUNCIONES: Itinerario + Google Maps
# =========================
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

def generar_link_google_maps_desde_itinerario(itinerario, travelmode="driving"):
    orden = []
    for dia in itinerario.keys():
        orden.extend(itinerario[dia])

    if len(orden) < 2:
        return None

    def coord(d):
        return f"{d['lat']:.6f},{d['lon']:.6f}"

    origin = coord(orden[0])
    destination = coord(orden[-1])
    waypoints = [coord(d) for d in orden[1:-1]]

    if len(waypoints) > 23:
        waypoints = waypoints[:23]

    waypoints_str = ""
    if waypoints:
        waypoints_str = "&waypoints=" + "%7C".join(waypoints)

    url = (
        "https://www.google.com/maps/dir/?api=1"
        f"&origin={origin}"
        f"&destination={destination}"
        f"{waypoints_str}"
        f"&travelmode={travelmode}"
        "&dir_action=navigate"
    )
    return url

# =========================
# PDF (Diseño Pro + Fotos)
# =========================
def generar_pdf_lujo(itinerario, lang):
    def limpiar_texto(texto):
        if texto is None:
            return ""
        return str(texto).encode("latin-1", "ignore").decode("latin-1")

    colores_region_local = {
        "Ciudad": "#FFB199",
        "Costa": "#9AD9FF",
        "Valle": "#A6F3A6",
        "Altiplano": "#E0B3FF",
    }

    def hex_to_rgb(h):
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    def imagen_a_jpg_temp(lugar):
        ref = image_override_path(lugar.get("nombre", "")) or lugar.get("imagen", "")
        try:
            if isinstance(ref, str) and ref.startswith("http"):
                r = requests.get(ref, timeout=15)
                r.raise_for_status()
                img_pil = Image.open(BytesIO(r.content))
            else:
                img_pil = Image.open(ref)
            img_pil = img_pil.convert("RGB")
            img_pil.thumbnail((1200, 1200))
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            tmp_path = tmp.name
            tmp.close()
            img_pil.save(tmp_path, "JPEG", quality=88)
            return tmp_path
        except:
            return None

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

    # Portada
    pdf.add_page()
    pdf.set_fill_color(248, 248, 248)
    pdf.rect(0, 0, 210, 297, style="F")

    pdf.set_text_color(25, 25, 25)
    pdf.set_font("Arial", "B", 30)
    pdf.ln(18)
    pdf.cell(0, 12, limpiar_texto(I18N[lang]["app_title"].replace("🌅 ", "")), ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 7, limpiar_texto(I18N[lang]["app_subtitle"]), ln=True, align="C")

    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 7, limpiar_texto(f"{I18N[lang]['generated_on']} {datetime.datetime.now().strftime('%d-%m-%Y')}"), ln=True, align="C")

    hero_img = None
    for _, lugares in itinerario.items():
        if lugares:
            hero_img = imagen_a_jpg_temp(lugares[0])
            break

    if hero_img:
        x, y, w, h = 18, 80, 174, 135
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(235, 235, 235)
        pdf.rect(x, y, w, h, style="FD")
        try:
            pdf.image(hero_img, x=x + 6, y=y + 6, w=w - 12)
        except:
            pass

    pdf.set_y(270)
    pdf.set_fill_color(30, 30, 30)
    pdf.rect(0, 270, 210, 27, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, limpiar_texto(I18N[lang]["footer_tagline"]), ln=True, align="C")

    # Itinerario
    for dia, lugares in itinerario.items():
        pdf.add_page()
        pdf.set_fill_color(30, 30, 30)
        pdf.rect(0, 0, 210, 22, style="F")
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Arial", "B", 18)
        pdf.set_xy(10, 6)
        pdf.cell(0, 10, limpiar_texto(dia), ln=False)

        pdf.ln(26)
        pdf.set_text_color(60, 60, 60)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 6, limpiar_texto(I18N[lang]["recommendation"]))
        pdf.ln(2)

        for i, lugar in enumerate(lugares):
            region = lugar.get("region", "")
            color_hex = colores_region_local.get(region, "#FFFFFF")
            r, g, b = hex_to_rgb(color_hex)

            card_x, card_w, card_h = 10, 190, 62
            start_y = pdf.get_y()
            if start_y + card_h > 280:
                pdf.add_page()
                pdf.ln(8)
                start_y = pdf.get_y()

            pdf.set_draw_color(230, 230, 230)
            pdf.set_fill_color(255, 255, 255)
            pdf.rect(card_x, start_y, card_w, card_h, style="FD")

            pdf.set_fill_color(r, g, b)
            pdf.rect(card_x, start_y, 6, card_h, style="F")

            img_temp = imagen_a_jpg_temp(lugar)
            img_x, img_y, img_w, img_h = card_x + 10, start_y + 8, 52, 46
            pdf.set_draw_color(240, 240, 240)
            pdf.rect(img_x, img_y, img_w, img_h, style="D")
            if img_temp:
                try:
                    pdf.image(img_temp, x=img_x, y=img_y, w=img_w, h=img_h)
                except:
                    pass

            text_x = img_x + img_w + 10
            text_y = start_y + 8
            pdf.set_xy(text_x, text_y)

            nombre = lugar.get("nombre", "")
            tipo = tr_type(lugar.get("tipo", ""))
            reg_tr = tr_region(region)
            desc = tr_desc(nombre, lugar.get("descripcion", ""))

            pdf.set_text_color(25, 25, 25)
            pdf.set_font("Arial", "B", 13)
            pdf.multi_cell(0, 6, limpiar_texto(nombre))

            pdf.set_text_color(80, 80, 80)
            pdf.set_font("Arial", "", 10)
            pdf.set_x(text_x)
            pdf.cell(0, 5, limpiar_texto(f"{tipo}  |  {lugar.get('tiempo','')} {I18N[lang]['hours']}  |  {reg_tr}"), ln=True)

            pdf.set_x(text_x)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 5, limpiar_texto(desc[:220]))

            if i < len(lugares) - 1:
                try:
                    dist = geodesic(
                        (lugar["lat"], lugar["lon"]),
                        (lugares[i + 1]["lat"], lugares[i + 1]["lon"])
                    ).km
                    pdf.set_x(text_x)
                    pdf.set_text_color(60, 60, 60)
                    pdf.set_font("Arial", "I", 9)
                    pdf.cell(0, 5, limpiar_texto(f"{I18N[lang]['distance_next']}: {dist:.1f} km"), ln=True)
                except:
                    pass

            pdf.ln(6)

    # Cierre
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(25, 25, 25)
    pdf.ln(20)
    pdf.cell(0, 10, limpiar_texto(I18N[lang]["good_trip"]), ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 7, limpiar_texto(I18N[lang]["auto_summary"]), align="C")

    filename = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    pdf.output(filename)
    return filename

# =========================
# INTERFAZ
# =========================
# Sidebar: idioma + días + modo + divisas
st.sidebar.header(t("sidebar_title"))
lang = st.sidebar.selectbox(t("language_label"), ["Español", "English", "Português"], index=0)
st.session_state["lang"] = lang

dias = st.sidebar.slider(t("days_label"), 1, 14, 3)

modo_viaje = st.sidebar.selectbox(
    t("travelmode_label"),
    ["driving", "walking", "transit", "bicycling"],
    index=0,
    format_func=lambda x: {
        "driving": t("travelmode_driving"),
        "walking": t("travelmode_walking"),
        "transit": t("travelmode_transit"),
        "bicycling": t("travelmode_bicycling"),
    }[x],
)

st.sidebar.divider()
st.sidebar.subheader(t("currency_title"))

monto = st.sidebar.number_input(t("amount_label"), min_value=0.0, value=100.0, step=10.0)

# Lista de monedas soportadas (incluye ARS y CLP) :contentReference[oaicite:3]{index=3}
codigos = monedas_disponibles()

# Sugerencia: deja un set acotado + opción "Ver todas"
ver_todas = st.sidebar.checkbox("Ver todas las monedas", value=False)
if not ver_todas:
    preferidas = ["CLP", "USD", "EUR", "BRL", "ARS"]
    codigos_ui = [c for c in preferidas if c in codigos]
else:
    codigos_ui = codigos

c1, c2 = st.sidebar.columns(2)
with c1:
    moneda_origen = st.selectbox(t("from_label"), codigos_ui, index=codigos_ui.index("USD") if "USD" in codigos_ui else 0)
with c2:
    # evita que por defecto quede igual
    idx_default = codigos_ui.index("CLP") if "CLP" in codigos_ui else (1 if len(codigos_ui) > 1 else 0)
    moneda_destino = st.selectbox(t("to_label"), codigos_ui, index=idx_default)
if st.sidebar.button(t("convert_btn")):
    try:
        convertido, detalle = convertir_divisa(monto, moneda_origen, moneda_destino)
        st.sidebar.success(
            f"{t('result_label')}: {monto:,.2f} {moneda_origen} → {convertido:,.2f} {moneda_destino}\n{detalle}"
        )
    except Exception as e:
        st.sidebar.error(f"{t('currency_error')}\n\nDetalle: {e}")
        st.sidebar.caption("Rates by Exchange Rate API (open access)")

# Título principal
st.title(t("app_title"))
st.markdown(t("app_subtitle"))

# Destinos por sección
destinos_seleccionados = []

for seccion in ["Ciudad", "Costa", "Valle", "Altiplano"]:
    titulo = {
        "Ciudad": t("section_city"),
        "Costa": t("section_coast"),
        "Valle": t("section_valley"),
        "Altiplano": t("section_altiplano"),
    }[seccion]
    st.subheader(titulo)

    lugares_seccion = [d for d in destinos if d["region"] == seccion]
    cols_por_fila = 3

    for i in range(0, len(lugares_seccion), cols_por_fila):
        fila = st.columns(min(cols_por_fila, len(lugares_seccion) - i))
        for j, lugar in enumerate(lugares_seccion[i:i + cols_por_fila]):
            with fila[j]:
                img_pil = cargar_imagen_para_ui(lugar)
                if img_pil is not None:
                    st.image(img_pil, use_column_width=True)

                st.markdown(f"**{lugar['nombre']}** ({tr_type(lugar['tipo'])})")
                st.markdown(f"🕓 {lugar['tiempo']} {t('hours')}")
                st.markdown(tr_desc(lugar["nombre"], lugar["descripcion"]))

                if st.checkbox(t("add_to_itinerary"), key=f"chk_{lugar['nombre']}"):
                    destinos_seleccionados.append(lugar)

# Mapa + Itinerario + Google Maps + PDF
if destinos_seleccionados:
    itinerario = generar_itinerario_por_cercania(destinos_seleccionados, dias)

    st.subheader(t("map_title"))
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

    st.subheader(t("itinerary_title"))
    for dia, lugares in itinerario.items():
        st.markdown(f"### {dia}")
        for lugar in lugares:
            st.markdown(f"**{lugar['nombre']}** ({tr_type(lugar['tipo'])})")
            st.markdown(f"🕓 {lugar['tiempo']} {t('hours')}")
            st.markdown(tr_desc(lugar["nombre"], lugar["descripcion"]))
        st.divider()

    ruta_url = generar_link_google_maps_desde_itinerario(itinerario, travelmode=modo_viaje)
    if ruta_url:
        st.markdown(f"🧭 [{t('open_gmaps')}]({ruta_url})", unsafe_allow_html=True)

    if st.button(t("generate_pdf")):
        pdf_path = generar_pdf_lujo(itinerario, lang=st.session_state["lang"])
        with open(pdf_path, "rb") as f:
            st.download_button(
                t("download_pdf"),
                f,
                file_name="Itinerario_Turistico_Arica_Lujo.pdf"
            )
else:
    st.info(t("select_at_least_one"))


