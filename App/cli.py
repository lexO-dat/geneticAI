import requests
import json
import os
import time

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
            self.manual_ucf = True  # Disable automatic UCF detection
            print(f"Selected UCF (Manual): {ucf_options[ucf_id]['name']}\n")
        else:
            print("Invalid UCF ID. Please try again.")

    def auto_select_ucf(self, input_message):
        """Automatically select UCF based on input, if manual mode is off."""
        if self.manual_ucf:  # Skip automatic selection if manual mode is active
            return

        print("Bot: Automatically selecting UCF based on input...")
        try:
            response = requests.post(
                "http://localhost:8001/v1/rag/run",
                json={"question": "what ucf you select based on this prompt: " + input_message + ". REMEMBER, ONLY RETURN THE UCF NAME, WHITOUT ANY EXPLANATION"},
            )
            response.raise_for_status()
            selected_ucf_name = response.json().get("selected_ucf", "")
            
            # Match the detected UCF name with available options
            for ucf in ucf_options:
                if ucf['name'] == selected_ucf_name:
                    self.selected_ucf = ucf['id']
                    print(f"Bot: Auto-selected UCF: {ucf['name']}")
                    return

            print("Bot: Failed to detect UCF. Using default UCF.")
        except Exception as e:
            print(f"Error selecting UCF: {e}")

    def send_message(self, input_message):
        """Send a message and handle responses."""
        if not input_message.strip():
            print("Message cannot be empty.")
            return

        # Add user message to history
        self.messages.append({"text": input_message, "isUser": True})
        print(f"\nYou: {input_message}")

        # Automatically select UCF unless manually set
        self.auto_select_ucf(input_message)

        # Generate Verilog Code
        print("Bot: Generating Verilog code...")
        verilog_code = self.generate_verilog(input_message)
        if not verilog_code:
            print("Bot: Failed to generate Verilog code.")
            return

        # Process with Cello
        print("Bot: Processing with Cello...")
        self.process_with_cello(verilog_code)

    def generate_verilog(self, prompt):
        """Generate Verilog code via API."""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "custom-llama-v1", "prompt": prompt},
            )
            response.raise_for_status()
            verilog_code = ""

            for line in response.iter_lines():
                if line:
                    parsed_line = json.loads(line)
                    verilog_code += parsed_line.get("response", "")

            print(f"Bot: Generated Verilog Code:\n{verilog_code}")
            return verilog_code

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

            # Update output details
            self.folder_name = cello_data.get("folder_name", "")
            self.output_files = cello_data.get("output_files", [])
            print("Bot: Cello Processing Completed!")
            print(f"Bot: Folder Name - {self.folder_name}")
            print("Bot: Generated Files:")
            for file in self.output_files:
                print(f"- {file}")

            # Offer download
            for file in self.output_files:
                self.download_file(self.folder_name, file)

        except Exception as e:
            print(f"Error processing with Cello: {e}")

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
