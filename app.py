from flask import Flask, request, jsonify
import json
import os
import difflib

app = Flask(__name__)

# 🔹 Función para cargar `data.json`
def load_data():
    json_path = "data.json"
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"contenido": "No se ha cargado ningún PDF aún."}

# 🔹 Función para buscar la mejor respuesta en `data.json`
def buscar_respuesta(pregunta, base_de_texto):
    lineas = base_de_texto.split(". ")  # Dividir en oraciones
    mejor_coincidencia = difflib.get_close_matches(pregunta, lineas, n=1, cutoff=0.3)
    return mejor_coincidencia[0] if mejor_coincidencia else "No encontré información relevante."

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
