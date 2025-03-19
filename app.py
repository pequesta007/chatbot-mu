from flask import Flask, request, jsonify
import json
import re
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# 🔹 Función para limpiar texto
def clean_text(text):
    text = text.replace("\n", " ")
    text = re.sub(r"✅|☑️|•|►|📌", "", text)  # Elimina caracteres especiales
    text = re.sub(r'\s+', ' ', text).strip()  # Normaliza espacios
    return text

# 🔹 Función para buscar la mejor respuesta
def search_best_match(question, data):
    all_sentences = []
    metadata = []

    for pdf, pages in data.items():
        for page, text in pages.items():
            sentences = text.split(". ")  # Divide en frases
            for sentence in sentences:
                cleaned_sentence = clean_text(sentence)
                all_sentences.append(cleaned_sentence)
                metadata.append((pdf, page))

    if not all_sentences:
        return {"response": "No tengo información suficiente para responder esa pregunta.", "pdf": None, "page": None}

    # 🔹 Vectorización y búsqueda semántica
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform([question] + all_sentences)
    question_vector = vectors[0]
    text_vectors = vectors[1:]

    similarities = cosine_similarity(question_vector, text_vectors).flatten()
    best_idx = np.argmax(similarities)
    best_match = all_sentences[best_idx]
    best_pdf, best_page = metadata[best_idx]

    # 🔹 Filtrar si la coincidencia es baja (< 0.3)
    if similarities[best_idx] < 0.3:
        return {"response": "No tengo información suficiente para responder esa pregunta.", "pdf": None, "page": None}

    # 🔹 Mejorar la respuesta: extraer solo la parte más relevante
    keywords = question.lower().split()
    refined_sentences = [s for s in best_match.split(". ") if any(k in s.lower() for k in keywords)]

    if refined_sentences:
        best_match = ". ".join(refined_sentences)  # Une las frases relacionadas

    return {
        "response": best_match,
        "pdf": best_pdf,
        "page": best_page
    }

# 🔹 Función para cargar el JSON estructurado
def load_data(json_path="data.json"):
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

# 🔹 Endpoint `/ask`
@app.route("/ask", methods=["POST"])
def ask():
    data = load_data()
    question = request.json.get("question", "")
    result = search_best_match(question, data)
    return jsonify(result)

# 🔹 Iniciar el servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
