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

"""
DONE:
    Convert CELLO into an API with the following endpoints:
        /v1/run → Executes CELLO and returns a JSON containing the folder name where the files were saved and a list of the generated files.
        /v1/outputs/{folder_name}/{file_name} → Returns a file located in the outputs folder (this will be used for previews or downloads on the front end).
"""
app = FastAPI(
    title="Cello API",
    description="API to generate genetic circuit designs using Cello 2.1",
    version="1.0.0"
)

# -------------------
# Middleware
# -------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

app.mount("/outputs", StaticFiles(directory=TEMP_OUTPUTS_DIR), name="outputs")

# Ucf list
UCF_LIST = [
    'Bth1C1G1T1', 'Eco1C1G1T1', 'Eco1C2G2T2', 'Eco2C1G3T1',
    'Eco2C1G5T1', 'Eco2C1G6T1', 'SC1C1G1T1'
]

@app.post("/v1/run", summary="Execute CELLO")
async def run(request: CelloRequest):
    tempVerilogName = None

    try:
        """
        - The received verilog code is saved in a temporary file with the name temp_{uuid}.v
        - If the verilogFile is provided, the file is searched in the VERILOGS_DIR
        """
        if request.verilogCode:
            tempVerilogName = f"temp_{uuid.uuid4().hex}.v"
            verilogPath = os.path.join(VERILOGS_DIR, tempVerilogName)
            with open(verilogPath, 'w') as f:
                f.write(request.verilogCode)
            log.cf.info(f"Temp file created: {tempVerilogName}")
        elif request.verilog_file:
            verilogPath = os.path.join(VERILOGS_DIR, f"{request.verilog_file}.v")
            if not os.path.isfile(verilogPath):
                raise HTTPException(status_code=404, detail="Verilog file not found.")
        else:
            raise HTTPException(status_code=400, detail="You must provide a verilogFile or verilogCode.")

        # Ucf selection and verification
        if request.ucfIndex is not None:
            try:
                selectedUcf = UCF_LIST[request.ucfIndex] + '.UCF.json'
                inputFile = UCF_LIST[request.ucfIndex] + '.input.json'
                outputFile = UCF_LIST[request.ucfIndex] + '.output.json'
            except IndexError:
                raise HTTPException(status_code=400, detail="Ucf index not valid.")
        else:
            # Custom UCF, Input and Output files (is not implemented yet, but it is a good idea to have it in mind)
            if not all([request.customUcf, request.customInput, request.customOutput]):
                raise HTTPException(status_code=400, detail="You must ptevide the custom input / output / ucf json files.")
            selectedUcf = request.customUcf
            inputFile = request.customInput
            outputFile = request.customOutput

        ucfPath = os.path.join(CONSTRAINTS_DIR, selectedUcf)
        inputPath = os.path.join(CONSTRAINTS_DIR, inputFile)
        outputPath = os.path.join(CONSTRAINTS_DIR, outputFile)

        # Verification of the existence of the ucf files
        for path, desc in zip([ucfPath, inputPath, outputPath], ["UCF", "Input", "Output"]):
            if not os.path.isfile(path):
                raise HTTPException(status_code=404, detail=f"Archivo {desc} no encontrado.")

        options = request.options.dict()
        inPath = LIBRARY_DIR
        outPath_ = TEMP_OUTPUTS_DIR
        vName_ = os.path.splitext(os.path.basename(verilogPath))[0].replace('.v', '')
        ucfName_ = selectedUcf
        inName_ = inputFile
        outName_ = outputFile

        try:
            result = cello_initializer(
                vName_, ucfName_, inName_, outName_,
                inPath, outPath_,
                options=options
            )
        except Exception as e:
            log.cf.error("Error executing cello", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

        output_files = os.listdir(os.path.join(TEMP_OUTPUTS_DIR, vName_))

        return JSONResponse(content={
            "message": "Cello process completed.",
            "result": result,
            "folder_name": vName_,
            "output_files": output_files  # List of the generated files
        })

    finally:
        if tempVerilogName:
            temp_verilog_path = os.path.join(VERILOGS_DIR, tempVerilogName)
            if os.path.isfile(temp_verilog_path):
                try:
                    os.remove(temp_verilog_path)
                    log.cf.info(f"Temporal verilog file deleted: {tempVerilogName}")
                except Exception as e:
                    log.cf.warning(f"Error deleting the temporal verilog file {tempVerilogName}: {e}")

# Endpoint that returns a file x (if it exists), I will use this to be able to make previews or allow the files to be downloaded
@app.get("/v1/outputs/{folder_name}/{file_name}", summary="Return File")
async def output(folder_name: str, file_name: str):
    outputPath = os.path.join(TEMP_OUTPUTS_DIR, folder_name, file_name)
    
    if not os.path.isfile(outputPath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(outputPath)





