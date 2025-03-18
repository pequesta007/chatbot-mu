import fitz  # PyMuPDF
import unicodedata
import ftfy
import re

# 🔹 Diccionario de caracteres problemáticos
reemplazos_hexadecimales = {
    "\ufb01": "fi", "\ufb02": "fl", "\ufb03": "ffi", "\ufb04": "ffl",  # Ligaduras comunes
    "\ufb05": "ft", "\ufb06": "st",  # Ligaduras extrañas
    "\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"',  # Comillas/apóstrofos
}

# 🔹 Lista de palabras que suelen dañarse en PDFs con fuentes especiales
correcciones_palabras = {
    "Gesón": "Gestión",
    "caracteríscas": "características",
    "nocaciones": "notificaciones",
    "vacunaón": "vacunación",
    "locación": "localización",
    "parición": "participación",
}

def extract_text_with_pymupdf(pdf_path):
    text = ""
    doc = fitz.open(pdf_path)

    for page in doc:
        page_dict = page.get_text("dict")  # Extraer en formato detallado
        for block in page_dict["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        extracted_text = span["text"]
                        extracted_text = unicodedata.normalize("NFKC", extracted_text)  # Normalizar caracteres Unicode
                        extracted_text = ftfy.fix_text(extracted_text)  # Corregir errores de codificación
                        
                        # 🔹 Reemplazar caracteres hexadecimales
                        for hex_code, reemplazo in reemplazos_hexadecimales.items():
                            extracted_text = extracted_text.replace(hex_code, reemplazo)

                        text += extracted_text + " "
        text += "\n"

    return text

def clean_text(text):
    # 🔹 Corrección manual de palabras con errores en PDFs
    for palabra_erronea, correccion in correcciones_palabras.items():
        text = re.sub(rf"\b{palabra_erronea}\b", correccion, text)  # Corrige solo palabras completas
    
    text = text.replace("\n", " ").strip()  # Quitar saltos de línea innecesarios
    text = " ".join(text.split())  # Normalizar espacios
    return text

pdf_path = "C:/Users/INFORMATICA/Desktop/chatbot_pdf/uploads/📲 Opciones de la APP Muni mascotas (1).pdf"
texto_extraido = extract_text_with_pymupdf(pdf_path)
texto_corregido = clean_text(texto_extraido)

# Guardar el texto corregido
with open("texto_extraido_corregido.txt", "w", encoding="utf-8") as f:
    f.write(texto_corregido)

print("✅ Extracción completada. Revisa 'texto_extraido_corregido.txt'.")
