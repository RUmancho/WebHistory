import sqlite3

def init_db():
    """Инициализация базы данных"""
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Test (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        class_name TEXT,
        answers TEXT,
        score INTEGER,
        level TEXT,
        time INTEGER
    )
    ''')
    
    conn.commit()
    conn.close()
