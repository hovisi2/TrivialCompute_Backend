import mysql.connector
import os
from mysql.connector import Error

def setup_database():
    connection = None
    cursor = None
    
    try:
        print("Attempting to connect to MySQL...")
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', '')
        )
        
        if connection.is_connected():
            print("Connected to MySQL successfully")
            cursor = connection.cursor()
            
            print("Reading schema file...")
            with open('schema.sql', 'r') as file:
                sql_script = file.read()
            
            statements = sql_script.split(';')
            
            print("Executing SQL statements...")
            for statement in statements:
                statement = statement.strip()
                if statement: 
                    cursor.execute(statement)
            
            connection.commit()
            print("Database setup completed")
            
            cursor.execute("USE trivial_compute")
            cursor.execute("SELECT COUNT(*) FROM questions")
            count = cursor.fetchone()[0]
            print(f"{count} sample questions inserted")
            
    except Error as e:
        print(f"Database setup failed: {e}")
        return False
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
    
    return True

def test_connection():
    connection = None
    cursor = None
    
    try:
        connection = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database='trivial_compute'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM questions")
            count = cursor.fetchone()[0]
            print(f"Database connection successful, {count} questions available")
            return True
            
    except Error as e:
        print(f"Database connection failed: {e}")
        return False
        
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

if __name__ == "__main__":
    print("Setting up Trivial Compute database...")
    print("=" * 50)
    
    success = setup_database()
    
    if success:
        print("\nTesting database connection...")
        test_connection()
        print("\nSetup complete, can now start the FastAPI server.")
    else:
        print("\nSetup failed. Check your MySQL config.")