import os

from flask import Flask
from flask import make_response

from flask_sqlalchemy import SQLAlchemy

from flask_restful import Resource
from flask_restful import Api
from flask_restful import reqparse
from flask_restful import fields,marshal_with

from werkzeug.exceptions import HTTPException

#
# Initialization
#
DIR=os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(DIR,'api_database.sqlite3')
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///api_database.sqlite3'
db=SQLAlchemy()
db.init_app(app)
api=Api(app)
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
    __tablename__='enrollment'
    enrollment_id=db.Column(db.Integer,primary_key=True,autoincrement=True)
    student_id=db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable=False)
    course_id=db.Column(db.Integer, db.ForeignKey('course.course_id'), nullable=False)

class HTTPServerError(HTTPException):
    def __init__(self,status_code,error_message=''):
        self.response=make_response(error_message,status_code)
class HTTPBadRequestError(HTTPException):
    def __init__(self,status_code,error_code,message):
        message='{"error_code":%s,"error_message":%s}'%(error_code,message)
        self.response=make_response(message,status_code)


class CourseAPI(Resource):
    course_fields={
        "course_id":fields.Integer,
        "course_name":fields.String,
        "course_code":fields.String,
        "course_description":fields.String
    }
    req=reqparse.RequestParser()
    req.add_argument('course_name')
    req.add_argument('course_code')
    req.add_argument('course_description')

    @marshal_with(course_fields)
    def get(self,course_id):
        try:
            course=db.session.query(Course).filter(Course.course_id==course_id).first()
        except:
            raise HTTPServerError(status_code=500)
        if course:
            return course,200
        else:
            raise HTTPServerError(status_code=404)
    @marshal_with(course_fields)
    def put(self,course_id):
        args=self.req.parse_args()
        course_name=args.get('course_name',None)
        course_code=args.get('course_code',None)
        course_description=args.get('course_description',None)
        if not course_name:
            raise HTTPBadRequestError(status_code=400,error_code='COURSE001',message="Course Name is required")
        if not course_code:
            raise HTTPBadRequestError(status_code=400,error_code="COURSE002",message="Course Code is required")
        try:
            course=db.session.query(Course).filter(Course.course_id==course_id).first()
        except:
            raise HTTPServerError(status_code=500)
        if course:
            try:
                course.course_name=course_name
                course.course_code=course_code
                course.course_description=course_description
                db.session.add(course)
                db.session.commit()
                return course,200
            except:
                db.session.rollback()
                raise HTTPServerError(status_code=500)
        else:
            raise HTTPServerError(status_code=404)
    def delete(self,course_id):
        try:
            course=db.session.query(Course).filter(Course.course_id==course_id).first()
        except:
            raise HTTPServerError(status_code=500)
        if course:
            try:
                db.session.delete(course)
                db.session.commit()
                return None,200
            except:
                db.session.rollback()
                raise HTTPServerError(status_code=500)
        else:
            raise HTTPServerError(status_code=404)
    @marshal_with(course_fields)
    def post(self):
        args=self.req.parse_args()
        course_name=args.get('course_name',None)
        course_code=args.get('course_code',None)
        course_description=args.get('course_description',None)
        if not course_name:
            raise HTTPBadRequestError(status_code=400,error_code='COURSE001',message="Course Name is required")
        if not course_code:
            raise HTTPBadRequestError(status_code=400,error_code="COURSE002",message="Course Code is required")
        try:
            course=db.session.query(Course).filter(Course.course_code==course_code).first()
        except:
            raise HTTPServerError(status_code=500)
        if course:
            raise HTTPServerError(status_code=409)
        else:
            course=Course(course_name=course_name,course_code=course_code,course_description=course_description)
            db.session.add(course)
            db.session.commit()
            return course,201
api.add_resource(CourseAPI,"/api/course/<int:course_id>","/api/course")
        
class StudentAPI(Resource):
    student_fields={
        "student_id":fields.Integer,
        "first_name": fields.String,
        "last_name": fields.String,
        "roll_number":fields.String
    }
    req=reqparse.RequestParser()
    req.add_argument('first_name')
    req.add_argument('last_name')
    req.add_argument('roll_number')
    @marshal_with(student_fields)
    def get(self,student_id):
        try:
            student=db.session.query(Student).filter(Student.student_id==student_id).first()
        except:
            raise HTTPServerError(status_code=500)
        print(student)
        if student:
            return student,200
        else:
            raise HTTPServerError(status_code=404)
    @marshal_with(student_fields)
    def put(self,student_id):
        args=self.req.parse_args()
        first_name=args.get('first_name',None)
        last_name=args.get('last_name',None)
        roll_number=args.get('roll_number',None)
        if not roll_number:
            raise HTTPBadRequestError(status_code=400,error_code="STUDENT001",message="Roll Number required")
        if not first_name:
            raise HTTPBadRequestError(status_code=400,error_code="STUDENT002",message="First Name is required")
        try:
            student=db.session.query(Student).filter(Student.student_id==student_id).first()
        except:
            raise HTTPServerError(status_code=500)
        if student:
            try:
                student.roll_number=roll_number
                student.first_name=first_name
                student.last_name=last_name
                db.session.add(student)
                db.session.commit()
                return student,200
            except:
                db.session.rollback()
                raise HTTPServerError(status_code=500)
        else:
            raise HTTPServerError(status_code=404)
    def delete(self,student_id):
        try:
            student=db.session.query(Student).filter(Student.student_id==student_id).first()
        except:
            raise HTTPServerError(status_code=500)
        if student:
            db.session.delete(student)
            db.session.commit()
            return None,200
            # except:
            #     db.session.rollback()
            #     raise HTTPServerError(status_code=500)
        else:
            raise HTTPServerError(status_code=404)
    @marshal_with(student_fields)
    def post(self):
        args=self.req.parse_args()
        first_name=args.get('first_name',None)
        last_name=args.get('last_name',None)
        roll_number=args.get('roll_number',None)
        if not roll_number:
            raise HTTPBadRequestError(status_code=400,error_code="STUDENT001",message="Roll Number required")
        if not first_name:
            raise HTTPBadRequestError(status_code=400,error_code="STUDENT002",message="First Name is required")
        try:
            student=db.session.query(Student).filter(Student.roll_number==roll_number).first()
        except:
            raise HTTPServerError(status_code=500)
        if student:
            raise HTTPServerError(status_code=409)
        else:
            student=Student(first_name=first_name,last_name=last_name,roll_number=roll_number)
            db.session.add(student)
            db.session.commit()
            return student,201
api.add_resource(StudentAPI,"/api/student/<int:student_id>","/api/student")

class EnrollmentAPI(Resource):
    enrollment_fields={
        "enrollment_id":fields.Integer,
        "student_id":fields.Integer,
        "course_id":fields.Integer
    }
    req=reqparse.RequestParser()
    req.add_argument('course_id')
    @marshal_with(enrollment_fields)
    def get(self,student_id):
        try:
            student=db.session.query(Student).filter(Student.student_id==student_id).first()
        except:
            raise HTTPServerError(status_code=500)
        if not student:
            raise HTTPBadRequestError(status_code=400,error_code="ENROLLMENT002",message="Student does not exist")
        try:
            enrollment=db.session.query(Enrollments).filter(Enrollments.student_id==student_id).all()
        except:
            raise HTTPServerError(status_code=500)
        if enrollment:
            return enrollment,200
        else:
            raise HTTPServerError(status_code=404)
    @marshal_with(enrollment_fields)
    def post(self,student_id):
        args=self.req.parse_args()
        course_id=args.get("course_id",None)
        print(course_id)
        if not course_id:
            raise HTTPBadRequestError(status_code=400,error_code="ENROLLMENT001",message="Course does not exist")
        try:
            student=db.session.query(Student).filter(Student.student_id==student_id).first()
            course=db.session.query(Course).filter(Course.course_id==course_id).first()
        except:
            raise HTTPServerError(status_code=500)
        if not student:
            raise HTTPServerError(status_code=404)
        if not course:
            raise HTTPBadRequestError(status_code=400,error_code="ENROLLMENT001",message="Course does not exist")
        try:
            enrollment=Enrollments(student_id=student_id,course_id=course_id)
            db.session.add(enrollment)
            db.session.commit()
            return enrollment,201
        except:
            db.session.rollback()
            return HTTPServerError(status_code=500)
    def delete(self,student_id,course_id):
        try:
            student=db.session.query(Student).filter(Student.student_id==student_id).first()
            course=db.session.query(Course).filter(Course.course_id==course_id)
        except:
            raise HTTPServerError(status_code=500)
        if not student:
            raise HTTPBadRequestError(status_code=400,error_code="ENROLLMENT002",message="Student does not exist")
        if not course:
            raise HTTPBadRequestError(status_code=400,error_code="ENROLLMENT001",message="Course does not exist")
        try:
            enrollment=db.session.query(Enrollments).filter((Enrollments.course_id==course_id)&(Enrollments.student_id==student_id)).first()
        except:
            raise HTTPServerError(status_code=500)
        if enrollment:
            db.session.delete(enrollment)
            db.session.commit()
            return None,200
        else:
            raise HTTPServerError(status_code=404)
api.add_resource(EnrollmentAPI,"/api/student/<int:student_id>/course","/api/student/<int:student_id>/course/<int:course_id>")

if __name__=="__main__":
    app.run()
