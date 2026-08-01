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
    """Check API health status.

    Returns:
        dict: A mapping with keys ``status`` (str, always ``"ok"``) and
        ``timestamp`` (str, current UTC time in ISO 8601 format).

    Example:
        >>> response = client.get("/health")
        >>> response.json()
        {'status': 'ok', 'timestamp': '2026-08-01T12:00:00+00:00'}
    """
    return {
        "status": "ok",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    """Create a new task.

    Args:
        payload (TaskCreate): The task data to create, including title,
            description, status, priority, assignee, and due date.

    Returns:
        TaskResponse: The newly created task, including its generated id,
        computed ``is_overdue`` flag, and created/updated timestamps.

    Raises:
        HTTPException: 409 Conflict if a task with the same title,
            description, status, priority, and assignee already exists.

    Example:
        >>> response = client.post("/tasks", json={"title": "Write docs"})
        >>> response.status_code
        201
    """
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
    """List tasks, optionally filtered by status, priority, overdue state, or search text.

    Args:
        status (TaskStatus | None): If provided, only include tasks with this status.
        priority (TaskPriority | None): If provided, only include tasks with this priority.
        overdue (bool | None): If provided, only include tasks whose ``is_overdue``
            flag matches this value.
        search (str | None): If provided, only include tasks whose title or
            description contains this text (case-insensitive).

    Returns:
        list[TaskResponse]: The tasks matching all provided filters.

    Example:
        >>> response = client.get("/tasks", params={"status": "ToDo"})
        >>> response.status_code
        200
    """
    return storage.get_all_tasks(status=status, priority=priority, overdue=overdue, search=search)

@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: str) -> TaskResponse:
    """Retrieve a single task by its id.

    Args:
        task_id (str): The unique id of the task to retrieve.

    Returns:
        TaskResponse: The matching task.

    Raises:
        HTTPException: 404 Not Found if no task with the given id exists.

    Example:
        >>> response = client.get("/tasks/123")
        >>> response.status_code
        200
    """
    task = storage.get_task_by_id(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")
    return task


@app.patch("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: str, payload: TaskUpdate) -> TaskResponse:
    """Partially update an existing task.

    Args:
        task_id (str): The unique id of the task to update.
        payload (TaskUpdate): The fields to update; unset fields are left
            unchanged. If ``status`` is set, the transition from the task's
            current status is validated.

    Returns:
        TaskResponse: The updated task.

    Raises:
        HTTPException: 404 Not Found if no task with the given id exists.
        HTTPException: 422 Unprocessable Entity if ``payload.status`` is set
            and the transition from the task's current status is not among
            the allowed transitions (raised by ``validate_status_transition``).

    Example:
        >>> response = client.patch("/tasks/123", json={"status": "InProgress"})
        >>> response.status_code
        200
    """
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
    """Delete a task by its id.

    Args:
        task_id (str): The unique id of the task to delete.

    Returns:
        None: Responds with HTTP 204 No Content on success.

    Raises:
        HTTPException: 404 Not Found if no task with the given id exists.

    Example:
        >>> response = client.delete("/tasks/123")
        >>> response.status_code
        204
    """
    deleted = storage.delete_task(task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task with id {task_id} not found")