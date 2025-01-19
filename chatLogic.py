import aiohttp
import asyncio
import json
import re
from llm import RAG
from typing import List, Dict, Optional, Any

class ChatLogic:
    def __init__(self):
        # Initialize state variables
        self.state = {
            "messages": [],
            "input_message": "",
            "is_loading": False,
            "output_files": [],
            "folder_name": "",
            "selected_ucf": 1,
        }

        self.ucf_options = [
            {"id": 0, "name": "Bth1C1G1T1"},
            {"id": 1, "name": "Eco1C1G1T1"},
            {"id": 2, "name": "Eco1C2G2T2"},
            {"id": 3, "name": "Eco2C1G3T1"},
            {"id": 4, "name": "Eco2C1G5T1"},
            {"id": 5, "name": "SC1C1G1T1"},
        ]

    async def process_with_cello(self, verilog_code: str, ucf_id: int) -> Dict:
        """Process the Verilog code with the Cello API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    'http://localhost:8000/v1/run',
                    json={
                        "verilogCode": verilog_code,
                        "ucfIndex": ucf_id,
                        "options": {
                            "verbose": True,
                            "log_overwrite": False,
                            "print_iters": False,
                            "exhaustive": False,
                            "test_configs": False,
                        },
                    },
                ) as response:
                    if not response.ok:
                        print(f"Cello API error: Status {response.status}")
                        raise Exception(f"Cello processing failed with status {response.status}")

                    data = await response.json()
                    print(f"Received Cello response: {json.dumps(data, indent=2)}")
                    return data
        except Exception as e:
            print(f"Error in process_with_cello: {str(e)}")
            raise

    async def send_message(self, set_state, input_message: str) -> None:
        """Main function to handle message sending and processing."""
        if not input_message.strip():
            return

        self.add_message(input_message, True)
        set_state("input_message", "")
        set_state("is_loading", True)

        try:
            # Generate Verilog code
            self.add_message("Generating Verilog code...", False)
            verilog_code = self.generate_verilog(input_message)

            self.add_message("Generated Verilog:", False)
            self.add_message(verilog_code, False)
            self.add_message("Selecting a UCF file...", False)

            # Get UCF selection
            selected_ucf = self.get_ucf_selection(input_message)
            self.add_message(f"Selected UCF: {self.ucf_options[selected_ucf]['name']}", False)
            self.add_message("Processing with Cello...", False)

            # Process with Cello
            cello_data = await self.process_with_cello(verilog_code, selected_ucf)

            # Update state with results
            if cello_data.get("output_files"):
                set_state("output_files", cello_data["output_files"])
            if cello_data.get("folder_name"):
                set_state("folder_name", cello_data["folder_name"])

            # Add final message
            cello_message = (
                json.dumps(cello_data.get("message"), indent=2)
                if isinstance(cello_data.get("message"), dict)
                else cello_data.get("message", "Cello processing completed.")
            )
            self.add_message(cello_message, False)

        except Exception as error:
            print(f"Error in send_message: {str(error)}")
            self.add_message(f"Error: {str(error)}", False)
            raise

        finally:
            set_state("is_loading", False)

    def generate_verilog(self, prompt: str) -> str:
        """Generate Verilog code via API and extract module definition."""
        try:
            response = RAG.verilog_generation(prompt)
            response_text = response.content

            module_pattern = r"module\s+.*?endmodule"
            matches = re.findall(module_pattern, response_text, re.DOTALL)

            if matches:
                extracted_code = matches[0]
                print(f"Generated Verilog Code:\n{extracted_code}")
                return extracted_code
            else:
                print("No Verilog module found in the generated code.")
                return ""

        except Exception as e:
            print(f"Error generating Verilog: {e}")
            raise

    def get_ucf_selection(self, input_message: str) -> int:
        """Automatically select a UCF based on the input message."""
        try:
            response = RAG.chat_response(input_message)
            selected_ucf_name = response

            for ucf in self.ucf_options:
                if ucf["name"] == selected_ucf_name:
                    print(f"Auto-selected UCF: {ucf['name']}")
                    return ucf["id"]

            print(f"Using default UCF: {self.ucf_options[1]['name']}")
            return 1

        except Exception as e:
            print(f"Error selecting UCF: {e}")
            raise

    def add_message(self, text: str, is_user: bool) -> None:
        """Add a message to the chat history."""
        self.state["messages"].append({"text": text, "isUser": is_user})

    def get_state(self) -> Dict[str, Any]:
        """Get the current state for the frontend."""
        return self.state
    
def run_async(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()