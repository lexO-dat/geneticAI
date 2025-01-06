from simple_term_menu import TerminalMenu
from sbol_to_json import main as sbtj
from synbiohub_scrapper import main as sbs
import os


'''
todo:
main:
- installer --> install dependencies
- scrapper --> scrape synbiohub and save the sbols
- db management (elastic) --> (search)
- file management and conversion
    - sbol to json (1 file or 1 dir)
    - json to db --> add indexed by cat and title
'''
def main():
    while True:
        options = [
            "[1] Instalar Dependencias - Instala paquetes desde requirements.txt",
            "[2] Scrapper - Obtiene datos de SynBioHub y guarda SBOLs",
            "[3] Manejo de base de datos - Publica o consulta información en ElasticSearch",
            "[4] Manejo de archivos - Convierte SBOL a JSON o agrega datos al sistema",
            "[5] Salir - Cierra la aplicación"
        ]
        terminal_menu = TerminalMenu(options, title="App")
        menu_entry_index = terminal_menu.show()
        print(f"Opcion seleccionada: {options[menu_entry_index]}")

        if menu_entry_index == 0:
            print("Instalando dependencias")
            os.system("pip install -r requirements.txt")
        elif menu_entry_index == 1:
            print("Scrapeando datos de synbiohub, esto puede tardar un rato")
            print("Se generara un csv con los distintos links y se descargaran los sbols para su posterior guardado en la carpeta sbol")
            sbs()
        elif menu_entry_index == 2:
            print("Posteando a la base de datos")
            os.system("python main-db.py")
        elif menu_entry_index == 3:
            sbtj()
        else:
            break
    
if __name__ == "__main__":
    main()
