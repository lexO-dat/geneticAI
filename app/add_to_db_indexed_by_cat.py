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

def extract_so_category(roles):
    so_category = None
    for role in roles:
        parts = role.rstrip('/').split('/')
        if parts:
            last_part = parts[-1]
            if last_part.startswith('SO:'):
                so_category = last_part
                break
    return so_category

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
    json_files = [f for f in os.listdir(input_dir) if f.endswith(".json")]
    
    for json_file in json_files:
        file_path = os.path.join(input_dir, json_file)
        data = load_json(file_path)
        if not data:
            continue
        
        actions = []
        for entry in data:
            roles = entry.get("roles", [])
            so_category = extract_so_category(roles)
            if so_category:
                entry['category'] = so_category
            else:
                continue
            index_name = so_category.lower().replace(':', '_').replace('.', '_')
            
            if not index_name:
                index_name = "unknown"
            
            action = {
                "_index": index_name,
                "_source": entry
            }
            actions.append(action)
        
        if actions:
            index_documents(es, actions)
            print(f"Indexed documents from {json_file} into indices based on SO categories.")
        else:
            print(f"No valid entries found in {json_file} for indexing.")

def main():
    inputFolder = input("Introduce la carpeta de archivos json PROCESADOS: ")
    es = connect_elasticsearch()
    if es:
        process_and_index_json_files(es, inputFolder)
