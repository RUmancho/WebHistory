from flask import Flask, render_template, request, jsonify
from DBmanager import init_db, save_test_result

app = Flask(__name__)

# Инициализация базы данных при старте приложения
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


if __name__ == '__main__':
    app.run(debug=True, port=5000)