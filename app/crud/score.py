from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseRepository
from app.models.score import Score
from app.models.student import Student
from app.models.subject import Subject
from app.schemas.score import ScoreCreate, ScoreUpdate

class ScoreRepository(BaseRepository[Score, ScoreCreate, ScoreUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Score, db)

    async def get_student_score_for_subject(self, student_id: int, subject_id: int) -> Optional[Score]:
        result = await self.db.execute(
            select(Score).where(
                and_(Score.student_id == student_id, Score.subject_id == subject_id)
            )
        )
        return result.scalar_one_or_none()

    async def get_student_scores_with_details(self, student_id: int) -> List[Score]:
        result = await self.db.execute(
            select(Score)
            .where(Score.student_id == student_id)
            .options(selectinload(Score.student), selectinload(Score.subject))
        )
        return result.scalars().all()

    async def get_by_subject(self, subject_id: int) -> List[Score]:
        result = await self.db.execute(
            select(Score).where(Score.subject_id == subject_id)
        )
        return result.scalars().all()