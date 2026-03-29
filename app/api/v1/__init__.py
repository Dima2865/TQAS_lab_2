from fastapi import APIRouter
from . import students, scores, subjects

router = APIRouter()
router.include_router(students.router)
router.include_router(subjects.router)
router.include_router(scores.router)