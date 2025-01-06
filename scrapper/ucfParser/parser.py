import os
import json

# TODO
# - [ ] Arreglar el tema de response_functions y models
# - [ ] Arreglar el tema de gate_name y name
# - [ ] Agregar todo lo de gates a un archivo llamado gate_name_gate_ucfname.json
# - [ ] Estandarizar el código para que pueda parsear de cualquiera de los ucf (EcoC1G1T0, EcoC1G1T1, EcoC1G1T2, EcoC1G1T3, etc)

# Definición de rutas
ucfPath = 'ucf/v2/ucf/Eco/Eco1C1G1T1.UCF.json'
resultFolder = './result'
cytometryFolder = resultFolder + '/cytometry/'
toxicityFolder = resultFolder + '/toxicity/'
ucf = json.load(open(ucfPath))

# Definición de variables
gateArr = []
responseMap = {}
partsMap = {}
cytometryMap = {}
toxixityMap = {}
gatesMap = {}

motifLib = []
logicConstraints = None
eugeneRules = None
geneticLocations = None
measurementStandards = None
header = None

# spliteado del ucf
for collection in ucf:
    collection_type = collection.get('collection')

    if collection_type == 'parts':
        partsMap[collection['name']] = collection # ver donde guardarlo

    elif collection_type == 'gate_parts':
        gateArr.append(collection) # ver donde guardarlo

    elif collection_type == 'response_functions': # esto en algunos se llama response_functions y en otros models y tampoco lo estoy guardando
        responseMap[collection['gate_name']] = collection # esto en algunos se llama gate_name y en otros name 

    elif collection_type == 'gates' and collection['gate_name']:
        gatesMap[collection['gate_name']] = collection

    elif collection_type == 'gates' and collection['name']:
        gatesMap[collection['name']] = collection

    elif collection_type == 'gate_cytometry':
        cytometryMap[collection['gate_name']] = collection['cytometry_data'] # ok -> sólo para el EcoC1G1T0
    elif collection_type == 'gate_toxicity':
        toxixityMap[collection['gate_name']] = collection # ok -> sólo para el EcoC1G1T0

    elif collection_type == 'motif_library': # ok
        motifLib.append(collection)
    elif collection_type == 'logic_constraints': # ok
        logicConstraints = collection

    elif collection_type == 'eugene_rules': # ok
        eugeneRules = collection
    elif collection_type == 'genetic_locations': # ok
        geneticLocations = collection
    elif collection_type == 'measurement_std': # ok
        measurememeasurementStandardsntstd = collection
    elif collection_type == 'header': # ok
        header = collection

# extraccion y creacion de los archivos de citometria
def splitCytometry():
    if not os.path.exists(cytometryFolder):
        os.makedirs(cytometryFolder)
    if (len(cytometryMap) == 0):
        print('No cytometry data')
    else:
        for cytometry, cytometryData in cytometryMap.items():
            cytometryPath = f"{cytometryFolder}{cytometry}_cytometry_{ucfPath.split('/')[4].split('.')[0]}.json"
            try:
                with open(cytometryPath, 'w') as f:
                    json.dump(cytometryData, f, indent=2)
                print(f"Cytometry file for {cytometry} created at {cytometryPath}")
            except Exception as e:
                print(f"Error writing cytometry file: {e}")

# extraccion y creacion de los archivos de toxicidad
def splitTocity():
    if not os.path.exists(toxicityFolder):
        os.makedirs(toxicityFolder)
    if (len(toxixityMap) == 0):
        print('No toxicity data')
    else:
        for toxicity, toxicityData in toxixityMap.items():
            toxicityPath = f"{toxicityFolder}{toxicity}_toxicity_{ucfPath.split('/')[4].split('.')[0]}.json"
            try:
                with open(toxicityPath, 'w') as f:
                    json.dump(toxicityData, f, indent=2)
                print(f"Toxicity file for {toxicity} created at {toxicityPath}")
            except Exception as e:
                print(f"Error writing toxicity file: {e}")

# extraccion y creacion de los archivos de constraints
def splitCircuitConstraints():
    constraints = {}
    constraints['logic_constraints'] = logicConstraints
    constraints['motif_library'] = motifLib
    constraints['eugene_rules'] = eugeneRules
    constraints['genetic_locations'] = geneticLocations
    constraints['measurement_std'] = measurementStandards
    constraints['header'] = header
    circuitConstraintsPath = f"{resultFolder}/circuit_constraints_{ucfPath.split('/')[4].split('.')[0]}.json"
    try:
        with open(circuitConstraintsPath, 'w') as f:
            json.dump(constraints, f, indent=2)
        print(f"Circuit constraints file created at {circuitConstraintsPath}")
    except Exception as e:
        print(f"Error writing circuit constraints file: {e}")


splitTocity()
splitCytometry()
splitCircuitConstraints()