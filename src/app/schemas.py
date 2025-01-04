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
    Pattern_Name : str
    Hole_id : str
    Drillhole_X : float
    Drillhole_Y : float
    Drillhole_Z : float
    Drillhole_ToeX : float
    Drillhole_ToeY : float
    Drillhole_ToeZ : float
    Drillhole_Length : float
    Drillhole_Dip :int
    Drillhole_Azimuth : int
    pixel_x : int
    pixel_y : int
    pixel_r : int
    pixel_depth : int
    def __init__(self, line):
        try:
            (self.Pattern_Name ,
            self.Hole_id ,
            self.Drillhole_X ,
            self.Drillhole_Y ,
            self.Drillhole_Z ,
            self.Drillhole_ToeX ,
            self.Drillhole_ToeY ,
            self.Drillhole_ToeZ ,
            self.Drillhole_Length ,
            self.Drillhole_Dip ,
            self.Drillhole_Azimuth ,
            self.pixel_x ,
            self.pixel_y ,
            self.pixel_r ) = line.split(",")
        except Exception as e:
            print(123321)
            print(e)
            pass    
