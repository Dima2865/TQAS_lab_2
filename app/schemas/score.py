from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

class ScoreBase(BaseModel):
    student_id: int
    subject_id: int
    score: float = Field(..., ge=0, le=100, description="Оценка от 0 до 100")

class ScoreCreate(ScoreBase):
    pass

class ScoreUpdate(BaseModel):
    score: Optional[float] = Field(None, ge=0, le=100)

class ScoreOut(ScoreBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

# Расширенная схема с деталями студента и предмета (для GET /scores/{id})
class ScoreWithDetails(ScoreOut):
    student: Optional['StudentOut'] = None
    subject: Optional['SubjectOut'] = None

    model_config = ConfigDict(from_attributes=True)

# Для избежания циклических импортов используем строки
from .student import StudentOut
from .subject import SubjectOut
ScoreWithDetails.model_rebuild()