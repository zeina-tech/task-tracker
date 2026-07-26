import importlib

from app import storage


def test_create_task_valid_returns_201_with_full_body(client):
    response = client.post(
        "/tasks",
        json={
            "title": "Write report",
            "description": "Quarterly report",
            "status": "ToDo",
            "priority": "High",
            "assignee": "Zeina",
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Write report"
    assert body["description"] == "Quarterly report"
    assert body["status"] == "ToDo"
    assert body["priority"] == "High"
    assert body["assignee"] == "Zeina"
    assert "id" in body
    assert "created_at" in body
    assert "updated_at" in body


def test_create_task_missing_title_returns_422(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 422


def test_create_task_duplicate_returns_409(client):
    payload = {
        "title": "Unique task",
        "description": "A duplicate should be blocked",
        "status": "ToDo",
        "priority": "High",
        "assignee": "Alex",
    }

    first_response = client.post("/tasks", json=payload)
    second_response = client.post("/tasks", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409
    assert second_response.json()["detail"] == "Task already exists"


def test_create_task_blank_title_returns_422(client):
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 422


def test_create_task_invalid_priority_returns_422(client):
    response = client.post("/tasks", json={"title": "Test", "priority": "Urgent"})
    assert response.status_code == 422


def test_create_task_unknown_field_returns_422(client):
    response = client.post("/tasks", json={"title": "Test", "extra_field": "nope"})
    assert response.status_code == 422


def test_list_tasks_empty_returns_200_and_empty_list(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_status_no_match_returns_200_and_empty_list(client, created_task):
    response = client.get("/tasks", params={"status": "Done"})
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_filter_by_priority_returns_only_matches(client):
    client.post("/tasks", json={"title": "Low one", "priority": "Low"})
    client.post("/tasks", json={"title": "High one", "priority": "High"})

    response = client.get("/tasks", params={"priority": "High"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["priority"] == "High"
    assert body[0]["title"] == "High one"


def test_get_task_by_id_returns_task(client, created_task):
    task_id = created_task["id"]
    response = client.get(f"/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["id"] == task_id


def test_get_task_by_id_not_found_returns_404_with_detail(client):
    response = client.get("/tasks/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id nonexistent-id not found"


def test_patch_partial_update_keeps_other_fields(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"description": "Updated description"})
    assert response.status_code == 200
    body = response.json()
    assert body["description"] == "Updated description"
    assert body["title"] == created_task["title"]
    assert body["status"] == created_task["status"]
    assert body["priority"] == created_task["priority"]


def test_patch_not_found_returns_404(client):
    response = client.patch("/tasks/nonexistent-id", json={"title": "Should fail"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id nonexistent-id not found"


def test_patch_valid_transition_todo_to_inprogress_returns_200(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    assert response.status_code == 200
    assert response.json()["status"] == "InProgress"


def test_patch_invalid_transition_todo_to_done_returns_422(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "Done"})
    assert response.status_code == 422


def test_patch_same_status_returns_422(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"status": "ToDo"})
    assert response.status_code == 422


def test_delete_existing_returns_204_no_body(client, created_task):
    task_id = created_task["id"]
    response = client.delete(f"/tasks/{task_id}")
    assert response.status_code == 204
    assert response.content == b""


def test_delete_missing_returns_404(client):
    response = client.delete("/tasks/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["detail"] == "Task with id nonexistent-id not found"


def test_tasks_persist_after_module_reload(client):
    response = client.post("/tasks", json={"title": "Persist me"})
    assert response.status_code == 201

    reloaded_storage = importlib.reload(storage)
    tasks = reloaded_storage.get_all_tasks()

    assert len(tasks) == 1
    assert tasks[0].title == "Persist me"

def test_create_task_with_valid_due_date_returns_201(client):
    response = client.post(
        "/tasks",
        json={"title": "Due date task", "due_date": "2026-12-31"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["due_date"] == "2026-12-31"
    assert body["is_overdue"] is False


def test_create_task_with_invalid_due_date_format_returns_422(client):
    response = client.post(
        "/tasks",
        json={"title": "Bad date task", "due_date": "not-a-date"},
    )
    assert response.status_code == 422


def test_create_task_with_past_due_date_is_overdue(client):
    response = client.post(
        "/tasks",
        json={"title": "Past due task", "due_date": "2020-01-01"},
    )
    assert response.status_code == 201
    assert response.json()["is_overdue"] is True


def test_patch_due_date_updates_overdue_status(client, created_task):
    task_id = created_task["id"]
    response = client.patch(f"/tasks/{task_id}", json={"due_date": "2020-01-01"})
    assert response.status_code == 200
    assert response.json()["is_overdue"] is True


def test_done_task_with_past_due_date_is_not_overdue(client):
    create_response = client.post(
        "/tasks",
        json={"title": "Will be done", "due_date": "2020-01-01"},
    )
    task_id = create_response.json()["id"]

    client.patch(f"/tasks/{task_id}", json={"status": "InProgress"})
    done_response = client.patch(f"/tasks/{task_id}", json={"status": "Done"})

    assert done_response.status_code == 200
    assert done_response.json()["is_overdue"] is False


def test_list_tasks_filter_overdue_true_returns_only_overdue(client):
    client.post("/tasks", json={"title": "Overdue one", "due_date": "2020-01-01"})
    client.post("/tasks", json={"title": "Future one", "due_date": "2099-01-01"})

    response = client.get("/tasks", params={"overdue": "true"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Overdue one"


def test_list_tasks_filter_overdue_false_returns_only_non_overdue(client):
    client.post("/tasks", json={"title": "Overdue one", "due_date": "2020-01-01"})
    client.post("/tasks", json={"title": "Future one", "due_date": "2099-01-01"})

    response = client.get("/tasks", params={"overdue": "false"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Future one"

def test_list_tasks_search_matches_title(client):
    client.post("/tasks", json={"title": "Fix login bug", "description": "Users cannot sign in"})
    client.post("/tasks", json={"title": "Update docs", "description": "Refresh README"})

    response = client.get("/tasks", params={"search": "login"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Fix login bug"


def test_list_tasks_search_matches_description_case_insensitive(client):
    client.post("/tasks", json={"title": "Fix login bug", "description": "Users cannot sign in"})
    client.post("/tasks", json={"title": "Update docs", "description": "Refresh README"})

    response = client.get("/tasks", params={"search": "readme"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Update docs"


def test_list_tasks_search_combined_with_status_filter(client):
    client.post("/tasks", json={"title": "Fix login bug", "status": "ToDo"})
    client.post("/tasks", json={"title": "Fix logout bug", "status": "InProgress"})

    response = client.get("/tasks", params={"search": "bug", "status": "ToDo"})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["title"] == "Fix login bug"


def test_list_tasks_search_no_matches_returns_200_and_empty_list(client, created_task):
    response = client.get("/tasks", params={"search": "nonexistentword"})
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_invalid_status_filter_returns_422(client):
    response = client.get("/tasks", params={"status": "Blocked"})
    assert response.status_code == 422