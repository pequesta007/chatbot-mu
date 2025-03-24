import fitz  # PyMuPDF
import json
import ftfy
import unicodedata
import re
import os

UPLOAD_FOLDER = "uploads"
DATA_FILE = "data.json"

# 🔹 Diccionario de correcciones extendido para evitar errores en palabras
reemplazos = {
    "ﬁ": "fi", "ﬂ": "fl", "ﬃ": "ffi", "ﬄ": "ffl", "ﬅ": "ft", "ﬆ": "st",
    "ﬀ": "ff", "\ufb01": "fi", "\ufb02": "fl", "\ufb05": "ft",
    "Gesón": "Gestión", "gesonar": "gestionar", "noficaciones": "notificaciones",
    "identificación": "identificación", "diagnóstico": "diagnóstico",
    "rescatistas": "rescatistas", "activa": "activa", "motivo": "motivo",
    "concienciación": "concienciación", "física": "física",
    "tenencia responsable": "tenencia responsable", "buenas prácticas": "buenas prácticas",
    "tipo": "tipo", "cantidad": "cantidad", "actividad": "actividad",
    "desparasitaciones (internaexterna)": "desparasitaciones (interna / externa)",
    "disponibles": "disponibles", "reportar": "reportar", "podrás": "podrás",
    "responsable": "responsable", "notificación": "notificación",
    "soporte": "soporte", "anticipación": "anticipación",
    "temporales": "temporales", "rutina de paseos": "rutina de paseos",
    "cirugías o procedimientos médicos (po, fecha, médico tratante)": "cirugías o procedimientos médicos (tipo, fecha, médico tratante)",
    "machohembra": "macho / hembra",
    "esterilizadono": "esterilizado / no esterilizado",
    "internexterna": "interna / externa",
    "5sica": "física",
    "runa de paseos": "rutina de paseos",
    "plasficarlo": "plastificarlo",
    "concienzación": "concienciación",
    "rescastas": "rescatistas",
    "incenvar": "incentivar",
    "idenficación": "identificación",
    "candad": "cantidad",
    "movo": "motivo",
    "diagnósco": "diagnóstico",
    "estado reproducvo": "estado reproductivo",
    "alimentación y observaciones": "alimentación y observaciones",
    "tenencia responsable, derechos de los animales y buenas práccas": "tenencia responsable, derechos de los animales y buenas prácticas",
    "po, fecha": "tipo, fecha",
    "tesgos": "testigos"
}

# 🔹 Caracteres invisibles y símbolos no deseados
caracteres_a_eliminar = re.compile(r'[\x00-\x1F\x7F-\x9F☻☼♀♂♫►•↑§/]')

# 🔹 Probar si el texto se extrae correctamente
def debug_text_output(text):
    print("🔍 Vista previa del texto extraído:")
    print("--------------------------------------------------")
    print(text[:1000])  # Muestra los primeros 1000 caracteres para revisión
    print("--------------------------------------------------")

# 🔹 Detectar títulos y subtítulos sin perder información
def detectar_secciones(text):
    lines = text.split("\n")
    estructura = {}
    current_section = None
    current_subsection = None

    for line in lines:
        line = caracteres_a_eliminar.sub('', line).strip()

        # 🔹 Detectar títulos principales (mayúsculas y menos de 10 palabras)
        if len(line) > 4 and (line.isupper() or len(line.split()) < 10):
            current_section = line
            estructura[current_section] = {}
            current_subsection = None
            continue

        # 🔹 Detectar subtítulos (Primera letra mayúscula y más de tres palabras)
        if len(line) > 6 and line[:1].isupper() and len(line.split()) > 3:
            if current_section:
                current_subsection = line
                estructura[current_section][current_subsection] = []
                continue

        # 🔹 Agregar contenido a la sección/subsección
        if line:
            if not current_section:
                current_section = "Información General"
                estructura[current_section] = {}

            if current_subsection:
                estructura[current_section].setdefault(current_subsection, []).append(line)
            else:
                estructura[current_section].setdefault("Descripción", []).append(line)

    # 🔹 Convertir listas en texto unificado y dividir secciones largas
    for section, subsections in estructura.items():
        for subsection, content in subsections.items():
            if isinstance(content, list):
                joined_content = " ".join(content)
                if len(joined_content) > 500:
                    split_content = [joined_content[i:i+500] for i in range(0, len(joined_content), 500)]
                    estructura[section][subsection] = split_content
                else:
                    estructura[section][subsection] = joined_content

    return estructura

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ""

    for page in doc:
        text += page.get_text("text") + "\n"

    return text.strip()

# 🔹 Limpiar y corregir el texto extraído
def clean_text(text):
    text = ftfy.fix_text(text)
    text = unicodedata.normalize("NFKC", text)
    text = caracteres_a_eliminar.sub('', text)

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

    for filename in os.listdir(upload_folder):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(upload_folder, filename)
            print(f"📄 Procesando: {filename}")

            extracted_text = extract_text_from_pdf(pdf_path)
            debug_text_output(extracted_text)  # 🔹 Verificar si el texto se extrae bien
            cleaned_text = clean_text(extracted_text)
            structured_data = detectar_secciones(cleaned_text)
            if structured_data:
                data[filename] = structured_data
            else:
                print(f"⚠ Advertencia: No se detectaron secciones en {filename}")

    save_to_json(data)

# 🔹 Ejecutar extracción y guardar en JSON
if __name__ == "__main__":
    process_all_pdfs()
