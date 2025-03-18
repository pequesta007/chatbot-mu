import fitz  # PyMuPDF
import json
import ftfy
import unicodedata
import re

# 🔹 Diccionario de corrección de caracteres dañados
reemplazos = {
    "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "ft", "ﬆ": "st",
    "ﬀ": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb05": "ft", "\uF02D": "ti",  
}

# 🔹 Lista de símbolos raros que hay que eliminar
simbolos_a_eliminar = ["☻", "☼", "♀", "♂", "♫", "►", "•", "↑", "\x02", "\x08", "\x18", "\x0b", "\x0c"]

# 🔹 Función para extraer texto del PDF
def extract_text_with_pymupdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)

    for page in doc:
        text += page.get_text("text") + "\n"

    return text.strip()

# 🔹 Función para limpiar texto y manejar los `\n`
def clean_text(text):
    text = ftfy.fix_text(text)
    text = unicodedata.normalize("NFKC", text)

    # 🔹 Reemplazo manual de caracteres dañados
    for char_raro, reemplazo in reemplazos.items():
        text = text.replace(char_raro, reemplazo)

    # 🔹 Eliminar símbolos extraños
    for simbolo in simbolos_a_eliminar:
        text = text.replace(simbolo, "")

    # 🔹 Forzar separación de letras en palabras clave como "Gestión"
    text = re.sub(r'G[^\w\s]?es[^\w\s]?ó[^\w\s]?n', "Gestión", text)

    # 🔹 MANEJO DE `\n`
    text = text.replace("\n", " ")  # 🔹 Opción 1: Eliminar `\n` y unir en una sola línea
    # text = re.sub(r'\n+', '\n', text).strip()  # 🔹 Opción 2: Mantener saltos de línea

    return text

# 🔹 Función para guardar en JSON sin perder el formato original
def save_to_json(text, json_path="data.json"):
    text = clean_text(text)
    data = {"contenido": text}

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ Texto guardado en '{json_path}' correctamente.")

# 🔹 Ruta del PDF
pdf_path = "uploads/📲 Opciones de la APP Muni mascotas (1).pdf"
json_path = "data.json"

# 🔹 Ejecutar extracción y guardar en JSON
texto_extraido = extract_text_with_pymupdf(pdf_path)
save_to_json(texto_extraido, json_path)
