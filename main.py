from fastapi import FastAPI
import mysql.connector
from fastapi.middleware.cors import CORSMiddleware

app=FastAPI()

conn=mysql.connector.connect(
        host="localhost",
        user="user",
        passwd="password",
        database="test"
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
    cursor.execute("select * from Data") 
    records=cursor.fetchall()
    return records
