from flask import Flask, render_template, request, jsonify
import json

app = Flask(__name__)

@app.route('/')
def index():
    """Главная страница с тестом"""
    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True)