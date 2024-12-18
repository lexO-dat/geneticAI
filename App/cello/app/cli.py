import os
import uuid
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .models import CelloRequest, CelloOptions
from core_algorithm.celloAlgo import cello_initializer
from config import LIBRARY_DIR, VERILOGS_DIR, CONSTRAINTS_DIR, TEMP_OUTPUTS_DIR
from core_algorithm.utils import log

app = FastAPI(
    title="Cello API",
    description="API para generar diseños de circuitos genéticos usando Cello 2.1",
    version="1.0.0"
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

# Montar archivos estáticos
app.mount("/outputs", StaticFiles(directory=TEMP_OUTPUTS_DIR), name="outputs")

# Lista predefinida de UCF
UCF_LIST = [
    'Bth1C1G1T1', 'Eco1C1G1T1', 'Eco1C2G2T2', 'Eco2C1G3T1',
    'Eco2C1G5T1', 'Eco2C1G6T1', 'SC1C1G1T1'
]

@app.post("/run_cello", summary="Ejecutar Cello para generar diseño de circuito genético")
async def run_cello(request: CelloRequest):
    temp_verilog_filename = None

    try:
        # Crear archivo temporal Verilog si viene como código
        if request.verilog_code:
            temp_verilog_filename = f"temp_{uuid.uuid4().hex}.v"
            verilog_path = os.path.join(VERILOGS_DIR, temp_verilog_filename)
            with open(verilog_path, 'w') as f:
                f.write(request.verilog_code)
            log.cf.info(f"Archivo Verilog temporal creado: {temp_verilog_filename}")
        elif request.verilog_file:
            verilog_path = os.path.join(VERILOGS_DIR, f"{request.verilog_file}.v")
            if not os.path.isfile(verilog_path):
                raise HTTPException(status_code=404, detail="Archivo Verilog no encontrado.")
        else:
            raise HTTPException(status_code=400, detail="Debe proporcionar 'verilog_file' o 'verilog_code'.")

        # Manejo de UCF
        if request.ucf_index is not None:
            try:
                selected_ucf = UCF_LIST[request.ucf_index] + '.UCF.json'
                input_file = UCF_LIST[request.ucf_index] + '.input.json'
                output_file = UCF_LIST[request.ucf_index] + '.output.json'
            except IndexError:
                raise HTTPException(status_code=400, detail="Índice UCF inválido.")
        else:
            if not all([request.custom_ucf, request.custom_input, request.custom_output]):
                raise HTTPException(status_code=400, detail="Se deben proporcionar archivos UCF, input y output personalizados.")
            selected_ucf = request.custom_ucf
            input_file = request.custom_input
            output_file = request.custom_output

        ucf_path = os.path.join(CONSTRAINTS_DIR, selected_ucf)
        input_path = os.path.join(CONSTRAINTS_DIR, input_file)
        output_path = os.path.join(CONSTRAINTS_DIR, output_file)

        # Verificar existencia de archivos
        for path, desc in zip([ucf_path, input_path, output_path], ["UCF", "Input", "Output"]):
            if not os.path.isfile(path):
                raise HTTPException(status_code=404, detail=f"Archivo {desc} no encontrado.")

        options = request.options.dict()
        in_path_ = LIBRARY_DIR
        out_path_ = TEMP_OUTPUTS_DIR
        v_name_ = os.path.splitext(os.path.basename(verilog_path))[0].replace('.v', '')
        ucf_name_ = selected_ucf
        in_name_ = input_file
        out_name_ = output_file

        try:
            result = cello_initializer(
                v_name_, ucf_name_, in_name_, out_name_,
                in_path_, out_path_,
                options=options
            )
        except Exception as e:
            log.cf.error("Error ejecutando cello_initializer", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

        # Devolver respuesta con el nombre de la carpeta
        return JSONResponse(content={
            "message": "Proceso de Cello completado exitosamente.",
            "result": result,
            "folder_name": v_name_
        })

    finally:
        # Eliminar archivo temporal Verilog
        if temp_verilog_filename:
            temp_verilog_path = os.path.join(VERILOGS_DIR, temp_verilog_filename)
            if os.path.isfile(temp_verilog_path):
                try:
                    os.remove(temp_verilog_path)
                    log.cf.info(f"Archivo Verilog temporal eliminado: {temp_verilog_filename}")
                except Exception as e:
                    log.cf.warning(f"No se pudo eliminar el archivo temporal {temp_verilog_filename}: {e}")

@app.get("/outputs/{folder_name}/{temp_name}/{pdf_name}_Eco1C1G1T1.UCF._dpl-sbol.pdf", summary="Servir PDF de circuito")
async def serve_pdf(folder_name: str, pdf_name: str, temp_name:str):
    pdf_path = os.path.join(TEMP_OUTPUTS_DIR, folder_name, temp_name, f"{pdf_name}_Eco1C1G1T1.UCF._dpl-sbol.pdf")
    if not os.path.isfile(pdf_path):
        raise HTTPException(status_code=404, detail="PDF no encontrado")
    return FileResponse(pdf_path, media_type="application/pdf")
