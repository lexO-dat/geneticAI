from simple_term_menu import TerminalMenu
import os

def main():
    while True:
        options = ["[1] Instalar Dependencias","[2] scrapear datos de synbiohub", "[3] convertir los sbol a json", "[4] subir a la db de elastic los json", "[5] Salir"]
        terminal_menu = TerminalMenu(options, title="App")
        menu_entry_index = terminal_menu.show()
        print(f"Opcion seleccionada: {options[menu_entry_index]}")

        if menu_entry_index == 0:
            print("Creando Carpetas necesarias")
            os.system("mkdir sbol")
            os.system("mkdir json-folder")
            os.system("mkdir processed-json-folder")
            print("Instalando dependencias")
            os.system("pip install -r requirements.txt")
        elif menu_entry_index == 1:
            print("Scrapeando datos de synbiohub")
            os.system("python synbiohub_scrapper.py")
        elif menu_entry_index == 2:
            print("Convirtiendo los sbol a json")
            os.system("python sbol_to_json.py")
        elif menu_entry_index == 3:
            print("Posteando a la base de datos")
            os.system("python main-db.py")
        else:
            break
    
if __name__ == "__main__":
    main()
