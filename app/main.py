from fastapi import FastAPI
from app.api import router as v1_router

from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

import os
from pathlib import Path

app = FastAPI(title="Student Scores API", version="1.0.0")

app.include_router(v1_router, prefix="/api/v1")

# Определяем путь к статической папке относительно текущего файла
BASE_DIR = Path(__file__).parent
static_dir = BASE_DIR / "static"

# Монтируем статику только если папка существует
if static_dir.exists() and static_dir.is_dir():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
else:
    print(f"Static directory not found at {static_dir}, skipping mount")

# Корневой эндпоинт (можно оставить как есть)
@app.get("/", response_class=HTMLResponse)
async def read_root():
    index_file = static_dir / "index.html"
    if index_file.exists():
        with open(index_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>API работает. Статическая страница не найдена.</h1>")

# app.mount("/static", StaticFiles(directory="app/static"), name="static")
#
# @app.get("/", response_class=HTMLResponse)
# async def read_root():
#     with open("app/static/index.html", "r", encoding="utf-8") as f:
#         return HTMLResponse(content=f.read())