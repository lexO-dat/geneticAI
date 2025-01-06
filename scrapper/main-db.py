import os
from simple_term_menu import TerminalMenu
from processJson import main as process_json
from add_to_db_indexed_by_cat import main as index_by_cat
from add_to_db_indexed_by_title import main as index_by_title

def main():
    while True:
        options = ["[1] Procesar los json antes de subir (desde carpeta json)", "[2] Indexar por categoria", "[3] Indexar por titulo", "[4] Salir"]
        terminal_menu = TerminalMenu(options, title="DB Management")
        menu_entry_index = terminal_menu.show()
        print(f"Opcion seleccionada: {options[menu_entry_index]}")

        if menu_entry_index == 0:
            print("procesando los json antes de subir a la db")
            process_json()
        elif menu_entry_index == 1:
            print("indexando por categoria")
            index_by_cat()
        elif menu_entry_index == 2:
            print("indexando por titulo")
            index_by_title()
        else:
            break
