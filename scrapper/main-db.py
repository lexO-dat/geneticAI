import os

def main():
    print("Procesando los json antes de subir a la db")
    os.system("python process-json.py")
    print("indexando por categoria")
    os.system("python add_to_db_indexed_by_cat.py")
    print("indexando por titulo")
    os.system("python add_to_db_indexed_by_title.py")
    print("todos los json subidos a la db")