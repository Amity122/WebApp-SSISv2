from . import students
import os
from flask import render_template, request, flash, redirect, url_for, jsonify
from WebApp.models import Students, Courses, Colleges
from .forms import add_student_form,delete_student_form,update_student_form
from WebApp import mysql
import cloudinary
from config import CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET, CLOUDINARY_CLOUD_NAME
import cloudinary.uploader
import cloudinary.api

cloudinary.config(
    CLOUDINARY_CLOUD_NAME=CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY=CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET=CLOUDINARY_API_SECRET
)

ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']

@students.route('/add-student', methods =['GET','POST'])
def add_student():
    form = add_student_form()
    new_student = None
    all_students = Students.query_filter(all=True)
    profile_photo = form.profile_pic.data
    form.college.choices = [(college.college_code, college.college_name) for college in Colleges.query_filter(all=True)]
    form.course.choices = [(course.course_code, course.course_name) for course in Courses.query_filter(all=True)]
    if request.method == 'POST':
        try:
            if profile_photo:
                if profile_photo.filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS:
                    upload_result = cloudinary.uploader.upload(profile_photo, folder="SIS")
                    new_student = Students(first_name=form.first_name.data, last_name=form.last_name.data, id=form.id_number.data, course=form.course.data, college=form.college.data, gender=form.gender.data, year_lvl=form.year_level.data, profile_pic=upload_result['secure_url'])
            else:
                new_student = Students(first_name=form.first_name.data, last_name=form.last_name.data, id=form.id_number.data, course=form.course.data, college=form.college.data, gender=form.gender.data, year_lvl=form.year_level.data)
            new_student.add()
            mysql.connection.commit()
            flash('Student added successfully!')
            return redirect(url_for('students.add_student'))
        except:
            flash('Error! Student already exists or ID Must be in YYYY-NNNN format e.g: 2020-0909')
            return redirect(url_for('students.add_student'))
    return render_template('students/add-students.html', form=form, all_students=all_students)

@students.route('/delete-student', methods =['GET','POST'])
def delete_student():
    form = delete_student_form()
    all_students = Students.query_filter(all=True)
    if request.method == 'POST':
        exists = Students.query_get(
            id=form.student_to_del.data)
        if exists.id:
            try:
                Students.delete(exists.id)
                mysql.connection.commit()
                flash("Student Removed Successfully!")
                return redirect(url_for('students.delete_student'))
            except:
                flash("ID Number must be YYYY-NNNN")
                return redirect(url_for('students.delete_student'))
        else:
            flash("Student does not exist")
            return redirect(url_for('students.delete_student'))
    return render_template('students/delete-students.html', form=form, all_students=all_students)

@students.route('/update-student', methods =['GET','POST'])
def update_student():
    form = update_student_form()
    all_students = Students.query_filter(all=True)
    form.new_college.choices = [(college.college_code, college.college_name) for college in Colleges.query_filter(all=True)]
    form.new_course.choices = [(course.course_code, course.course_name) for course in Courses.query_filter(all=True)]
    return render_template('students/update-students.html', form=form, all_students=all_students)

@students.route("/home/update-student/<id>", methods=['GET', 'POST'])
def update_student_info(id):
    form = update_student_form()
    new_profile_picture = form.new_profile_pic.data
    form.new_college.choices = [(college.college_code, college.college_name) for college in Colleges.query_filter(all=True)]
    form.new_course.choices = [(course.course_code, course.course_name) for course in Courses.query_filter(all=True)]
    if request.method == 'POST':
        # try:
            if new_profile_picture:
                if new_profile_picture.filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS:
                    upload_result = cloudinary.uploader.upload(new_profile_picture, folder="SIS")
                    new_profile_picture = upload_result['secure_url']
            new_id_number = form.new_id_number.data
            new_first_name = form.new_first_name.data
            new_last_name = form.new_last_name
            new_course = form.new_course.data
            new_year_level = form.new_year_level.data
            new_gender = form.new_gender.data
            new_college= form.new_college.data
            Students.update_student(id, new_id=new_id_number, new_year_lvl=new_year_level, new_first_name=new_first_name, new_course=new_course, new_college=new_college, new_last_name=new_last_name, new_gender=new_gender, new_profile_pic=new_profile_picture)
            mysql.connection.commit()
            flash('Student Edited Successfully!')
            return redirect(url_for('students.update_student'))
        # except:
        #     flash('Student Already Exists!')
        #     return redirect(url_for('students.update_student'))
    return render_template('students/update-students.html', form=form)

@students.route("/home/add-student/course/<college_code>", methods=['GET', 'POST'])
def course(college_code):
    courses = Courses.query_filter(resp_college=college_code)
    coursesArray = []

    for course in courses:
        courseObj = {}
        courseObj['course_code'] = course.course_code
        courseObj['course_name'] = course.course_name
        coursesArray.append(courseObj)
    
    return jsonify({'courses': coursesArray})
    
        