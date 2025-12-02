from flask import Flask, render_template, request, jsonify
from DBmanager import init_db, drop_all_tables, clear_db, save_test_result, get_all_tests, get_test_by_id, get_statistics

app = Flask(__name__)

# Пересоздание базы данных с чистой схемой при старте
drop_all_tables()
init_db()


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


@app.route('/api/submit-test', methods=['POST'])
def submit_test():
    """Приём данных теста и сохранение в БД"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'status': 'error', 'message': 'Нет данных'}), 400
        
        # Проверка обязательных полей
        required_fields = ['firstName', 'lastName', 'className', 'answers', 'testLevel', 'score']
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Отсутствует поле: {field}'}), 400
        
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
        print(f"Ответы: {data['answers']}")
        
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
