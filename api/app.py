import os

import psycopg
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr


app = FastAPI(
    title="TaskFlow API",
    version="1.0.0",
)


class TaskCreate(BaseModel):
    name: str
    email: EmailStr
    title: str
    description: str


def get_connection():
    return psycopg.connect(
        host=os.getenv("POSTGRES_HOST", "postgres"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
        dbname=os.getenv("POSTGRES_DB", "taskflow"),
        user=os.getenv("POSTGRES_USER", "taskflow"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def init_database():
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(150) NOT NULL,
                    email VARCHAR(255) NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    description TEXT NOT NULL
                )
                """
            )

        connection.commit()


@app.on_event("startup")
def startup():
    init_database()


@app.get("/")
def root():
    return {
        "message": "TaskFlow API fonctionne"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/api/tasks")
def get_tasks():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        id,
                        name,
                        email,
                        title,
                        description
                    FROM tasks
                    ORDER BY id DESC
                    """
                )

                rows = cursor.fetchall()

        return [
            {
                "id": row[0],
                "name": row[1],
                "email": row[2],
                "title": row[3],
                "description": row[4],
            }
            for row in rows
        ]

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@app.post("/api/tasks", status_code=201)
def create_task(task: TaskCreate):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO tasks (
                        name,
                        email,
                        title,
                        description
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        task.name,
                        task.email,
                        task.title,
                        task.description,
                    ),
                )

                task_id = cursor.fetchone()[0]

            connection.commit()

        return {
            "id": task_id,
            "name": task.name,
            "email": task.email,
            "title": task.title,
            "description": task.description,
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )