from reactpy import component, html, use_state, use_effect
from chatLogic import ChatLogic, run_async
from fastapi import FastAPI
from reactpy.backend.fastapi import configure

# Initialize ChatLogic instance
chat_logic = ChatLogic()

@component
def ChatApp():
    # State variables
    messages, set_messages = use_state([])
    input_message, set_input_message = use_state("")
    selected_file, set_selected_file = use_state(None)
    output_files, set_output_files = use_state([])
    ucf_options, set_ucf_options = use_state([])
    selected_ucf, set_selected_ucf = use_state(None)

    # Load initial state from ChatLogic
    @use_effect
    async def load_state():
        state = await chat_logic.get_state()
        set_messages(state["messages"])
        set_output_files(state["output_files"])
        set_ucf_options(state["ucf_options"])

    # Handle sending a message
    async def send_message(event):
        if input_message.strip():
            await run_async(chat_logic.send_message())
            updated_state = await chat_logic.get_state()
            set_messages(updated_state["messages"])
            set_input_message("")

    # Handle file selection
    def preview_file(file_name):
        if file_name.endswith(('.txt', '.csv', '.json')):
            with open(file_name, 'r') as f:
                content = f.read()
            return html.pre(content)
        elif file_name.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return html.img({"src": file_name, "style": {"maxWidth": "100%"}})
        elif file_name.endswith('.pdf'):
            return html.p(f"PDF preview not supported directly. File: {file_name}")
        else:
            return html.p("Preview not supported for this file type.")

    # File preview
    preview_content = None
    if selected_file:
        preview_content = preview_file(selected_file)

    return html.div(
        {
            "style": {
                "display": "flex",
                "flexDirection": "row",
                "height": "100vh",
                "backgroundColor": "#0e1117",
                "color": "#ffffff",
                "fontFamily": "Arial, sans-serif",
            }
        },
        # Sidebar
        html.div(
            {
                "style": {
                    "flex": "1",
                    "padding": "1rem",
                    "borderRight": "1px solid #ccc",
                }
            },
            html.h2("UCF Selection"),
            html.select(
                {
                    "value": selected_ucf,
                    "onChange": lambda e: set_selected_ucf(e["target"]["value"]),
                    "style": {
                        "width": "100%",  # Full width dropdown
                        "padding": "0.5rem",
                        "border": "1px solid #ccc",
                        "borderRadius": "5px",
                        "backgroundColor": "#1c1e22",
                        "color": "#ffffff",
                    },
                },
                [html.option({"value": ucf["id"]}, ucf["name"]) for ucf in ucf_options],
            ),

            html.h2("Files"),
            html.div(
                {
                    "style": {
                        "height": "400px",
                        "overflowY": "auto",
                        "border": "1px solid #ccc",
                        "padding": "0.5rem",
                    }
                },
                [
                    html.button(
                        {
                            "onClick": lambda f=file: set_selected_file(f),
                            "style": {
                                "display": "block",
                                "marginBottom": "0.5rem",
                                "backgroundColor": "transparent",
                                "border": "1px solid #ccc",
                                "padding": "0.5rem",
                                "cursor": "pointer",
                            },
                        },
                        f"📄 {file}",
                    )
                    for file in output_files
                ] if output_files else html.p("No files generated."),
            ),
        ),
        # Main Content
        html.div(
            {
                "style": {
                    "flex": "4",
                    "padding": "1rem",
                }
            },
            # Messages
            html.div(
                {
                    "style": {
                        "height": "400px",
                        "overflowY": "auto",
                        "border": "1px solid #ccc",
                        "padding": "1rem",
                        "backgroundColor": "#1c1e22",
                    }
                },
                [
                    html.div(
                        {
                            "style": {
                                "marginBottom": "1rem",
                                "padding": "0.5rem",
                                "borderRadius": "5px",
                                "backgroundColor": "#2e333a"
                                if msg["isUser"]
                                else "#3e454d",
                            }
                        },
                        html.strong("You: " if msg["isUser"] else "Assistant: "),
                        msg["text"],
                    )
                    for msg in messages
                ],
            ),
            # File preview section
            html.div(
                {"style": {"marginTop": "1rem"}}, html.h3("Previewing File"), preview_content
            ),
            # Input field
            html.div(
                {
                    "style": {
                        "position": "sticky",
                        "bottom": "0",
                        "padding": "1rem",
                        "borderTop": "1px solid #ccc",
                        "backgroundColor": "#0e1117",
                    }
                },
                html.input(
                    {
                        "type": "text",
                        "value": input_message,
                        "onChange": lambda e: set_input_message(e["target"]["value"]),
                        "placeholder": "Type your message",
                        "style": {
                            "width": "calc(100% - 60px)",
                            "padding": "0.5rem",
                            "marginRight": "10px",
                            "border": "1px solid #ccc",
                            "borderRadius": "5px",
                        },
                    }
                ),
                html.button(
                    {
                        "onClick": send_message,
                        "style": {
                            "padding": "0.5rem 1rem",
                            "backgroundColor": "#4CAF50",
                            "color": "white",
                            "border": "none",
                            "borderRadius": "5px",
                            "cursor": "pointer",
                        },
                    },
                    "Send",
                ),
            ),
        ),
    )

# Run the ReactPy app

# Create a FastAPI instance
fastapi_app = FastAPI()

# Configure the ReactPy app with the FastAPI app
configure(fastapi_app, ChatApp)

if __name__ == "__main__":
    import uvicorn

    # Run the FastAPI app
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)
