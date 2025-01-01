from pydantic import BaseModel
from typing import List, Optional

class Analysis(BaseModel):
    id:str
    name:str

class Operation(BaseModel):
    ana_id:str
    op: str 
    options:dict
    
class UploadFile(BaseModel):
    filename: str
    content_type: str
    file: bytes