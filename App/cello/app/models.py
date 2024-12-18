# models.py
from pydantic import BaseModel, Field
from typing import Optional

class CelloOptions(BaseModel):
    verbose: bool
    log_overwrite: bool
    print_iters: bool
    exhaustive: bool
    test_configs: bool

class CelloRequest(BaseModel):
    verilog_file: Optional[str] = None
    verilog_code: Optional[str] = Field(
        None, description="Código Verilog directamente proporcionado en la solicitud."
    )
    ucf_index: Optional[int] = None
    custom_ucf: Optional[str] = None
    custom_input: Optional[str] = None
    custom_output: Optional[str] = None
    options: CelloOptions

    class Config:
        schema_extra = {
            "example": {
                "verilog_file": "and",
                "verilog_code": "module and_gate(...); ... endmodule",
                "ucf_index": 1,
                "options": {
                    "verbose": True,
                    "log_overwrite": False,
                    "print_iters": False,
                    "exhaustive": False,
                    "test_configs": False
                }
            }
        }
