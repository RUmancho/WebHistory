from flask import Flask, render_template, request, jsonify
from DBmanager import *

app = Flask(__name__)

# Путь к файлу с ключом
KEY_FILE_PATH = 'key.txt'


def get_teacher_key():
    """Получение ключа учителя из файла"""
    try:
        with open(KEY_FILE_PATH, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Ошибка при чтении ключа: {str(e)}")
        return None

# Инициализация базы данных при старте
init_db()


@app.route('/')
def index():
    """Главная страница с результатами учеников"""
    return render_template('index.html')


@app.route('/api/verify-key', methods=['POST'])
def verify_key():
    """Проверка ключа учителя и получение результатов"""
    try:
        data = request.get_json()
        
        if not data or 'key' not in data:
            return jsonify({'status': 'error', 'message': 'Ключ не предоставлен'}), 400
        
        teacher_key = get_teacher_key()
        if teacher_key is None:
            return jsonify({'status': 'error', 'message': 'Ошибка сервера при чтении ключа'}), 500
        
        if data['key'].strip() != teacher_key:
            return jsonify({'status': 'error', 'message': 'Неверный ключ доступа'}), 403
        
        # Ключ верный - возвращаем данные учеников по классам
        students_by_class = get_students_by_class()
        
        return jsonify({
            'status': 'success',
            'data': students_by_class
        }), 200
        
    except Exception as e:
        print(f"Ошибка при проверке ключа: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Ошибка сервера'}), 500


@app.route('/test/high-school-student/easy')
def high_school_easy():
    return render_template('HighSchoolStudent/easy.html')

@app.route('/test/high-school-student/medium')
def high_school_medium():
    return render_template('HighSchoolStudent/medium.html')

@app.route('/test/high-school-student/hard')
def high_school_hard():
    return render_template('HighSchoolStudent/hard.html')

@app.route('/test/middle-school-student/easy')
def middle_school_easy():
    return render_template('MiddleSchoolStudent/easy.html')

@app.route('/test/middle-school-student/medium')
def middle_school_medium():
    return render_template('MiddleSchoolStudent/medium.html')

@app.route('/test/middle-school-student/hard')
def middle_school_hard():
    return render_template('MiddleSchoolStudent/hard.html')


@app.route('/api/check-test', methods=['POST'])
def check_test():
    """Проверка, проходил ли пользователь данный тест"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'Нет данных'}), 400
        
        required_fields = ['firstName', 'lastName', 'className', 'testLevel']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Отсутствует поле: {field}'}), 400
        
        result = check_test_exists(
            first_name=data['firstName'],
            last_name=data['lastName'],
            class_name=data['className'],
            level=data['testLevel']
        )
        
        if result['exists']:
            return jsonify({
                'status': 'exists',
                'message': f'Вы уже проходили этот тест! Ваш результат: {result["score"]} из {result["max_score"]}',
                'score': result['score'],
                'max_score': result['max_score'],
                'created_at': result['created_at']
            }), 200
        
        return jsonify({'status': 'ok', 'message': 'Тест можно пройти'}), 200
        
    except Exception as e:
        print(f"Ошибка при проверке теста: {str(e)}")
        return jsonify({'status': 'error', 'message': 'Ошибка сервера'}), 500


@app.route('/api/submit-test', methods=['POST'])
def submit_test():
    """Приём данных теста и сохранение в БД"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'Нет данных'}), 400
        
        required_fields = ['firstName', 'lastName', 'className', 'answers', 'testLevel', 'score']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Отсутствует поле: {field}'}), 400
        
        # Проверяем, не проходил ли уже этот тест
        existing = check_test_exists(
            first_name=data['firstName'],
            last_name=data['lastName'],
            class_name=data['className'],
            level=data['testLevel']
        )
        
        if existing['exists']:
            return jsonify({
                'status': 'exists',
                'message': f'Вы уже проходили этот тест! Ваш результат: {existing["score"]} из {existing["max_score"]}'
            }), 409
        
        # Сохранение данных в БД
        test_id = save_test_result(
            first_name=data['firstName'],
            last_name=data['lastName'],
            class_name=data['className'],
            answers=data['answers'],
            score=data['score'],
            level=data['testLevel'],
            time=data.get('time', 0)
        )
        
        print(f"Тест успешно сохранен! ID: {test_id}")
        print(f"Ученик: {data['firstName']} {data['lastName']}, Класс: {data['className']}")
        print(f"Уровень: {data['testLevel']}, Баллы: {data['score']}")
        
        return jsonify({
            'status': 'success',
            'message': 'Результаты теста успешно сохранены',
            'test_id': test_id
        }), 200
        
    except Exception as e:
        print(f"Ошибка при сохранении результатов теста: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Ошибка сервера при сохранении данных'
        }), 500


@app.route('/api/tests', methods=['GET'])
def get_tests():
    """Получение всех результатов тестов"""
    try:
        tests = get_all_tests()
        return jsonify({
            'status': 'success',
            'data': tests,
            'count': len(tests)
        }), 200
    except Exception as e:
        print(f"Ошибка при получении тестов: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Ошибка сервера при получении данных'
        }), 500


@app.route('/api/tests/<int:test_id>', methods=['GET'])
def get_test(test_id):
    """Получение конкретного результата теста"""
    try:
        test = get_test_by_id(test_id)
        if test:
            return jsonify({
                'status': 'success',
                'data': test
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Тест не найден'
            }), 404
    except Exception as e:
        print(f"Ошибка при получении теста: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Ошибка сервера при получении данных'
        }), 500


@app.route('/api/statistics', methods=['GET'])
def get_stats():
    """Получение статистики по тестам"""
    try:
        stats = get_statistics()
        return jsonify({
            'status': 'success',
            'data': stats
        }), 200
    except Exception as e:
        print(f"Ошибка при получении статистики: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Ошибка сервера при получении статистики'
        }), 500


@app.route('/api/clear-database', methods=['POST'])
def clear_database():
    """Очистка базы данных"""
    try:
        clear_db()
        return jsonify({
            'status': 'success',
            'message': 'База данных успешно очищена'
        }), 200
    except Exception as e:
        print(f"Ошибка при очистке базы данных: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'Ошибка сервера при очистке базы данных'
        }), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
