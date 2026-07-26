from datetime import datetime, timezone

from fastapi import FastAPI, status, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models import TaskCreate, TaskUpdate, TaskStatus, TaskPriority, TaskResponse
from app import storage
from app.business_rules import validate_status_transition

app = FastAPI(
    title="Task Tracker API",
    description="Module 1 Task Tracker REST API — learning project using FastAPI, Pydantic, and JSON file storage.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check() -> dict:
    """
    Simple health check endpoint.
    Returns HTTP 200 with a status flag and current UTC timestamp.
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    try:
        return storage.add_task(payload)
    except storage.DuplicateTaskError as exc:
        raise HTTPException(status_code=409, detail="Task already exists") from exc


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
    overdue: bool | None = None,
    search: str | None = None,
) -> list[TaskResponse]:
    return storage.get_all_tasks(status=status, priority=priority, overdue=overdue, search=search)

@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    if payload.status is not None:
        existing = storage.get_task_by_id(task_id)
        if existing is None:
            raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
        validate_status_transition(existing.status, payload.status)

    task = storage.update_task(task_id, payload)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: str) -> None:
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")