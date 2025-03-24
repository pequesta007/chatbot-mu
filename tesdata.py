import json

DATA_FILE = "data.json"

try:
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        print("✅ JSON cargado correctamente.")
        print("🔍 Claves principales:", list(data.keys()))
        for filename, sections in data.items():
            print(f"📄 Archivo: {filename}")
            for section, content in sections.items():
                print(f"  🔹 Sección: {section} -> Tipo de contenido: {type(content)}")
                if isinstance(content, dict):
                    for sub_section, sub_content in content.items():
                        print(f"    🔸 Sub-sección: {sub_section} -> Tipo: {type(sub_content)}")
                        if isinstance(sub_content, list):
                            print(f"      🔽 Vista previa: {sub_content[:2]}")  # Muestra un par de ejemplos
except Exception as e:
    print(f"❌ ERROR al cargar {DATA_FILE}: {e}")
