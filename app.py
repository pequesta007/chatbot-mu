from flask import Flask, request, jsonify
import json
import torch
import nltk
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer, util

# Descargar datos de NLTK (solo la primera vez)
nltk.download("punkt")
nltk.download("stopwords")

app = Flask(__name__)

DATA_FILE = "data.json"

# Diccionario de saludos
SALUDOS = {
    "hola": "¡Hola! ¿En qué puedo ayudarte con tu mascota? 😊",
    "hi": "¡Hola! ¿Cómo puedo ayudarte? 🐶",
    "qué tal": "¡Todo bien! ¿Tienes alguna consulta sobre tu mascota?",
    "q tal": "¡Hola! Dime en qué necesitas ayuda.",
    "cómo estás": "¡Estoy listo para ayudarte con cualquier consulta sobre mascotas! 🐾",
    "buenas": "¡Hola! ¿Cómo puedo ayudarte?"
}

# Lista de opciones disponibles
OPCIONES = [
    "Registro y gestión de mascotas",
    "Localización y reporte de pérdidas",
    "Escaneo de código QR",
    "Control Sanitario",
    "Ubicación de veterinarias",
    "Adopción y comunidad",
    "Soporte técnico"
]

# Cargar datos desde JSON
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
            textos, referencias = [], []
            for filename, sections in raw_data.items():
                for section, content in sections.items():
                    if isinstance(content, dict):
                        for sub_section, sub_content in content.items():
                            if isinstance(sub_content, list):
                                texto = " ".join(sub_content)  # Unir texto de listas
                                if len(texto) > 20:
                                    textos.append(texto)
                                    referencias.append(f"{filename} > {section} > {sub_section}")
                    elif isinstance(content, list):
                        texto = " ".join(content)
                        if len(texto) > 20:
                            textos.append(texto)
                            referencias.append(f"{filename} > {section}")
            return textos, referencias
    except Exception as e:
        print(f"❌ ERROR al cargar {DATA_FILE}: {e}")
        return [], []

# Cargar datos y modelo de embeddings
data, referencias = load_data()
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(data, convert_to_tensor=True) if data else None

# Buscar la mejor respuesta
def buscar_respuesta(pregunta):
    if not data or embeddings is None:
        return "No hay información disponible en la base de datos."
    
    pregunta_limpia = pregunta.lower().strip()
    
    # Manejo de saludos
    for saludo, respuesta in SALUDOS.items():
        if saludo in pregunta_limpia:
            return respuesta
    
    # Responder sobre opciones disponibles
    if "opciones" in pregunta_limpia:
        return "Aquí tienes las opciones disponibles: \n- " + "\n- ".join(OPCIONES)
    
    # Comparación semántica
    pregunta_emb = model.encode(pregunta, convert_to_tensor=True)
    similitudes = util.pytorch_cos_sim(pregunta_emb, embeddings)[0]
    umbral_similitud = 0.50
    mejores_indices = [i for i in range(len(similitudes)) if similitudes[i] > umbral_similitud]
    
    if not mejores_indices:
        return "No encontré una respuesta exacta, pero intenta reformular tu pregunta."
    
    idx_mejor = mejores_indices[torch.argmax(similitudes[mejores_indices]).item()]
    return data[idx_mejor]

# API para recibir preguntas y generar respuestas
@app.route("/ask", methods=["POST"])
def ask():
    user_input = request.json.get("question", "").strip()
    
    if not user_input:
        return jsonify({"response": "Por favor, ingresa una pregunta válida."})
    
    respuesta = buscar_respuesta(user_input)
    return jsonify({"response": respuesta})

if __name__ == "__main__":
    app.run(debug=True)
