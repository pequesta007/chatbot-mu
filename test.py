import fitz  # PyMuPDF
import json
import ftfy
import unicodedata
import re
import os

# 🔹 Diccionario de corrección de caracteres dañados
reemplazos = {
    "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "ft", "ﬆ": "st",
    "ﬀ": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb05": "ft", "\uF02D": "ti"
}

# 🔹 Lista de símbolos raros que hay que eliminar
simbolos_a_eliminar = ["☻", "☼", "♀", "♂", "♫", "►", "•", "↑", "\x02", "\x08", "\x18", "\x0b", "\x0c"]

# 🔹 Función para extraer texto del PDF con estructura
def extract_text_with_pymupdf(pdf_path):
    doc = fitz.open(pdf_path)
    text_by_page = {}

    for i, page in enumerate(doc):
        text = page.get_text("text")
        text_by_page[f"Página {i+1}"] = text.strip()  # Guardamos por páginas

    return text_by_page

# 🔹 Función para limpiar texto y manejar caracteres dañados
def clean_text(text):
    text = ftfy.fix_text(text)
    text = unicodedata.normalize("NFKC", text)

    for char_raro, reemplazo in reemplazos.items():
        text = text.replace(char_raro, reemplazo)

    for simbolo in simbolos_a_eliminar:
        text = text.replace(simbolo, "")

    text = re.sub(r'G[^\w\s]?es[^\w\s]?ó[^\w\s]?n', "Gestión", text)

    return text.strip()

# 🔹 Función para procesar TODOS los PDFs en `uploads/` y agregarlos estructurados en JSON
def process_all_pdfs(upload_folder="uploads", json_path="data.json"):
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}
    else:
        data = {}

    for filename in os.listdir(upload_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(upload_folder, filename)
            print(f"📄 Procesando: {filename}")

            extracted_text = extract_text_with_pymupdf(pdf_path)

            # 🔹 Limpiar cada página del documento
            cleaned_text_by_page = {page: clean_text(text) for page, text in extracted_text.items()}

            # 🔹 Guardar el PDF con su contenido estructurado por páginas
            data[filename] = cleaned_text_by_page

    # 🔹 Guardar en JSON con estructura
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ Todos los PDFs han sido procesados y guardados en '{json_path}' con estructura.")

# 🔹 Ejecutar extracción y guardar en JSON estructurado
process_all_pdfs()
