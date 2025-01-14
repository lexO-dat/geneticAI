import requests
import json
import os
import time
from llm import RAG
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage
import re

ucf_options = [
    {"id": 0, "name": "Bth1C1G1T1"},
    {"id": 1, "name": "Eco1C1G1T1"},
    {"id": 2, "name": "Eco1C2G2T2"},
    {"id": 3, "name": "Eco2C1G3T1"},
    {"id": 4, "name": "Eco2C1G5T1"},
    {"id": 5, "name": "SC1C1G1T1"},
]

class ChatApp:
    def __init__(self):
        self.messages = []
        self.selected_ucf = 1
        self.folder_name = ""
        self.output_files = []
        self.manual_ucf = False

    def display_ucf_options(self):
        """Display UCF options."""
        print("\nAvailable UCF Options:")
        for ucf in ucf_options:
            print(f"{ucf['id']}: {ucf['name']}")

    def set_ucf(self, ucf_id):
        """Set the selected UCF manually."""
        if 0 <= ucf_id < len(ucf_options):
            self.selected_ucf = ucf_id
            self.manual_ucf = True
            print(f"Selected UCF (Manual): {ucf_options[ucf_id]['name']}\n")
        else:
            print("Invalid UCF ID. Please try again.")

    def auto_select_ucf(self, input_message):
        """Automatically select UCF based on input, if manual mode is off."""
        if self.manual_ucf:
            return

        print("Bot: Automatically selecting UCF based on input...")
        try:
            """ response = requests.post(
                "http://localhost:8001/v1/rag/run",
                json={"question": "what ucf you select based on this prompt: " + input_message + ". REMEMBER, ONLY RETURN THE UCF NAME, WHITOUT ANY EXPLANATION"},
            ) """
            response = RAG.chat_response("what ucf you select based on this promot: " + input_message + ". REMEMBER, ONLY RETURN THE UCF NAME, WHITOUT ANY EXPLANATION")
            selected_ucf_name = response
            
            # Match UCF name to ID
            for ucf in ucf_options:
                if ucf['name'] == selected_ucf_name:
                    self.selected_ucf = ucf['id']
                    print(f"Bot: Auto-selected UCF: {ucf['name']}")
                    return

            print("Bot: Failed to detect UCF. Using default UCF.")
            self.selected_ucf = 1
        except Exception as e:
            print(f"Error selecting UCF: {e}")

    def send_message(self, input_message):
        """Send a message and handle responses."""
        if not input_message.strip():
            print("Message cannot be empty.")
            return

        self.messages.append({"text": input_message, "isUser": True})
        print(f"\nYou: {input_message}")

        self.auto_select_ucf(input_message)

        # Generate The verilog code with the ollama model
        print("Bot: Generating Verilog code...")
        verilog_code = self.generate_verilog(input_message)
        if not verilog_code:
            print("Bot: Failed to generate Verilog code.")
            return

        print("Bot: Processing with Cello...")
        self.process_with_cello(verilog_code)

    def generate_verilog(self, prompt):
        """Generate Verilog code via API and extract module definition."""
        try:
            llm = ChatOllama(
                base_url="http://localhost:11434",
                model="custom-llama-8b",
                system="""
                You are an AI assistant that generates CELLO-compatible Verilog code for genetic circuits. Generate only the Verilog code without explanations unless specifically requested. For logic function requests, return a single `module top (...) endmodule` block containing inputs, outputs, and assign statements.

                Key requirements:
                - Output only Verilog code without commentary
                - Do not use bit arrays [x:y] in modules - use individual wires
                - Do not use clk or anything like that
                - Use & and | operators instead of && and ||
                - Follow standard Verilog module structure with proper indentation

                3. Response Protocol:
                - Always provide ONLY THE VERILOG CODE CREATED BY YOU

                Example format:
                module top(
                  input wire A,
                  input wire B,
                  output wire Y
                );
                  assign Y = A & B;
                endmodule

                Valid operators and constructs:
                - Basic logic: &, |, ~
                - Module declaration: module, endmodule
                - Port types: input wire, output wire
                - Internal signals: wire
                - Assignments: assign

                Example implementations:
                1. AND gate:
                module top(
                  input wire A,
                  input wire B, 
                  output wire Y
                );
                  assign Y = A & B;
                endmodule

                2. Combinational circuit:
                module m0xA6(output out, input in1, in2, in3);
                    always @(in1, in2, in3)
                        begin
                            case({in1, in2, in3})
                                3'b000: {out} = 1'b1;
                                3'b001: {out} = 1'b0;
                                3'b010: {out} = 1'b1;
                                3'b011: {out} = 1'b0;
                                3'b100: {out} = 1'b0;
                                3'b101: {out} = 1'b1;
                                3'b110: {out} = 1'b1;
                                3'b111: {out} = 1'b0;
                            endcase
                        end
                endmodule

                3. Priority Detector:
                module priority_detector(output outX, outY, input A, B, C);
                    wire outZ;
                        always@(C, B, A)
                            begin
                                case({C, B, A})
                                    3'b000: {outZ, outY, outX} = 3'b000;
                                    3'b001: {outZ, outY, outX} = 3'b001;
                                    3'b010: {outZ, outY, outX} = 3'b100;
                                    3'b011: {outZ, outY, outX} = 3'b100;
                                    3'b100: {outZ, outY, outX} = 3'b010;
                                    3'b101: {outZ, outY, outX} = 3'b001;
                                    3'b110: {outZ, outY, outX} = 3'b100;
                                    3'b111: {outZ, outY, outX} = 3'b100;
                                endcase
                            end
                endmodule
                """
            )

            response = llm.invoke([HumanMessage(content=prompt)])
            
            # Extract content from the response
            responseText = response.content
            """ print(f"Bot: Generated Response:\n{responseText}")
 """
            module_pattern = r'module\s+.*?endmodule'
            matches = re.findall(module_pattern, responseText, re.DOTALL)
            
            if matches:
                extracted_code = matches[0]
                print(f"Bot: Generated Verilog Code:\n{extracted_code}")
                return extracted_code
            else:
                print("No Verilog module found in the generated code.")
                return ""
                
        except Exception as e:
            print(f"Error generating Verilog: {e}")
            return ""

    def process_with_cello(self, verilog_code):
        """Process Verilog code with Cello API."""
        try:
            cello_response = requests.post(
                "http://localhost:8000/v1/run",
                json={
                    "verilogCode": verilog_code,
                    "ucfIndex": self.selected_ucf,
                    "options": {
                        "verbose": True,
                        "log_overwrite": False,
                        "print_iters": False,
                        "exhaustive": False,
                        "test_configs": False,
                    },
                },
            )
            cello_response.raise_for_status()
            cello_data = cello_response.json()

            self.folder_name = cello_data.get("folder_name", "")
            self.output_files = cello_data.get("output_files", [])
            print("Bot: Cello Processing Completed!")
            print("--------------------------------------------------------------------------------")
            print(f"Bot: Folder Name - {self.folder_name}")
            print("Bot: Generated Files:")
            for file in self.output_files:
                print(f"- {file}")

            # TODO: ask for the email and send the generated files via email
            for file in self.output_files:
                self.download_file(self.folder_name, file)
            
            print("--------------------------------------------------------------------------------")



        except Exception as e:
            print(f"Error processing with Cello: {e}")

    # TODO: make this work
    def download_file(self, folder_name, file):
        """Download a file from the server."""
        url = f"http://localhost:8000/v1/outputs/{folder_name}/{file}"
        try:
            response = requests.get(url)
            response.raise_for_status()

            save_path = os.path.join("Downloads", folder_name)
            os.makedirs(save_path, exist_ok=True)
            file_path = os.path.join(save_path, file)

            with open(file_path, "wb") as f:
                f.write(response.content)

            print(f"Bot: Downloaded - {file_path}")

        except Exception as e:
            print(f"Failed to download {file}: {e}")

    # Main loop
    def chat_loop(self):
        """Interactive chat loop."""
        print("Welcome to the Chat CLI! Type 'exit' to quit.")
        print("Type 'ucf' to see UCF options or 'setucf [id]' to select a UCF.\n")

        while True:
            user_input = input("You: ")

            if user_input.lower() == "exit":
                print("Goodbye!")
                break
            elif user_input.lower() == "ucf":
                self.display_ucf_options()
            elif user_input.lower().startswith("setucf"):
                try:
                    _, ucf_id = user_input.split()
                    self.set_ucf(int(ucf_id))
                except ValueError:
                    print("Invalid command. Usage: setucf [id]")
            else:
                self.send_message(user_input)


if __name__ == "__main__":
    app = ChatApp()
    app.chat_loop()