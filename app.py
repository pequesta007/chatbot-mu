from flask import Flask, request, jsonify
import json
import os
import difflib
import re

app = Flask(__name__)

# 🔹 Función para cargar `data.json`
def load_data():
    json_path = "data.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"contenido": "No se ha cargado ningún PDF aún."}

# 🔹 Función para dividir texto en oraciones manualmente
def dividir_en_oraciones(texto):
    return re.split(r'(?<=[.!?])\s+', texto)

# 🔹 Función para buscar la mejor respuesta
def buscar_respuesta(pregunta, base_de_texto):
    oraciones = dividir_en_oraciones(base_de_texto)
    mejor_coincidencia = difflib.get_close_matches(pregunta, oraciones, n=3, cutoff=0.2)
    
    if mejor_coincidencia:
        return reformular_respuesta(mejor_coincidencia[0])
    else:
        return "Lo siento, no encontré información relevante en los documentos." 

# 🔹 Función para reformular la respuesta
def reformular_respuesta(texto):
    return f"Según la información encontrada: {texto}"

# 🔹 Ruta para realizar preguntas al chatbot
@app.route("/ask", methods=["POST"])
def ask():
    question = request.json.get("question", "").lower()
    data = load_data()
    
    if "contenido" in data:
        respuesta = buscar_respuesta(question, data["contenido"])
        return jsonify({"response": respuesta})
    else:
        return jsonify({"response": "No tengo información suficiente para responder esa pregunta."})

if __name__ == "__main__":
    app.run(debug=True)
