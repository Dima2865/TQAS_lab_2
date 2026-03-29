from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.student import StudentRepository
from app.schemas.student import StudentCreate, StudentUpdate, StudentOut

router = APIRouter(prefix="/students", tags=["students"])

async def get_student_repo(db: AsyncSession = Depends(get_db)) -> StudentRepository:
    return StudentRepository(db)

@router.post("/", response_model=StudentOut, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_in: StudentCreate,
    repo: StudentRepository = Depends(get_student_repo)
):
    # Проверяем, нет ли студента с таким email
    existing = await repo.get_by_email(student_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await repo.create(student_in)

@router.get("/", response_model=List[StudentOut])
async def read_students(
    skip: int = 0,
    limit: int = 100,
    repo: StudentRepository = Depends(get_student_repo)
):
    return await repo.get_multi(skip=skip, limit=limit)

@router.get("/{student_id}", response_model=StudentOut)
async def read_student(
    student_id: int,
    repo: StudentRepository = Depends(get_student_repo)
):
    student = await repo.get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.patch("/{student_id}", response_model=StudentOut)
async def update_student(
    student_id: int,
    student_in: StudentUpdate,
    repo: StudentRepository = Depends(get_student_repo)
):
    student = await repo.get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return await repo.update(student, student_in)

@router.delete("/{student_id}", response_model=StudentOut)
async def delete_student(
    student_id: int,
    repo: StudentRepository = Depends(get_student_repo)
):
    deleted = await repo.delete(student_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Student not found")
    return deleted

@router.get("/by-group/{group_name}", response_model=List[StudentOut])
async def read_students_by_group(
    group_name: str,
    repo: StudentRepository = Depends(get_student_repo)
):
    return await repo.get_by_group(group_name)