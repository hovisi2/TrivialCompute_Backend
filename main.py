from fastapi import FastAPI, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import mysql.connector
import random
import os
from typing import List, Dict, Any, Optional

class Question(BaseModel):
    category: str
    question: str
    answer: str

class QuestionUpdate(BaseModel):
    category: Optional[str] = None
    question: Optional[str] = None  
    answer: Optional[str] = None

class QuestionResponse(BaseModel):
    id: int
    category: str
    question: str
    answer: str

app = FastAPI(title="Trivial Compute API", version="1.0.0")

def get_db_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            passwd=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "trivial_compute"),
            autocommit=False
        )
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "http://localhost:4200").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"]
)

@app.get("/", tags=["Health"])
def root():
    return {"message": "Trivial Compute API", "version": "1.0.0"}

@app.get("/get_data", response_model=List[QuestionResponse], tags=["Questions"])
def get_all_questions():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, category, question, answer FROM questions")
        records = cursor.fetchall()
        return records
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.post("/add_question", tags=["Questions"])  
def add_question_legacy(category: str = Form(...), question: str = Form(...), answer: str = Form(...)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO questions (category, question, answer) VALUES (%s, %s, %s)",
            (category.strip(), question.strip(), answer.strip())
        )
        conn.commit()
        return {"status": "success", "category": category}
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

# new endpoints
@app.get("/api/questions/categories", response_model=Dict[str, List[str]], tags=["Categories"])
def get_categories():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM questions ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        return {"categories": categories}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.get("/api/questions/{question_id}", response_model=QuestionResponse, tags=["Questions"])
def get_question(question_id: int):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, category, question, answer FROM questions WHERE id = %s", (question_id,))
        record = cursor.fetchone()
        if not record:
            raise HTTPException(status_code=404, detail="Question not found")
        return record
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.get("/api/questions/category/{category}", response_model=List[QuestionResponse], tags=["Questions"])
def get_questions_by_category(category: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, category, question, answer FROM questions WHERE category = %s", (category,))
        records = cursor.fetchall()
        return records
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.get("/api/questions/random/{category}", response_model=QuestionResponse, tags=["Questions"])
def get_random_question(category: str):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, category, question, answer FROM questions WHERE category = %s", (category,))
        records = cursor.fetchall()
        if not records:
            raise HTTPException(status_code=404, detail=f"No questions found for category: {category}")
        return random.choice(records)
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.post("/api/questions", response_model=Dict[str, Any], tags=["Questions"])
def create_question(question: Question):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO questions (category, question, answer) VALUES (%s, %s, %s)",
            (question.category.strip(), question.question.strip(), question.answer.strip())
        )
        conn.commit()
        question_id = cursor.lastrowid
        return {"status": "success", "id": question_id, "message": "Question created successfully"}
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.put("/api/questions/{question_id}", response_model=Dict[str, str], tags=["Questions"])  
def update_question(question_id: int, question_update: QuestionUpdate):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM questions WHERE id = %s", (question_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Question not found")
        
        updates = []
        params = []
        if question_update.category is not None:
            updates.append("category = %s")
            params.append(question_update.category.strip())
        if question_update.question is not None:
            updates.append("question = %s") 
            params.append(question_update.question.strip())
        if question_update.answer is not None:
            updates.append("answer = %s")
            params.append(question_update.answer.strip())
            
        if not updates:
            raise HTTPException(status_code=400, detail="No fields to update")
            
        params.append(question_id)
        query = f"UPDATE questions SET {', '.join(updates)} WHERE id = %s"
        
        cursor.execute(query, params)
        conn.commit()
        return {"status": "success", "message": "Question updated successfully"}
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        conn.close()

@app.delete("/api/questions/{question_id}", response_model=Dict[str, str], tags=["Questions"])
def delete_question(question_id: int):
    """Delete question"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM questions WHERE id = %s", (question_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Question not found")
            
        cursor.execute("DELETE FROM questions WHERE id = %s", (question_id,))
        conn.commit()
        return {"status": "success", "message": "Question deleted successfully"}
    except mysql.connector.Error as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")  
    finally:
        conn.close()

@app.post("/api/admin/authenticate", response_model=Dict[str, Any], tags=["Authentication"])
def authenticate_admin(username: str = Form(...), password: str = Form(...)):
    admin_user = os.getenv("ADMIN_USERNAME", "admin")
    admin_pass = os.getenv("ADMIN_PASSWORD", "password")
    
    if username == admin_user and password == admin_pass:
        return {"status": "success", "message": "Authentication successful", "authenticated": True}
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
