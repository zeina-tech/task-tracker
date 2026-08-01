import json
import uuid
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Optional

from app.models import TaskCreate, TaskPriority, TaskResponse, TaskStatus, TaskUpdate

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "tasks.json"

class DuplicateTaskError(Exception):
    """Raised when a task with identical fields already exists."""
    
def _load_tasks() -> dict[str, TaskResponse]:
    if not DATA_FILE.exists():
        return {}

    raw = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return {
        item["id"]: TaskResponse(**item)
        for item in raw
    }


def _save_tasks(tasks: dict[str, TaskResponse]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    payload = [task.model_dump(mode="json") for task in tasks.values()]
    DATA_FILE.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def _compute_is_overdue(due_date: Optional[date], status: TaskStatus) -> bool:
    if due_date is None:
        return False
    return due_date < datetime.now(timezone.utc).date() and status != TaskStatus.DONE


_tasks: dict[str, TaskResponse] = _load_tasks()


def add_task(payload: TaskCreate) -> TaskResponse:
    """Create and persist a new task, rejecting duplicates.

    Args:
        payload (TaskCreate): The task data to create.

    Returns:
        TaskResponse: The newly created task, with generated id, computed
        ``is_overdue`` flag, and created/updated timestamps.

    Raises:
        DuplicateTaskError: If a task with the same title, description,
            status, priority, and assignee already exists.
    """
    duplicate_key = (
        payload.title.strip(),
        payload.description or "",
        payload.status.value,
        payload.priority.value,
        payload.assignee or "",
    )
    for existing in _tasks.values():
        existing_key = (
            existing.title.strip(),
            existing.description or "",
            existing.status.value,
            existing.priority.value,
            existing.assignee or "",
        )
        if existing_key == duplicate_key:
            raise DuplicateTaskError("Task already exists")

    task_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    task = TaskResponse(
        id=task_id,
        title=payload.title,
        description=payload.description or "",
        status=payload.status,
        priority=payload.priority,
        assignee=payload.assignee,
        due_date=payload.due_date,
        is_overdue=_compute_is_overdue(payload.due_date, payload.status),
        created_at=now,
        updated_at=now,
    )
    _tasks[task_id] = task
    _save_tasks(_tasks)
    return task


def get_all_tasks(
    status: Optional[TaskStatus] = None,
    priority: Optional[TaskPriority] = None,
    overdue: Optional[bool] = None,
    search: Optional[str] = None,
) -> list[TaskResponse]:
    """Retrieve all tasks, optionally filtered by status, priority, overdue state, or search text.

    Args:
        status (Optional[TaskStatus]): If provided, only include tasks with this status.
        priority (Optional[TaskPriority]): If provided, only include tasks with this priority.
        overdue (Optional[bool]): If provided, only include tasks whose ``is_overdue``
            flag matches this value.
        search (Optional[str]): If provided, only include tasks whose title or
            description contains this text (case-insensitive).

    Returns:
        list[TaskResponse]: The tasks matching all provided filters.
    """
    results = list(_tasks.values())
    if status is not None:
        results = [task for task in results if task.status == status]
    if priority is not None:
        results = [task for task in results if task.priority == priority]
    if overdue is not None:
        results = [task for task in results if task.is_overdue == overdue]
    if search is not None:
        needle = search.strip().lower()
        results = [
            task for task in results
            if needle in task.title.lower() or needle in task.description.lower()
        ]
    return results


def get_task_by_id(task_id: str) -> Optional[TaskResponse]:
    """Retrieve a single task by its id.

    Args:
        task_id (str): The unique id of the task to retrieve.

    Returns:
        Optional[TaskResponse]: The matching task, or None if no task with
        the given id exists.
    """
    return _tasks.get(task_id)


def update_task(task_id: str, payload: TaskUpdate) -> Optional[TaskResponse]:
    """Apply a partial update to an existing task and persist the change.

    Args:
        task_id (str): The unique id of the task to update.
        payload (TaskUpdate): The fields to update; unset fields are left
            unchanged.

    Returns:
        Optional[TaskResponse]: The updated task, or None if no task with
        the given id exists.
    """
    existing = _tasks.get(task_id)
    if existing is None:
        return None

    updates = payload.model_dump(exclude_unset=True)
    updated_data = existing.model_dump()
    updated_data.update(updates)
    updated_data["updated_at"] = datetime.now(timezone.utc)
    updated_data["is_overdue"] = _compute_is_overdue(
        updated_data["due_date"], TaskStatus(updated_data["status"])
    )

    updated_task = TaskResponse(**updated_data)
    _tasks[task_id] = updated_task
    _save_tasks(_tasks)
    return updated_task


def delete_task(task_id: str) -> bool:
    """Delete a task by its id and persist the change.

    Args:
        task_id (str): The unique id of the task to delete.

    Returns:
        bool: True if a task was found and deleted, False otherwise.
    """
    if task_id in _tasks:
        del _tasks[task_id]
        _save_tasks(_tasks)
        return True
    return False


def _reset() -> None:
    _tasks.clear()
    _save_tasks(_tasks)