from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional

class StudentBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    group_name: Optional[str] = None

class StudentCreate(StudentBase):
    pass

class StudentUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    group_name: Optional[str] = None

class StudentOut(StudentBase):
    id: int

    model_config = ConfigDict(from_attributes=True)