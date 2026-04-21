from pydantic import BaseModel

class EditModell(BaseModel):
    product_id: int
    nev: str
    marka_nev: str
    polc_nev: str

class TermekSablon(BaseModel):
    nev: str
    marka_id: int
    polc_id: int


class NevSablon(BaseModel):
    nev: str

class GetIDBrand(BaseModel):
    marka_id: int