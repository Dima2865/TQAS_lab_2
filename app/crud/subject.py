from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseRepository
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate

class SubjectRepository(BaseRepository[Subject, SubjectCreate, SubjectUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Subject, db)

    async def get_by_name(self, name: str) -> Optional[Subject]:
        result = await self.db.execute(
            select(Subject).where(Subject.name == name)
        )
        return result.scalar_one_or_none()