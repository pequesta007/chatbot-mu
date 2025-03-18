import os
import json
import re
import unicodedata
import pdfplumber
import fitz  # PyMuPDF
from flask import Flask, request, jsonify
from difflib import get_close_matches

UPLOAD_FOLDER = "uploads"
DATA_FILE = "data.json"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# 🔹 Limpiar texto sin eliminar caracteres importantes
def clean_text(text):
    text = unicodedata.normalize("NFKC", text)  # Normalizar caracteres Unicode

    # Eliminar SOLO caracteres de control sin afectar letras
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F-\x9F]', '', text)
    text = re.sub(r'\s{2,}', ' ', text).strip()  # Normalizar espacios
    return text

# 🔹 Extraer texto con PyMuPDF de manera más confiable
def extract_text_with_pymupdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)
    for page in doc:
        page_text = page.get_text("blocks")  # Extraer bloques de texto
        if page_text:
            for block in page_text:
                text += block[4] + "\n"  # Extraer contenido del bloque de texto
    return text

# 🔹 Extraer texto con pdfplumber si PyMuPDF falla
def extract_text_with_pymupdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)

    for page in doc:
        words = page.get_text("dict")["blocks"]  # Extraer texto con estructura
        for block in words:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text += span["text"] + " "  # Extraer palabras sin perder letras
        text += "\n"

    return text.strip()

# 🔹 Función principal de extracción
def extract_text_from_pdf(pdf_path):
    print(f"📄 Procesando PDF: {pdf_path}")
    text = extract_text_with_pymupdf(pdf_path)  # Intentar con PyMuPDF

    if not text or len(text.strip()) < 30:  # Si PyMuPDF falla, usar pdfplumber
        print("⚠️ PyMuPDF no extrajo bien el texto. Probando con pdfplumber...")
        text = extract_text_with_pymupdf(pdf_path)

    print("🔍 **Texto extraído ANTES de limpiar:**\n", text[:1000])  # Mostrar los primeros 1000 caracteres

    if not text:
        print("❌ No se pudo extraer texto del PDF.")
        return "No se pudo extraer texto del documento."

    return clean_text(text)

# 🔹 Guardar datos en JSON
def save_data_to_json(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# 🔹 Cargar datos desde JSON
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                return json.loads(content) if content else {}
        except json.JSONDecodeError:
            return {}
    return {}

# 🔹 Endpoint para subir PDF y extraer datos
@app.route("/upload", methods=["POST"])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    extracted_text = extract_text_from_pdf(file_path)
    data = load_data()
    data[file.filename] = extracted_text
    save_data_to_json(data)

    return jsonify({"message": "File uploaded and processed successfully"})

# 🔹 Endpoint para consultar información del PDF
@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.json.get("question", "").lower()
    data = load_data()

    # Unir todo el contenido en una sola cadena de texto
    all_text = " ".join(data.values()).lower()

    # Buscar coincidencias aproximadas con similitud
    matches = get_close_matches(user_question, all_text.split(". "), n=3, cutoff=0.3)

    response = matches[0] if matches else "Lo siento, no encontré información relevante."
    
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
