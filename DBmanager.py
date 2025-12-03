import sqlite3
import json

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
        
        # Удаляем старые лишние таблицы если есть
        cursor.execute('DROP TABLE IF EXISTS Answers')
        cursor.execute('DROP TABLE IF EXISTS TestResults')
        cursor.execute('DROP TABLE IF EXISTS Users')
        
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


def check_test_exists(first_name, last_name, class_name, level):
    """Проверка, проходил ли пользователь данный тест"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, score, max_score, created_at FROM Test 
            WHERE LOWER(first_name) = LOWER(?) 
            AND LOWER(last_name) = LOWER(?) 
            AND LOWER(class_name) = LOWER(?) 
            AND level = ?
        ''', (first_name.strip(), last_name.strip(), class_name.strip(), level))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return {
                'exists': True,
                'test_id': row['id'],
                'score': row['score'],
                'max_score': row['max_score'],
                'created_at': row['created_at']
            }
        return {'exists': False}
        
    except Exception as e:
        print(f"Ошибка при проверке существования теста: {str(e)}")
        return {'exists': False}


def save_test_result(first_name, last_name, class_name, answers, score, level, time=0):
    """Сохранение результатов теста в базу данных"""
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
        ''', (first_name.strip(), last_name.strip(), class_name.strip(), answers_json, score, max_score, level, time))
        
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
        
        cursor.execute('SELECT COUNT(*) as count FROM Test')
        stats['total_tests'] = cursor.fetchone()['count']
        
        cursor.execute('SELECT AVG(score * 1.0 / max_score * 100) as avg FROM Test')
        result = cursor.fetchone()['avg']
        stats['average_score_percent'] = round(result, 2) if result else 0
        
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


def get_students_by_class():
    """Получение всех учеников, сгруппированных по классам"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, class_name, first_name, last_name, answers, score, max_score, level, created_at
            FROM Test
            ORDER BY class_name, last_name, first_name
        ''')
        
        rows = cursor.fetchall()
        conn.close()
        
        # Группировка по классам
        classes = {}
        for row in rows:
            class_name = row['class_name']
            if class_name not in classes:
                classes[class_name] = []
            
            classes[class_name].append({
                'id': row['id'],
                'first_name': row['first_name'],
                'last_name': row['last_name'],
                'answers': json.loads(row['answers']),
                'score': row['score'],
                'max_score': row['max_score'],
                'level': row['level'],
                'created_at': row['created_at']
            })
        
        return classes
        
    except Exception as e:
        print(f"Ошибка при получении учеников по классам: {str(e)}")
        return {}