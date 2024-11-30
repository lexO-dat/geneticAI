import os
import sbol_to_json as stj

# recorrer la carpeta sbol y convertir todos los archivos a json
sbol_folder = "sbol"
final_path = "json-folder"
for file in os.listdir(sbol_folder):
    if file.endswith(".xml"):
        stj.sbol_to_json(os.path.join(sbol_folder, file), final_path)
