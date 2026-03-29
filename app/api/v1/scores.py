from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud.score import ScoreRepository
from app.crud.student import StudentRepository
from app.crud.subject import SubjectRepository
from app.schemas.score import ScoreCreate, ScoreUpdate, ScoreOut, ScoreWithDetails

router = APIRouter(prefix="/scores", tags=["scores"])

async def get_score_repo(db: AsyncSession = Depends(get_db)) -> ScoreRepository:
    return ScoreRepository(db)

@router.post("/", response_model=ScoreOut, status_code=status.HTTP_201_CREATED)
async def create_score(
    score_in: ScoreCreate,
    repo: ScoreRepository = Depends(get_score_repo),
    student_repo: StudentRepository = Depends(lambda db=Depends(get_db): StudentRepository(db)),
    subject_repo: SubjectRepository = Depends(lambda db=Depends(get_db): SubjectRepository(db))
):
    # Проверяем существование студента и предмета
    student = await student_repo.get(score_in.student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    subject = await subject_repo.get(score_in.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Проверяем, не существует ли уже оценка для этого студента и предмета
    existing = await repo.get_student_score_for_subject(score_in.student_id, score_in.subject_id)
    if existing:
        raise HTTPException(status_code=400, detail="Score for this student and subject already exists")

    return await repo.create(score_in)

@router.get("/", response_model=List[ScoreOut])
async def read_scores(
    skip: int = 0,
    limit: int = 100,
    repo: ScoreRepository = Depends(get_score_repo)
):
    return await repo.get_multi(skip=skip, limit=limit)

@router.get("/{score_id}", response_model=ScoreWithDetails)
async def read_score(
    score_id: int,
    repo: ScoreRepository = Depends(get_score_repo)
):
    score = await repo.get(score_id)
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    return score

@router.patch("/{score_id}", response_model=ScoreOut)
async def update_score(
    score_id: int,
    score_in: ScoreUpdate,
    repo: ScoreRepository = Depends(get_score_repo)
):
    score = await repo.get(score_id)
    if not score:
        raise HTTPException(status_code=404, detail="Score not found")
    return await repo.update(score, score_in)

@router.delete("/{score_id}", response_model=ScoreOut)
async def delete_score(
    score_id: int,
    repo: ScoreRepository = Depends(get_score_repo)
):
    deleted = await repo.delete(score_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Score not found")
    return deleted

@router.get("/student/{student_id}", response_model=List[ScoreWithDetails])
async def read_scores_by_student(
    student_id: int,
    repo: ScoreRepository = Depends(get_score_repo),
    student_repo: StudentRepository = Depends(lambda db=Depends(get_db): StudentRepository(db))
):
    student = await student_repo.get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return await repo.get_student_scores_with_details(student_id)

@router.get("/subject/{subject_id}", response_model=List[ScoreOut])
async def read_scores_by_subject(
    subject_id: int,
    repo: ScoreRepository = Depends(get_score_repo),
    subject_repo: SubjectRepository = Depends(lambda db=Depends(get_db): SubjectRepository(db))
):
    subject = await subject_repo.get(subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    return await repo.get_by_subject(subject_id)