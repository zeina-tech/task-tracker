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