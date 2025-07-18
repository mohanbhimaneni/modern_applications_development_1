import os
from flask import Flask
from flask import redirect
from flask import render_template
from flask import request
from flask_sqlalchemy import SQLAlchemy

# DIR=os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///database.sqlite3'
db = SQLAlchemy()
db.init_app(app)
app.app_context().push()

#
# Models
#
class Student(db.Model):
    __tablename__='student'
    student_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    roll_number=db.Column(db.String, unique=True)
    first_name=db.Column(db.String, nullable=False)
    last_name=db.Column(db.String)

class Course(db.Model):
    __tablename__='course'
    course_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    course_code=db.Column(db.String,unique=True,nullable=False)
    course_name=db.Column(db.String,nullable=False)
    course_description=db.Column(db.String)

class Enrollments(db.Model):
    __tablename__='enrollments'
    enrollment_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    estudent_id=db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    ecourse_id=db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)

#
# Routes
#
@app.route('/',methods=['GET'])
def home():
    students=Student.query.all()
    return render_template('home.html',students=students,len=len)

@app.route('/student/create',methods=['GET'])
def create_student():
    return render_template('create_student.html')

@app.route('/student/create',methods=['POST'])
def store_student():
    db.session.begin()
    roll_number=request.form.get('roll')
    exists = bool(Student.query.filter_by(roll_number=roll_number).first())
    if exists:
        return render_template('student_exists.html')
    first_name=request.form.get('f_name')
    last_name=request.form.get('l_name')
    courses=list(map(lambda x: int(x[-1]),request.form.getlist('courses')))
    student=Student(roll_number=roll_number,first_name=first_name,last_name=last_name)
    db.session.add(student)
    db.session.commit()
    for course in courses:
        print(course)
        enrollment=Enrollments(estudent_id=student.student_id,ecourse_id=course)
        db.session.add(enrollment)
    db.session.commit()
    return redirect('/')

@app.route('/student/<int:student_id>/update',methods=['GET'])
def update_student(student_id):
    student=Student.query.filter_by(student_id=student_id).first()
    enrollments=Enrollments.query.filter_by(estudent_id=student_id).all()
    enrollments=list(map(lambda x: x.ecourse_id, enrollments))
    return render_template('update_student.html',student=student,enrollments=enrollments)

@app.route('/student/<int:student_id>/update',methods=['POST'])
def store_updated_student(student_id):
    db.session.begin()
    student=Student.query.filter_by(student_id=student_id).first()
    students_enrollments=Enrollments.query.filter_by(estudent_id=student_id).all()
    for enrollment in students_enrollments:
        db.session.delete(enrollment)
    db.session.commit()
    f_name=request.form.get('f_name')
    l_name=request.form.get('l_name')
    if student.first_name!=f_name:
        student.first_name=f_name
    if student.last_name!=l_name:
        student.last_name=l_name
    db.session.commit()
    courses_list=list(map(lambda x: int(x[-1]),request.form.getlist('courses')))
    for course in courses_list:
        print(course)
        enrollment=Enrollments(estudent_id=student.student_id,ecourse_id=course)
        db.session.add(enrollment)
    db.session.commit()
    return redirect('/')

@app.route('/student/<int:student_id>/delete',methods=['GET'])
def delete_student(student_id):
    db.session.begin()
    student=Student.query.filter_by(student_id=student_id).first()
    enrollments=Enrollments.query.filter_by(estudent_id=student_id).all()
    for enrollment in enrollments:
        db.session.delete(enrollment)
    db.session.commit()
    db.session.delete(student)
    db.session.commit()
    return redirect('/')

@app.route('/student/<int:student_id>',methods=['GET'])
def show_student_details(student_id):
    student=Student.query.filter_by(student_id=student_id).first()
    enrollments=Enrollments.query.filter_by(estudent_id=student_id).all()
    courses=[]
    for enrollment in enrollments:
        courses.append(Course.query.filter_by(course_id=enrollment.ecourse_id).first())
    return render_template('student_details.html',student=student,courses=courses,range=range,len=len)

if __name__=='__main__':
    app.run()