from pydantic import BaseModel, ConfigDict
from typing import Optional

class SubjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class SubjectCreate(SubjectBase):
    pass

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class SubjectOut(SubjectBase):
    id: int

    model_config = ConfigDict(from_attributes=True)