from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
app = Flask(__name__)

#------------------------------------DATABASE MANAGEMENT---------------------------------------------------------------------

app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///sampledb.sqlite3"

#unnayan

db = SQLAlchemy(app)

app.app_context().push()

class Student(db.Model):
    student_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    roll_number = db.Column(db.String(), unique = True, nullable = False)
    first_name = db.Column(db.String(), nullable = False)
    last_name = db.Column(db.String())
    courses = db.relationship("Course", backref = "studiesby", secondary = "enrollments")

class Course(db.Model):
    course_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    course_code = db.Column(db.String(), unique = True, nullable = False)
    course_name = db.Column(db.String(), nullable = False)
    course_description = db.Column(db.String())

class Enrollments(db.Model):
    enrollment_id = db.Column(db.Integer, primary_key = True, autoincrement= True)
    estudent_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable = False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable = False)

#-----------------------------------Routes-------------------------------------------------------------------------------------

@app.route('/')
def home():
    students = Student.query.all()
    return render_template("index.html", students = students)

@app.route('/student/create', methods = ['GET', 'POST'])
def create():
    if request.method == "POST":
        roll = request.form.get("roll")
        A = db.session.query(Student).filter(Student.roll_number == roll).first()
        if(A):
            return render_template("exist.html")
        else:
            f_name = request.form.get("f_name")
            l_name = request.form.get("l_name")
            checked_courses = request.form.getlist("courses")
            new_student = Student(roll_number = roll, first_name = f_name, last_name = l_name)
            db.session.add(new_student)
            db.session.commit()
            for c in checked_courses:
                enroll = Enrollments(estudent_id = new_student.student_id, ecourse_id = int(c[7]))
                db.session.add(enroll)
            db.session.commit()
            return redirect('/')
    return render_template("create.html")

@app.route('/student/<int:id>')
def student(id):
    student = Student.query.get(id)
    course = student.courses
    return render_template("enroll.html", student = student, course = course)

@app.route('/student/<int:id>/update', methods = ["GET", "POST"])
def update(id):
    stud = Student.query.get(id)
    if request.method == "POST":
        fname = request.form.get("f_name")
        lname = request.form.get("l_name")
        checked_courses = request.form.getlist("courses")
        A = db.session.query(Enrollments).filter(Enrollments.estudent_id == id).first()
        while(A):
            db.session.delete(A)
            db.session.commit()
            A = db.session.query(Enrollments).filter(Enrollments.estudent_id == id).first()
        stud.first_name = fname
        stud.last_name= lname
        db.session.commit()
        for c in checked_courses:
            enroll = Enrollments(estudent_id = stud.student_id, ecourse_id = int(c[7]))
            db.session.add(enroll)
        db.session.commit()
        return redirect('/')
    return render_template("update.html", stud = stud)

@app.route('/student/<int:id>/delete')
def delete(id):
    stud = Student.query.get(id)
    db.session.delete(stud)
    db.session.commit()
    enroll = db.session.query(Enrollments).filter(Enrollments.estudent_id == id).first()
    while(enroll):
        db.session.delete(enroll)
        db.session.commit()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug = True)
