from fastapi import FastAPI, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
from typing import List, Optional
import random

app = FastAPI()

# database connection
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="user",
            passwd="password",
            database="trivial_compute"
        )
        return conn
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# data models
class Question(BaseModel):
    id: Optional[int] = None
    category: str
    question: str
    answer: str

class QuestionUpdate(BaseModel):
    category: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None

class CategoryResponse(BaseModel):
    categories: List[str]

# endpoints
@app.get("/")
def root():
    return {"message": "Trivial Compute API", "version": "1.0"}

# question crud
@app.get("/get_data")
def get_all_questions():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM questions")
        records = cursor.fetchall()
        return records
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.get("/api/questions/categories")
def get_categories():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM questions")
        categories = [row[0] for row in cursor.fetchall()]
        return {"categories": categories}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.get("/api/questions/{question_id}")
def get_question(question_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM questions WHERE id = %s", (question_id,))
        question = cursor.fetchone()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        return question
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.get("/api/questions/category/{category}")
def get_questions_by_category(category: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM questions WHERE category = %s", (category,))
        questions = cursor.fetchall()
        return {"category": category, "questions": questions}
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.get("/api/questions/random/{category}")
def get_random_question(category: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM questions WHERE category = %s", (category,))
        questions = cursor.fetchall()
        if not questions:
            raise HTTPException(status_code=404, detail=f"No questions found for category: {category}")
        
        random_question = random.choice(questions)
        return random_question
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# @app.post("/add_question")
# def add_question(category: str = Form(...), 
#                 question: str = Form(...),
#                 answer: str = Form(...)):
#     conn = get_db_connection()
#     try:
#         cursor = conn.cursor()
#         cursor.execute("INSERT INTO questions (category, question, answer) VALUES (%s, %s, %s)", 
#                       (category, question, answer))
#         conn.commit()
#         question_id = cursor.lastrowid
#         return {"status": "success", "data": {"id": question_id, "category": category}}
#     except Error as e:
#         conn.rollback()
#         raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
#     finally:
#         if conn.is_connected():
#             cursor.close()
#             conn.close()

@app.post("/api/questions")
def create_question(question: Question):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO questions (category, question, answer) VALUES (%s, %s, %s)",
                      (question.category, question.question, question.answer))
        conn.commit()
        question_id = cursor.lastrowid
        return {"status": "success", "id": question_id, "message": "Question created successfully"}
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.put("/api/questions/{question_id}")
def update_question(question_id: int, question_update: QuestionUpdate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM questions WHERE id = %s", (question_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Question not found")
        
        update_fields = []
        values = []
        
        if question_update.category is not None:
            update_fields.append("category = %s")
            values.append(question_update.category)
        if question_update.question is not None:
            update_fields.append("question = %s")
            values.append(question_update.question)
        if question_update.answer is not None:
            update_fields.append("answer = %s")
            values.append(question_update.answer)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        values.append(question_id)
        query = f"UPDATE questions SET {', '.join(update_fields)} WHERE id = %s"
        
        cursor.execute(query, values)
        conn.commit()
        
        return {"status": "success", "message": "Question updated successfully"}
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

@app.delete("/api/questions/{question_id}")
def delete_question(question_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM questions WHERE id = %s", (question_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Question not found")
        
        cursor.execute("DELETE FROM questions WHERE id = %s", (question_id,))
        conn.commit()
        
        return {"status": "success", "message": "Question deleted successfully"}
    except Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()

# check basic api connection
@app.get("/testing")
def test_api():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
