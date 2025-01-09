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
    
class Shapes(BaseModel):
    ana_id:str
    video_id:str
    name:str
    shapes:str


class DrillHole(BaseModel):
    Pattern_Name: str
    Hole_id: str
    Drillhole_X: float
    Drillhole_Y: float
    Drillhole_Z: float
    Drillhole_ToeX: float
    Drillhole_ToeY: float
    Drillhole_ToeZ: float
    Drillhole_Length: float
    Drillhole_Dip: int
    Drillhole_Azimuth: int
    pixel_x: Optional[int] = None
    pixel_y: Optional[int] = None
    pixel_r: Optional[int] = None
    pixel_depth: Optional[int] = None

    @classmethod
    def from_csv(cls, line: str):
        try:
            data = line.split(",")
            drillhole_data = {
                "Pattern_Name": data[0],
                "Hole_id": data[1],
                "Drillhole_X": float(data[2]),
                "Drillhole_Y": float(data[3]),
                "Drillhole_Z": float(data[4]),
                "Drillhole_ToeX": float(data[5]),
                "Drillhole_ToeY": float(data[6]),
                "Drillhole_ToeZ": float(data[7]),
                "Drillhole_Length": float(data[8]),
                "Drillhole_Dip": int(data[9]),
                "Drillhole_Azimuth": int(data[10]),
                "pixel_x": cls.safe_int(data[11]) if len(data) > 11 else None,
                "pixel_y": cls.safe_int(data[12]) if len(data) > 12 else None,
                "pixel_r": cls.safe_int(data[13]) if len(data) > 13 else None,
                "pixel_depth": cls.safe_int(data[14]) if len(data) > 14 else None
            }
            return cls(**drillhole_data)  # Use Pydantic's automatic validation and initialization
        except Exception as e:
            print(f"Failed to read CSV data into DrillHole: {e}")
            return None
    @staticmethod
    def safe_int(value: str):
        try:
            return int(value)
        except ValueError:
            print(f"Invalid integer value: {value}")
            return None  # or return a default value like 0 if preferred