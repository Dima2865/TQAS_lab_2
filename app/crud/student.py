from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import BaseRepository
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentUpdate

class StudentRepository(BaseRepository[Student, StudentCreate, StudentUpdate]):
    def __init__(self, db: AsyncSession):
        super().__init__(Student, db)

    async def get_by_email(self, email: str) -> Optional[Student]:
        result = await self.db.execute(
            select(Student).where(Student.email == email)
        )
        return result.scalar_one_or_none()

    async def get_by_group(self, group_name: str) -> List[Student]:
        result = await self.db.execute(
            select(Student).where(Student.group_name == group_name)
        )
        return result.scalars().all()