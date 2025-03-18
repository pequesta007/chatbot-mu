import fitz

pdf_path = "uploads/📲 Opciones de la APP Muni mascotas (1).pdf"  # Asegúrate de que el PDF está en la carpeta "uploads"
doc = fitz.open(pdf_path)

for page in doc:
    text = page.get_text("text")
    print("🔍 TEXTO EXTRAÍDO (Original):", text)  # Imprime el texto extraído
    print("\n🧐 CÓDIGOS HEXADECIMALES:")
    
    for char in text:
        print(f"'{char}' -> {hex(ord(char))}")  # Muestra cada letra con su código en hexadecimal
    
    break  # Solo analizar la primera página para no sobrecargar la terminal
