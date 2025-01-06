import os
import json
from elasticsearch import Elasticsearch, helpers

def connect_elasticsearch():
    es = Elasticsearch(hosts=["http://localhost:9200"])
    if es.ping():
        print("Connected to Elasticsearch")
    else:
        print("Could not connect to Elasticsearch")
        es = None
    return es

def load_json(file_path):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return None

def index_documents(es, docs):
    try:
        helpers.bulk(es, docs)
    except Exception as e:
        print(f"Error indexing documents: {e}")

def process_and_index_json_files(es, input_dir):
    index_name = "indexed_by_title"  # Nombre del índice único
    json_files = [f for f in os.listdir(input_dir) if f.endswith(".json")]

    for json_file in json_files:
        file_path = os.path.join(input_dir, json_file)
        data = load_json(file_path)
        if not data:
            continue

        actions = []
        for entry in data:
            action = {
                "_index": index_name,
                "_source": entry
            }
            actions.append(action)

        if actions:
            index_documents(es, actions)
            print(f"Documentos indexados de {json_file} en el índice '{index_name}'.")
        else:
            print(f"No se encontraron entradas válidas en {json_file} para indexar.")

def main():
    inputFolder = input("Introduce la carpeta de archivos json PROCESADOS")
    es = connect_elasticsearch()
    if es:
        process_and_index_json_files(es, inputFolder)
