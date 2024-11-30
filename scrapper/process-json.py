import os
import json

def load_json(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Archivo no encontrado: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error al decodificar JSON en {file_path}: {e}")
        return None

def save_json(data, file_path):
    with open(file_path, "w") as file:
        json.dump(data, file, indent=4)

def extract_category(roles):
    categories = []
    for role in roles:
        parts = role.rstrip('/').split('/')
        if parts:
            last_part = parts[-1]
            categories.append(last_part)
    return categories

def process_json_file(input_file, output_dir):
    data = load_json(input_file)
    if not data:
        return

    sequence_mapping = {}
    for entry in data:
        if entry.get('id', '').endswith('_sequence'):
            main_id = entry['id'][:-len('_sequence')]
            sequence_mapping[main_id] = entry.get('elements', '')

    new_data = []
    for entry in data:
        if entry.get('id', '').endswith('_sequence'):
            continue

        seq_id = entry.get('id', '')
        if seq_id in sequence_mapping:
            entry['sequence'] = sequence_mapping[seq_id]

        roles = entry.get("roles", [])
        categories = extract_category(roles)
        if categories:
            entry['category'] = categories

        new_data.append(entry)

    output_file = os.path.join(output_dir, os.path.basename(input_file))
    save_json(new_data, output_file)
    print(f"Procesado {input_file}, guardado en {output_file}")

def process_all_jsons(input_dir, output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    json_files = [f for f in os.listdir(input_dir) if f.endswith(".json")]

    for json_file in json_files:
        input_file = os.path.join(input_dir, json_file)
        process_json_file(input_file, output_dir)

if __name__ == "__main__":
    input_directory = "./json-folder"
    output_directory = "./processed-json-folder"
    process_all_jsons(input_directory, output_directory)
