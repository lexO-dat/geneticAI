
# Genetic AI

Synthetic biology is an interdisciplinary field that combines biology, engineering and computation to design and build new biological systems or modify existing ones for specific purposes. Within this context, the creation and optimization of genetic circuits are key tasks to advance in the creation of efficient and functional systems.

This project is focused on developing an automated system to analyze and create genetic circuits using tools such as CELLO and artificial intelligence.

# Prerequisites:
## Ollama:
- To install Ollama, go to the [Ollama web page](https://ollama.com/) and follow the installation instructions in the documentation. (NOTE: if you have a NVIDIA gpu you have to configure the NVIDIA cuda drivers).
- On my notebook with 8gb of ram and an i5 11th i used the 3.1:8b model version of Ollama, but i recommend the 70b version model or more.
- To execute Ollama run:
```
ollama serve
```
- Create the custom verilog creator model based on the "custom-llama.txt" file with the following command:
```
ollama create < custom model name > -f custom-llama.txt
```

NOTE: if you are using the cli mode, you have to change the name of the verilog creator model in the part of the code where is called. (you have to do the same on the frontend code)

## CELLO:
- Python 3.11 version (if you want to run it locally).
- To run the CELLO api run:
``` bash
cd App/cello
virtualenv -p python3.11 cello # to create a virtualenv
source cello/bin/activate
pip install -r requirements.txt
python run.py
```

NOTE: this will execute the cello api in 0.0.0.0:8000, to see more further information about the endpoints go to: 0.0.0.0:8000/docs.

## Frontend:
- nodejs and pnpm installed
- To install all the dependencies and run the front run the following commands:
``` bash
cd front/chat
pnpm install
pnpm run dev
```

## RAG system:
- To run the rag system run the following commands:
``` bash
cd llm
virtualenv -p python3.11 rag # to create a virtualenv
source rag/bin/activate
pip install -r requirements.txt
python RAG.py
```

NOTE: you have to create a supabase account and locate the SUPABASE_URL and SUPABASE_KEY to create the vectorial database and also have to create a .env file:

```
SUPABASE_URL="SUPABASE URL"
SUPABASE_KEY="SUPABASE KEY"
```

I'm currently working on a code that upload to the vectorial database a chunked txt file that contains all the ucf files information.

- The ucf txt file have to be like this:
``` txt
# Bth1C1G1T1 inputs
Input Sensors:
- BA_sensor
- IPTG_sensor
- aTc_sensor

# Bth1C1G1T1 outputs
Output Sensors:
- nanoluc_reporter
- nanoluc_reporter_2

# Bth1C1G1T1 organism
Organism:
- Bacteroides thetaiotaomicron VPI-5482

# Bth1C1G1T1 genome
Genome:
- wildtype with dCas9 integrated

# Bth1C1G1T1 media
Media:
- TYG (10 g/L Tryptone Peptone, 5 g/L Yeast Extract, 11 mM Glucose, 100 mM KPO4 (pH7.2), 72\u00b5M CaCl2, 0.4 \u00b5g/ml FeSO4 and 1\u00b5g/mL Resazurin, 1.2 \u00b5g/ml hematin, 0.5g/mL of L-cysteine, and 1 \u00b5g/ml of Vitamin K (menadione)

# Bth1C1G1T1 temperature
Temperature:
- 37 degrees Celsius

# Bth1C1G1T1 growth
Growth:
- Inoculation: Inoculate individual colonies into TYG media without antibiotics and grow 18 hours overnight in the anaerobic chamber.  Dilution and Induction: Next day, dilute 100-fold into pre-reduced TYG with inducers (no antibiotics), grow for 6 hours in the anaerobic chamber.  Measurement: Plate Reader, data processing for RPUL normalization

# Bth1C1G1T1 logic constraints
Logic constraints:
- NOR -> 7 instances max.
- OUTPUT_OR -> unlimited

# Bth1C1G1T1 posible use
Posible Use:
- It can be used in genetic circuits as a logical switch where dCas9 blocks a promoter until it receives a signal (e.g., chemical induction), enabling combinational control in biological systems.
```

# Running the app

There are 2 options:
- web chat
- cli app

NOTE: for the moment you have to run:
- the cello api in one terminal
- the rag api
- the cli or the frontend

All the information about how to run this modules is on the prerequisites section.

## Running the web chat (i have to correct something on the compose for this)

- You have to install Docker, you can follow the install instructions on their docs page: [Docker docs](https://docs.docker.com/)

- Run the frontend as shown in the Prerequisites section.
- Run the following command to execute the Docker compose (run it ot the root folder of the project):
``` bash
sudo docker compose up
```
This command will run all the RAG system codes and server and the cello api, aditionally you have to run the "ollama serve" command.

## Running the cli app (i have to correct something on the compose for this)

- You have to install Docker, you can follow the install instructions on their docs page: [Docker docs](https://docs.docker.com/)
- Run the following command to execute the Docker compose (run it ot the root folder of the project):
``` bash
sudo docker compose up
```
This command will run all the RAG system codes and server and the cello api, aditionally you have to run the "ollama serve" command.
- Run the cli app on the root folder:
``` bash
python cli.py
```

