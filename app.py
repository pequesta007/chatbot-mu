from flask import Flask, request, jsonify
import json
import re
import torch
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sentence_transformers import SentenceTransformer, util

# Descargar datos necesarios de nltk
nltk.download("punkt")
nltk.download("stopwords")

app = Flask(__name__)

# 📌 Cargar `data.json`
def load_data():
    try:
        with open("data.json", "r", encoding="utf-8") as f:
            return json.load(f)  # Retorna el diccionario completo
    except Exception as e:
        print(f"❌ ERROR al cargar data.json: {e}")
        return {}

data = load_data()

# 📌 Cargar modelo de embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")
stop_words = set(stopwords.words("spanish"))

# 📌 Preprocesar texto (minúsculas y limpieza de caracteres)
def preprocess_text(text):
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)  # Elimina signos de puntuación
    return text.strip()

# 📌 Extraer palabras clave de la pregunta
def extraer_palabras_clave(pregunta):
    palabras = word_tokenize(pregunta, language="spanish")
    palabras_clave = [palabra for palabra in palabras if palabra not in stop_words and palabra.isalpha()]
    return set(palabras_clave)

# 📌 Generar embeddings solo con fragmentos útiles
def generar_embeddings():
    textos = []
    mapeo_texto = []  # Guardar referencia del texto original
    for key, contenido in data.items():
        if isinstance(contenido, str):
            frases = contenido.split(". ")  # Dividir en frases manejables
            frases = [frase for frase in frases if len(frase) > 30]  # Filtrar frases muy cortas
            textos.extend(frases)
            mapeo_texto.extend([key] * len(frases))  # Asignar clave de origen a cada frase
    return textos, model.encode(textos, convert_to_tensor=True), mapeo_texto

textos, txt_embeddings, mapeo_texto = generar_embeddings()

# 📌 Buscar respuesta usando embeddings y palabras clave
def buscar_respuesta(pregunta):
    pregunta_emb = model.encode(pregunta, convert_to_tensor=True)
    similitudes = util.pytorch_cos_sim(pregunta_emb, txt_embeddings)[0]
    idx_mejor = torch.argmax(similitudes).item()
    mejor_respuesta = textos[idx_mejor]
    
    # 🔹 Extraer palabras clave de la pregunta
    palabras_clave_pregunta = extraer_palabras_clave(pregunta)
    palabras_clave_respuesta = extraer_palabras_clave(mejor_respuesta)
    
    # 🔹 Filtrar respuestas que no sean instrucciones claras
    palabras_relevantes = {"registrar", "registro", "mascota", "agregar", "formulario"}
    if not palabras_relevantes & palabras_clave_respuesta:
        return "No encontré una respuesta exacta, pero revisa la sección de registro en la app."  
    
    # 🔹 Limitar la respuesta a 2-3 oraciones relevantes
    oraciones = mejor_respuesta.split(". ")
    respuesta_corta = ". ".join(oraciones[:3])
    
    return respuesta_corta if similitudes[idx_mejor] > 0.3 else "Lo siento, no encontré información relevante."

# 📌 API para recibir preguntas y dar respuestas
@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("question", "").strip()
    
    if not user_input:
        return jsonify({"response": "Por favor, ingresa una pregunta válida."})
    
    respuesta = buscar_respuesta(user_input)
    return jsonify({"response": respuesta})

if __name__ == "__main__":
    app.run(debug=True)
