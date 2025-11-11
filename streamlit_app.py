import streamlit as st
import openai
import os

# streamlit_app.py

destinos = [
    {"nombre": "Morro de Arica", "lat": -18.477, "lon": -70.330, "tipo": "Cultura", "tiempo": 1.5,
     "region": "Ciudad", "descripcion": "Icono histórico con vista panorámica de la ciudad.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/2/2c/Morro_de_Arica.jpg"},
    {"nombre": "Playa El Laucho", "lat": -18.486, "lon": -70.318, "tipo": "Playa", "tiempo": 2,
     "region": "Costa", "descripcion": "Playa tranquila ideal para relajarse y tomar sol.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Playa_El_Laucho_Arica.jpg"},
    {"nombre": "Cuevas de Anzota", "lat": -18.533, "lon": -70.353, "tipo": "Naturaleza", "tiempo": 1.5,
     "region": "Costa", "descripcion": "Cuevas naturales con formaciones rocosas únicas.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/7/7e/Cuevas_de_Anzota.jpg"},
    {"nombre": "Playa Chinchorro", "lat": -18.466, "lon": -70.307, "tipo": "Playa", "tiempo": 2.5,
     "region": "Costa", "descripcion": "Famosa playa con actividades de pesca y deportes acuáticos.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/3/3c/Playa_Chinchorro_Arica.jpg"},
    {"nombre": "Museo de Sitio Colón 10", "lat": -18.480, "lon": -70.317, "tipo": "Cultura", "tiempo": 1,
     "region": "Ciudad", "descripcion": "Museo arqueológico con vestigios de culturas prehispánicas.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/8/8c/Museo_de_Sitio_Colon_10_Arica.jpg"},
    {"nombre": "Humedal del Río Lluta", "lat": -18.425, "lon": -70.324, "tipo": "Naturaleza", "tiempo": 2,
     "region": "Costa", "descripcion": "Ecosistema protegido, ideal para observación de aves.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/1/1e/Humedal_del_Rio_Lluta_Arica.jpg"},
    {"nombre": "Museo de Azapa", "lat": -18.52, "lon": -70.33, "tipo": "Cultura", "tiempo": 1.5,
     "region": "Valle", "descripcion": "Museo arqueológico con momias y artefactos de la cultura Chinchorro.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/e/ea/Museo_Azapa_Arica.jpg"},
    {"nombre": "Valle de Lluta", "lat": -18.43, "lon": -70.32, "tipo": "Naturaleza", "tiempo": 2,
     "region": "Valle", "descripcion": "Hermoso valle con agricultura tradicional y paisajes naturales.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/1/12/Valle_de_Lluta_Arica.jpg"},
    {"nombre": "Catedral de San Marcos", "lat": -18.478, "lon": -70.328, "tipo": "Cultura", "tiempo": 1,
     "region": "Ciudad", "descripcion": "Imponente catedral del centro de Arica, arquitectura neoclásica.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/0/02/Catedral_de_San_Marcos_Arica.jpg"},
    {"nombre": "La Ex Aduana", "lat": -18.479, "lon": -70.329, "tipo": "Cultura", "tiempo": 1,
     "region": "Ciudad", "descripcion": "Edificio histórico que albergó la aduana de la ciudad.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/3/3e/Ex_Aduana_Arica.jpg"},
    {"nombre": "Presencias Tutelares", "lat": -18.48, "lon": -70.33, "tipo": "Cultura", "tiempo": 1.5,
     "region": "Ciudad", "descripcion": "Sitio arqueológico con petroglifos de gran valor cultural.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/4/4d/Presencias_Tutelares_Arica.jpg"},
    {"nombre": "Putre", "lat": -18.195, "lon": -69.559, "tipo": "Cultura", "tiempo": 3,
     "region": "Altiplano", "descripcion": "Pueblo tradicional a orillas del altiplano con cultura Aymara.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/d/d3/Putre_village.jpg"},
    {"nombre": "Parque Nacional Lauca", "lat": -18.243, "lon": -69.352, "tipo": "Naturaleza", "tiempo": 4,
     "region": "Altiplano", "descripcion": "Parque con volcanes, lagunas y fauna típica de la zona.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/2/2c/Parque_Nacional_Lauca_Chile.jpg"},
    {"nombre": "Lago Chungará", "lat": -18.25, "lon": -69.15, "tipo": "Naturaleza", "tiempo": 2,
     "region": "Altiplano", "descripcion": "Lago a gran altitud con vistas espectaculares y flamencos.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/5/5c/Lago_Chungara.jpg"},
    {"nombre": "Salar de Surire", "lat": -18.85, "lon": -69.05, "tipo": "Naturaleza", "tiempo": 3.5,
     "region": "Altiplano", "descripcion": "Salar impresionante con fauna típica del altiplano.",
     "imagen": "https://upload.wikimedia.org/wikipedia/commons/7/74/Salar_de_Surire.jpg"}
]

