from flask import Flask, render_template

app = Flask(__name__)


@app.route('/test/high-school-student/first')
def high_school_first():
    return render_template('high-school-student/first.html')

@app.route('/test/high-school-student/second')
def high_school_second():
    return render_template('high-school-student/second.html')

@app.route('/test/high-school-student/third')
def high_school_third():
    return render_template('high-school-student/third.html')

@app.route('/test/middle-school-student/first')
def middle_school_first():
    return render_template('middle-school-student/first.html')

@app.route('/test/middle-school-student/second')
def middle_school_second():
    return render_template('middle-school-student/second.html')

@app.route('/test/middle-school-student/third')
def middle_school_third():
    return render_template('middle-school-student/third.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)