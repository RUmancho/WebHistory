import sqlite3
import json

DATABASE_PATH = 'database.db'

def init_db():
    """Инициализация базы данных"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Test (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            answers TEXT NOT NULL,
            score INTEGER NOT NULL,
            level TEXT NOT NULL,
            time INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        print("База данных успешно инициализирована")
        
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {str(e)}")


def save_test_result(first_name, last_name, class_name, answers, score, level, time=0):
    """Сохранение результатов теста в базу данных"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Преобразование списка ответов в JSON строку
        answers_json = json.dumps(answers, ensure_ascii=False)
        
        cursor.execute('''
        INSERT INTO Test (first_name, last_name, class_name, answers, score, level, time)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, class_name, answers_json, score, level, time))
        
        test_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return test_id
        
    except Exception as e:
        print(f"Ошибка при сохранении результатов теста в БД: {str(e)}")
        raise


def get_all_tests():
    """Получение всех результатов тестов"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM Test ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        tests = []
        for row in rows:
            tests.append({
                'id': row['id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'class_name': row['class_name'],
                'answers': json.loads(row['answers']),
                'score': row['score'],
                'level': row['level'],
                'time': row['time'],
                'created_at': row['created_at']
            })
        
        conn.close()
        return tests
        
    except Exception as e:
        print(f"Ошибка при получении результатов тестов: {str(e)}")
        return []


def get_test_by_id(test_id):
    """Получение результата теста по ID"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM Test WHERE id = ?', (test_id,))
        row = cursor.fetchone()
        
        if row:
            test = {
                'id': row['id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'class_name': row['class_name'],
                'answers': json.loads(row['answers']),
                'score': row['score'],
                'level': row['level'],
                'time': row['time'],
                'created_at': row['created_at']
            }
            conn.close()
            return test
        
        conn.close()
        return None
        
    except Exception as e:
        print(f"Ошибка при получении результата теста: {str(e)}")
        return None
