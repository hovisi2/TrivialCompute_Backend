from fastapi import FastAPI,Form
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()

conn=mysql.connector.connect(
        host="localhost",
        user="user",
        passwd="password",
        database="trivial_compute"
)

app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
)        

@app.get("/")
def root():
    return {"message":"Hello World"}

@app.get("/get_data")
def get_tasks():
    cursor=conn.cursor(dictionary=True)
    cursor.execute("select * from questions") 
    records=cursor.fetchall()
    return records

@app.post("/add_question")
def add_question( category:str=Form(...), 
                 question:str=Form(...),
                 answer:str=Form(...)):
    cursor=conn.cursor()
    cursor.execute("insert into questions (category, question, answer) values (%s,%s,%s)", (category, question, answer))
    conn.commit()
    return {"status": "success", "data": category}
