import os
import xml.etree.ElementTree as ET
from simple_term_menu import TerminalMenu
import json

def sbol_to_json(sbol_file, output_folder):
    """
    Convierte un archivo SBOL XML a formato JSON y lo guarda en la carpeta especificada.
    
    :param sbol_file: Ruta del archivo SBOL XML.
    :param output_folder: Carpeta donde se guardará el JSON. Por defecto, "sbol".
    :return: None
    """
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Obtención de los namespaces
        def get_namespaces(xml_file):
            events = ET.iterparse(xml_file, events=("start-ns",))
            namespaces = {}
            for _, ns in events:
                if ns[0] not in namespaces:
                    namespaces[ns[0]] = ns[1]
            return namespaces

        namespaces = {prefix: uri for prefix, uri in get_namespaces(sbol_file).items()}

        tree = ET.parse(sbol_file)
        root = tree.getroot()

        output = []

        # Extracción de componentes
        for comp_def in root.findall(f"{{{namespaces['sbol']}}}ComponentDefinition"):
            component = {
                "id": comp_def.find(f"{{{namespaces['sbol']}}}displayId").text if comp_def.find(f"{{{namespaces['sbol']}}}displayId") is not None else None,
                "title": comp_def.find(f"{{{namespaces['dcterms']}}}title").text if comp_def.find(f"{{{namespaces['dcterms']}}}title") is not None else None,
                "description": comp_def.find(f"{{{namespaces['dcterms']}}}description").text if comp_def.find(f"{{{namespaces['dcterms']}}}description") is not None else None,
                "type": comp_def.find(f"{{{namespaces['sbol']}}}type").get(f"{{{namespaces['rdf']}}}resource") if comp_def.find(f"{{{namespaces['sbol']}}}type") is not None else None,
                "roles": [
                    role.get(f"{{{namespaces['rdf']}}}resource")
                    for role in comp_def.findall(f"{{{namespaces['sbol']}}}role")
                ],
                "sequence_ref": comp_def.find(f"{{{namespaces['sbol']}}}sequence").get(f"{{{namespaces['rdf']}}}resource") if comp_def.find(f"{{{namespaces['sbol']}}}sequence") is not None else None,
            }
            output.append(component)

        # Extracción de secuencias
        for seq in root.findall(f"{{{namespaces['sbol']}}}Sequence"):
            sequence = {
                "id": seq.find(f"{{{namespaces['sbol']}}}displayId").text if seq.find(f"{{{namespaces['sbol']}}}displayId") is not None else None,
                "elements": seq.find(f"{{{namespaces['sbol']}}}elements").text if seq.find(f"{{{namespaces['sbol']}}}elements") is not None else None,
            }
            output.append(sequence)

        json_output = json.dumps(output, indent=4)
        json_file_path = os.path.join(output_folder, os.path.splitext(os.path.basename(sbol_file))[0] + ".json")

        # json
        with open(json_file_path, "w") as json_file:
            json_file.write(json_output)

        print(f"JSON generado y guardado en {json_file_path}")

    except ET.ParseError as e:
        print(f"Error al procesar el archivo XML '{sbol_file}': {e}")

def main():
    while True:
        options = ["[1] Convertir un archivo SBOL a JSON", "[2] Convertir una carpeta de archivos SBOL a JSON", "[3] Salir"]
        terminal_menu = TerminalMenu(options, title="SBOL a JSON")
        menu_entry_index = terminal_menu.show()
        print(f"Opcion seleccionada: {options[menu_entry_index]}")

        if menu_entry_index == 0:
            sbol_file = input("Introduce la ruta del archivo SBOL XML: ")
            output_folder = input("Introduce la carpeta de salida (por defecto, 'json'): ") or "json"
            print(f"Convirtiendo '{sbol_file}' a JSON...")
            sbol_to_json(sbol_file, output_folder)
        elif menu_entry_index == 1:
            sbolFolder = input("Introduce la carpeta de archivos SBOL XML, por defecto es 'sbol': ") or "sbol"
            outputFolder = input("Introduce la carpeta de salida (por defecto, 'json'): ") or "json"
            for file in os.listdir(sbolFolder):
                if file.endswith(".xml"):
                    print(f"Convirtiendo '{file}' a JSON...")
                    sbol_to_json(os.path.join(sbolFolder, file), sbolFolder)
        else:
            break
        