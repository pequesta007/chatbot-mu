import fitz  # PyMuPDF
import json
import ftfy
import unicodedata
import re
import os

UPLOAD_FOLDER = "uploads"
DATA_FILE = "data.json"

# 🔹 Diccionario extendido para corregir palabras fragmentadas y caracteres mal extraídos
reemplazos = {
    "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "ft", "ﬆ": "st",
    "ﬀ": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb05": "ft",
    "G es ón": "Gestión", "G esón": "Gestión", "G e s t i ó n": "Gestión",
    "iden/dad": "identidad", "tes/gos": "testigos", "alimenta/ción": "alimentación",
    "aten/ción": "atención", "reac/ción": "reacción", "incen/var": "incentivar",
    "no/ficaciones": "notificaciones", "ges/on": "gestión", "reproducvo": "reproductivo",
    "plas/ficarlo": "plastificarlo", "comu/cate": "comunícate", "mo/vo": "motivo",
    "concienzación": "concienciación", "po, fecha": "tipo, fecha",
    "vacunación y esterilización gratuitas": "vacunación y esterilización gratuitas",
    "educación y concienzación": "educación y concienciación",
    "interac/vos": "interactivos", "infograFas": "infografías", "expl/ca/vos": "explicativos",
    "Gesón": "Gestión", "buenas práccas": "buenas prácticas", "Tesgos": "Testigos",
    "idenficar": "identificar", "incenvar": "incentivar", "idendad": "identidad",
    "fotosvideos": "fotos y videos", "explicavos": "explicativos",
    "noficaciones": "notificaciones", "empo": "tiempo", "movo": "motivo",
    "diagnósco": "diagnóstico", "rescastas": "rescatistas", "acva": "activa",
    "internexterna": "interna/externa", "machohembra": "macho/hembra",
    "esterilizadono": "esterilizado / no", "5sica": "física", "candad": "cantidad",
    "diagnoscadas": "diagnosticadas", "acvidad": "actividad", "comparr": "compartir",
    "ancipación": "anticipación", "runa de paseos": "rutina de paseos",
    "Fsico": "Físico", "ttiemporales": "temporales", "ttiemporal": "temporal",
    "interacvos": "interactivos", "desparasitaciones (internaexterna": "desparasitaciones (interna/externa",
    "rutina de paseos y acvidad física": "rutina de paseos y actividad física",
    "tenencia responsable, derechos de los animales y buenas práccas": "tenencia responsable, derechos de los animales y buenas prácticas"
}

# 🔹 Caracteres invisibles y símbolos no deseados
caracteres_a_eliminar = re.compile(r'[\x00-\x1F\x7F-\x9F☻☼♀♂♫►•↑/]')

# 🔹 Extraer texto con mayor precisión
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""
    
    for page in doc:
        text += page.get_text("text") + "\n"
    
    return text.strip()

# 🔹 Limpiar y corregir el texto extraído
def clean_text(text):
    text = ftfy.fix_text(text)  # 🔹 Corrige errores de codificación
    text = unicodedata.normalize("NFKC", text)  # 🔹 Normaliza caracteres Unicode
    text = caracteres_a_eliminar.sub('', text)  # 🔹 Elimina caracteres invisibles
    
    # 🔹 Corregir palabras fragmentadas con más precisión
    for original, corregido in reemplazos.items():
        text = re.sub(re.escape(original), corregido, text, flags=re.IGNORECASE)
    
    return text.strip()

# 🔹 Guardar en JSON sin perder la estructura
def save_to_json(data, json_path=DATA_FILE):
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"✅ Datos guardados en `{json_path}` correctamente.")

# 🔹 Procesar TODOS los PDFs en `uploads/`
def process_all_pdfs(upload_folder=UPLOAD_FOLDER, json_path=DATA_FILE):
    data = {}
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    
    for filename in os.listdir(upload_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(upload_folder, filename)
            print(f"📄 Procesando: {filename}")

            extracted_text = extract_text_from_pdf(pdf_path)
            cleaned_text = clean_text(extracted_text)
            
            # 🔹 Guardar con estructura limpia
            data[filename] = cleaned_text
    
    save_to_json(data)

# 🔹 Ejecutar extracción y guardar en JSON
if __name__ == "__main__":
    process_all_pdfs()
