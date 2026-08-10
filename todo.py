from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3


class TaskCreate(BaseModel):
    title: str


app = FastAPI()


def initialize_database():
    connection = sqlite3.connect("tasks.db")

    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL
        )
    """)

    count = connection.execute(
        "SELECT COUNT(*) FROM tasks"
    ).fetchone()[0]

    if count == 0:
        connection.executemany(
            "INSERT INTO tasks (id, title, done) VALUES (?, ?, ?)",
            [
                (1, "Learn Python", False),
                (2, "Build API", False),
                (3, "Submit assignment", True)
            ]
        )

    connection.commit()
    connection.close()


initialize_database()


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None

tasks = [
    {"id": 1, "title": "Learn Python", "done": False},
    {"id": 2, "title": "Build API", "done": False},
    {"id": 3, "title": "Submit assignment", "done": True}
]


@app.get("/", description="Get information about the Task API")
def home():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", description="Check if the API is running")
def health():
    return {
        "status": "ok"
    }


@app.get("/tasks", description="Get all tasks")
def get_tasks():
    return tasks


@app.get("/tasks/{task_id}", description="Get a task by ID")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )
@app.post("/tasks", status_code=201, description="Create a new task")
def create_task(task: TaskCreate):
    if task.title.strip() == "":
        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty"
        )

    new_task = {
        "id": len(tasks) + 1,
        "title": task.title,
        "done": False
    }

    tasks.append(new_task)

    return new_task
@app.put("/tasks/{task_id}", description="Update an existing task")
def update_task(task_id: int, updated_task: TaskUpdate):
    if updated_task.title is None and updated_task.done is None:
        raise HTTPException(
            status_code=400,
            detail="Provide title or done"
        )

    for task in tasks:
        if task["id"] == task_id:

            if updated_task.title is not None:
                if updated_task.title.strip() == "":
                    raise HTTPException(
                        status_code=400,
                        detail="Title cannot be empty"
                    )
                task["title"] = updated_task.title

            if updated_task.done is not None:
                task["done"] = updated_task.done

            return task

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )
@app.delete("/tasks/{task_id}", status_code=204, description="Delete a task")
def delete_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            tasks.remove(task)
            return

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )