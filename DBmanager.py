import sqlite3
import json
from datetime import datetime

DATABASE_PATH = 'database.db'


def get_connection():
    """Получение соединения с базой данных"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {str(e)}")
        raise


def init_db():
    """Инициализация базы данных"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Test (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            class_name TEXT NOT NULL,
            answers TEXT NOT NULL,
            score INTEGER NOT NULL,
            max_score INTEGER NOT NULL,
            level TEXT NOT NULL,
            time_spent INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
        conn.close()
        print("База данных успешно инициализирована")
        
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {str(e)}")
        raise


def clear_db():
    """Полная очистка базы данных"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM Test')
        cursor.execute("DELETE FROM sqlite_sequence WHERE name = 'Test'")
        
        conn.commit()
        conn.close()
        print("База данных успешно очищена")
        
    except Exception as e:
        print(f"Ошибка при очистке базы данных: {str(e)}")
        raise


def drop_all_tables():
    """Удаление всех таблиц (для пересоздания схемы)"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DROP TABLE IF EXISTS Answers')
        cursor.execute('DROP TABLE IF EXISTS TestResults')
        cursor.execute('DROP TABLE IF EXISTS Users')
        cursor.execute('DROP TABLE IF EXISTS Test')
        
        conn.commit()
        conn.close()
        print("Все таблицы удалены")
        
    except Exception as e:
        print(f"Ошибка при удалении таблиц: {str(e)}")
        raise


def save_test_result(first_name, last_name, class_name, answers, score, level, time=0):
    """Сохранение результатов теста в базу данных
    
    answers - список ответов в формате:
    [
        {"question": 1, "answer": "c", "correct_answer": "c", "correct": true},
        {"question": 2, "answer": "a", "correct_answer": "b", "correct": false},
        ...
    ]
    """
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # Преобразование списка ответов в JSON строку
        if isinstance(answers, list):
            answers_json = json.dumps(answers, ensure_ascii=False)
        else:
            answers_json = answers
        
        max_score = len(json.loads(answers_json) if isinstance(answers_json, str) else answers)
        
        cursor.execute('''
        INSERT INTO Test (first_name, last_name, class_name, answers, score, max_score, level, time_spent)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (first_name, last_name, class_name, answers_json, score, max_score, level, time))
        
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
        conn = get_connection()
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
                'max_score': row['max_score'],
                'level': row['level'],
                'time_spent': row['time_spent'],
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
        conn = get_connection()
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
                'max_score': row['max_score'],
                'level': row['level'],
                'time_spent': row['time_spent'],
                'created_at': row['created_at']
            }
            conn.close()
            return test
        
        conn.close()
        return None
        
    except Exception as e:
        print(f"Ошибка при получении результата теста: {str(e)}")
        return None


def get_statistics():
    """Получение общей статистики по тестам"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        stats = {}
        
        # Общее количество тестов
        cursor.execute('SELECT COUNT(*) as count FROM Test')
        stats['total_tests'] = cursor.fetchone()['count']
        
        # Средний балл в процентах
        cursor.execute('SELECT AVG(score * 1.0 / max_score * 100) as avg FROM Test')
        result = cursor.fetchone()['avg']
        stats['average_score_percent'] = round(result, 2) if result else 0
        
        # Статистика по уровням
        cursor.execute('''
            SELECT level, COUNT(*) as count, 
                   AVG(score * 1.0 / max_score * 100) as avg_score
            FROM Test
            GROUP BY level
        ''')
        stats['by_level'] = [dict(row) for row in cursor.fetchall()]
        
        conn.close()
        return stats
        
    except Exception as e:
        print(f"Ошибка при получении статистики: {str(e)}")
        return {}
