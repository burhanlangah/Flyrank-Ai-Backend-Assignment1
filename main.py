from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
from pathlib import Path

app = FastAPI()
DB_PATH = Path("tasks.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    cursor.execute("SELECT COUNT(*) FROM tasks")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Learn FastAPI", 0))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Build a database", 0))
        cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Deploy to production", 0))
    conn.commit()
    conn.close()

@app.on_event("startup")
async def startup():
    init_db()


class TaskCreate(BaseModel):
    title: str = ""


class TaskUpdate(BaseModel):
    title: str = ""
    done: bool = False


@app.get("/tasks", summary="API info")
def read_root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health", summary="Health check")
def health_check():
    return {"status": "ok"}


@app.get("/tasks", summary="List all tasks")
def get_tasks():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks")
    tasks = [{"id": row[0], "title": row[1], "done": row[2]} for row in cursor.fetchall()]
    conn.close()
    return tasks


@app.get("/tasks/{id}", summary="Get a single task by id")
def get_task(id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, done FROM tasks WHERE id = ?", (id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    return {"id": row[0], "title": row[1], "done": row[2]}


@app.post("/tasks", status_code=201, summary="Create a new task")
def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", (task.title, False))
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return {"id": task_id, "title": task.title, "done": False}


@app.put("/tasks/{id}", summary="Update a task's title and/or done status")
def update_task(id: int, update: TaskUpdate):
    if not update.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    
    cursor.execute("UPDATE tasks SET title = ?, done = ? WHERE id = ?", (update.title, update.done, id))
    conn.commit()
    conn.close()
    return {"id": id, "title": update.title, "done": update.done}


@app.delete("/tasks/{id}", status_code=204, summary="Delete a task")
def delete_task(id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks WHERE id = ?", (id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail=f"Task {id} not found")
    
    cursor.execute("DELETE FROM tasks WHERE id = ?", (id,))
    conn.commit()
    conn.close()