from bs4 import BeautifulSoup

with open("archivo_sbol.xml", "r") as file:
    soup = BeautifulSoup(file, "xml")

sequence = soup.find("sbol:elements").text
print("Secuencia genética:")
print(sequence)

def format_sequence(sequence, line_length=50, block_size=10):
    formatted_sequence = ""
    line_number = 1
    for i in range(0, len(sequence), line_length):
        line_sequence = sequence[i:i + line_length]
        
        blocks = [line_sequence[j:j + block_size] for j in range(0, len(line_sequence), block_size)]
        
        formatted_line = f"{str(line_number).zfill(4)} {' '.join(blocks)}"
        formatted_sequence += formatted_line + "\n"
        
        # Incrementar el número de línea
        line_number += 1
    
    return formatted_sequence.strip()

formatted_sequence = format_sequence(sequence)
print(formatted_sequence)
