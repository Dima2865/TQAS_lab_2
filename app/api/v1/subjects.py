from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.subject import SubjectRepository
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectOut

router = APIRouter(prefix="/subjects", tags=["subjects"])

async def get_subject_repo(db: AsyncSession = Depends(get_db)) -> SubjectRepository:
    return SubjectRepository(db)

@router.post("/", response_model=SubjectOut, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject_in: SubjectCreate,
    repo: SubjectRepository = Depends(get_subject_repo)
):
    existing = await repo.get_by_name(subject_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Subject with this name already exists")
    return await repo.create(subject_in)

@router.get("/", response_model=List[SubjectOut])
async def read_subjects(
    skip: int = 0,
    limit: int = 100,
    repo: SubjectRepository = Depends(get_subject_repo)
):
    return await repo.get_multi(skip=skip, limit=limit)

@router.get("/{subject_id}", response_model=SubjectOut)
async def read_subject(
    subject_id: int,
    repo: SubjectRepository = Depends(get_subject_repo)
):
    subject = await repo.get(subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return subject

@router.patch("/{subject_id}", response_model=SubjectOut)
async def update_subject(
    subject_id: int,
    subject_in: SubjectUpdate,
    repo: SubjectRepository = Depends(get_subject_repo)
):
    subject = await repo.get(subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return await repo.update(subject, subject_in)

@router.delete("/{subject_id}", response_model=SubjectOut)
async def delete_subject(
    subject_id: int,
    repo: SubjectRepository = Depends(get_subject_repo)
):
    deleted = await repo.delete(subject_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Subject not found")
    return deleted