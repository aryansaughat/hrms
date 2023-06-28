from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash, send_file,\
    send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import sqlite3
from datetime import datetime, timedelta
import datetime
import calendar
from flask_mail import Mail, Message
import base64
from functools import wraps
import pickle
import os
import numpy as np
import nepali_datetime as nd

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'noreply.hrms2@gmail.com'
app.config['MAIL_PASSWORD'] = 'bmoknegzgfzscmqs'
mail = Mail(app)
UPLOAD_FOLDER = 'D:/project/employee files'
#UPLOAD_FOLDER = 'G:/project/employee files'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
DATABASE = 'hrms.db'

#app.permanent_session_lifetime = timedelta(minutes=30)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def main():
    if 'user_id' in session:
        username = session['user_id']
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            select_query = "SELECT count(*) FROM Employees"
            c.execute(select_query)
            count1 = c.fetchone()
            date = datetime.date.today()
            select_query = "SELECT count(*) FROM Attendance where Attendance_date= :ad "
            c.execute(select_query, {"ad": date})
            count2 = c.fetchone()
            select_query = "SELECT count(*) FROM Leaves where Status='pending' "
            c.execute(select_query)
            count3 = c.fetchone()
            select_query = "SELECT count(*) FROM Departments"
            c.execute(select_query)
            count4 = c.fetchone()
            select_query = "SELECT count(*) FROM Designations"
            c.execute(select_query)
            count5 = c.fetchone()
            select_query = '''SELECT count(*) FROM Attendance where Attendance_date= :ad
                                       and employee_id=(SELECT employee_id FROM users WHERE username= :un)'''
            c.execute(select_query, {"ad": date, "un": username})
            attendance_count = c.fetchone()[0]
            attendance_exists = attendance_count > 0
            return render_template('home.html', emp=count1, atndce=count2, leave=count3, depart=count4,
                                   desgn=count5, ae=attendance_exists)
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            select_query = "SELECT * FROM users WHERE username = :username"
            c.execute(select_query, {"username": username})
            user = c.fetchone()
            if user:
                if user[14] == 'Active':
                    if check_password_hash(user[4], password):
                        session['user_id'] = username
                        return redirect('/dashboard')
                    else:
                        flash('Invalid Password. Please Enter Corect Password', 'Error')
                        return render_template('login.html')
                else:
                    flash('User is inactive. Please Contact Administration', 'Error')
                    return redirect('/login')
            else:
                flash('Invalid username. Please Enter Correct Username', 'Error')
                return redirect('/login')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect('/login')


@app.route('/dashboard')
def home():
    if 'user_id' in session:
        username = session['user_id']
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            select_query = "SELECT count(*) FROM Employees"
            c.execute(select_query)
            count1 = c.fetchone()
            date = datetime.date.today()
            select_query = "SELECT count(*) FROM Attendance where Attendance_date= :ad "
            c.execute(select_query, {"ad": date})
            count2 = c.fetchone()
            select_query = "SELECT count(*) FROM Leaves where Status='pending' "
            c.execute(select_query)
            count3 = c.fetchone()
            select_query = "SELECT count(*) FROM Departments"
            c.execute(select_query)
            count4 = c.fetchone()
            select_query = "SELECT count(*) FROM Designations"
            c.execute(select_query)
            count5 = c.fetchone()
            select_query = '''SELECT count(*) FROM Attendance where Attendance_date= :ad
                           and employee_id=(SELECT employee_id FROM users WHERE username= :un)'''
            c.execute(select_query, {"ad": date, "un": username})
            attendance_count = c.fetchone()[0]
            attendance_exists = attendance_count > 0
            return render_template('home.html', emp=count1, atndce=count2, leave=count3, depart=count4,
                                   desgn=count5, ae=attendance_exists)
    else:
        return redirect(url_for('login'))


@app.route('/users')
@login_required
def user_form():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM Users")
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        users = []
        for row in result:
            user = dict(zip(columns, row))
            users.append(user)

        select_query = "SELECT * FROM Departments"
        c.execute(select_query)
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        departments = []
        for row in result:
            department = dict(zip(columns, row))
            departments.append(department)

        select_query = "SELECT * FROM Designations"
        c.execute(select_query)
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        designations = []
        for row in result:
            designation = dict(zip(columns, row))
            designations.append(designation)

        select_query = "SELECT * FROM Roles"
        c.execute(select_query)
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        roles = []
        for row in result:
            role = dict(zip(columns, row))
            roles.append(role)
    return render_template('usercreation.html', users=users, depart=departments, designation=designations, roles=roles)


@app.route('/create_user', methods=['POST', 'GET'])
@login_required
def create_user():
    if request.method == 'POST':
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            cusername = session['user_id']
            eid = request.form['id']
            name = request.form['name']
            username = request.form['username']
            password = request.form['password']
            email = request.form['email']
            phone = request.form['phone']
            role = request.form['role']
            designation = request.form['designation']
            department = request.form['department']
            hashed_password = generate_password_hash(password)
            status = 'inactive'
            c.execute(
                '''INSERT INTO Users (Employee_ID,Name, Username, Password, Email, Phone, Role, designation, department, 
                created_by, Status) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                (eid, name, username, hashed_password, email, phone, role, designation, department, cusername, status))
            conn.commit()
            if conn.total_changes > 0:
                flash('User Created successfully', 'Sucess')
                return redirect(url_for('user_form'))
        except Exception as e:
            flash('Error creating user: ' + str(e), 'error')
    return redirect(url_for('user_form'))


@app.route('/get_user_data', methods=['POST'])
def get_user_data():
    id = request.form['id']
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    select_query = '''SELECT * FROM Users WHERE Id=:i'''
    c.execute(select_query, {'i': id})
    user = c.fetchone()
    columns = [desc[0] for desc in c.description]
    result = dict(zip(columns, user))
    c.close()
    if result is not None:
        employee_id = result['Employee_ID']
        user_name = result['Name']
        username = result['Username']
        email = result['Email']
        phone = result['Phone']
        role = result['Role']
        designation = result['Designation']
        department = result['Department']
        return jsonify({
            'id': id,
            'empid': employee_id,
            'name': user_name,
            'username': username,
            'email': email,
            'phone': phone,
            'role': role,
            'designation': designation,
            'department': department
        })


@app.route('/edit_user/<int:id>', methods=['POST'])
@login_required
def edit_user(id):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        if request.method == 'POST':
            cusername = session['user_id']
            eid = request.form['id']
            username = request.form['username']
            role = request.form['role']
            designation = request.form['designation']
            department = request.form['department']
            try:
                update_query = """
                       UPDATE Users
                       SET username=?,
                         role=?,
                         designation=?,
                         department=?,
                         updated_by=?
                       WHERE ID = ? AND Employee_ID = ?
                   """
                c.execute(update_query, (username, role, designation, department, cusername, id, eid))
                conn.commit()
                if conn.total_changes > 0:
                    flash('Updated Successfully', 'success')
                    return redirect(url_for('user_form'))
            except Exception as e:
                flash('Error While Updating. Please Try again Later' + str(e), 'error')
                return redirect(url_for('user_form'))
    return redirect(url_for('user_form'))


@app.route('/changestatus/<int:id>', methods=['POST', 'GET'])
def changestatus(id):
    try:
        username = session['user_id']
        with sqlite3.connect(DATABASE) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            select_query = "SELECT Status FROM Users WHERE Id = ?"
            c.execute(select_query, (id,))
            row = c.fetchone()
            if row is None:
                flash('User not found', 'error')
                return redirect(url_for('create_user'))
            current_status = row['Status']
            new_status = 'Inactive' if current_status.lower() == 'active' else 'Active'
            update_query = "UPDATE Users SET Status = ?, Updated_by = ? WHERE Id = ?"
            c.execute(update_query, (new_status, username, id))
            conn.commit()
            if conn.total_changes > 0:
                flash('User status changed successfully', 'success')
            else:
                flash('No changes made to user status', 'info')
        return redirect(url_for('create_user'))
    except Exception as e:
        flash('Error while changing status: ' + str(e), 'error')
        return redirect(url_for('create_user'))


@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    try:
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        if request.method == 'POST':
            username = request.form['username']
            email = request.form['email']
            select_query = "SELECT * FROM USERS WHERE username = :u and email = :e"
            c.execute(select_query, {"u": username, "e": email})
            result = c.fetchone()
            if result:
                send_password_email(email, 'Hrms@123', username)
                flash('New password is sent to your email', 'Sucess')
                rst_password(result[0])
                return redirect(url_for('login'))
            else:
                flash('Username and Password doesnot match. Please Enter again', 'Warning')
                return redirect(url_for('login'))
    except Exception as e:
        flash('Error while reseting password: ' + str(e), 'error')
        return redirect(url_for('login'))


def send_password_email(recipient, new_password, username):
    subject = 'Password Reset'
    msg = Message(subject=subject, sender='noreply.hrms2@gmail.com', recipients=[recipient])
    with open("G:/Kapil/study/final project/hr/static/images/logo.png", "rb") as logo_file:
        logo_data = logo_file.read()
        logo_base64 = base64.b64encode(logo_data).decode("utf-8")
    email_content = render_template("resetpasswordtemplate.html", un=username, password=new_password, logo_base64=logo_base64)
    msg.html = email_content
    mail.send(msg)
    return 'Password reset email sent'


@app.route('/fetch_employee_data', methods=['GET'])
def fetch_employee_data():
    employee_id = request.args.get('id')
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        check = "SELECT * FROM Users where Employee_id= :id"
        c.execute(check, {"id": employee_id})
        result = c.fetchone()
        if result is not None:
            error_message = "User already created for employee ID: {}".format(employee_id)
            return jsonify({'error': error_message}), 400
        query = "SELECT Name, Email, Phone, Designation, Department FROM employees WHERE id= :id"
        c.execute(query, {"id": employee_id})
        result = c.fetchone()
        c.close()
        if result is not None:
            name = result[0]
            email = result[1]
            phone = result[2]
            designation = result[3]
            department = result[4]
            return jsonify(
                {'name': name, 'email': email, 'phone': phone, 'design': designation, 'department': department})
        else:
            error_message = "Employee ID not found: {}. Please Enter Employee Data first".format(employee_id)
            return jsonify({'error': error_message}), 400


@app.route('/modules')
@login_required
def modules():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''SELECT Role_Name FROM roles''')
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        roles = []
        for row in result:
            role = dict(zip(columns, row))
            roles.append(role)
        c.execute('''SELECT * FROM Modules''')
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        modules = []
        for row in result:
            module = dict(zip(columns, row))
            modules.append(module)
        c.execute('''SELECT * FROM Modulesassigned''')
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        massigneds = []
        for row in result:
            massigned = dict(zip(columns, row))
            massigneds.append(massigned)
    return render_template('modules.html', roles=roles, modules=modules, assigned=massigneds)


@app.route('/addmodules', methods=['GET', 'POST'])
@login_required
def add_modules():
    try:
        username = session['user_id']
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        if request.method == 'POST':
            role = request.form['role']
            modules = request.form.getlist('modules')
            modules_str = ','.join(modules)
            insert_query = "INSERT INTO Modulesassigned (Role, Description, entered_by) VALUES (?, ?, ?)"
            c.execute(insert_query, (role, modules_str, username))
            conn.commit()
            if conn.total_changes > 0:
                flash("Modules assigned to role successfully", 'success')
                return redirect(url_for('modules'))
    except Exception as e:
        flash('Error assigning modules: ' + str(e), 'error')
        return redirect(url_for('modules'))


@app.route('/reset_password')
def reset_password():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        select_query = "SELECT * FROM Users"
        c.execute(select_query)
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        users = []
        for row in result:
            user = dict(zip(columns, row))
            users.append(user)
    return render_template('resetpassword.html', users=users)


@app.route('/rst_password/<int:id>')
def rst_password(id):
    try:
        username = session['user_id']
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        password = 'Hrms@123'
        hashed_password = generate_password_hash(password)
        update_query = "UPDATE Users set password= :pass, updated_by= :un WHERE Id= :i"
        c.execute(update_query, {"pass": hashed_password, "un": username, "i": id})
        conn.commit()
        if conn.total_changes > 0:
            flash('Password reseted to : {} '.format(password))
            return redirect(url_for('reset_password'))
    except Exception as e:
        flash('Error Reseting Password: ' + str(e), 'error')


@app.route('/profile')
@login_required
def profile():
    username = session['user_id']
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        select_query = "SELECT * FROM employees where id=(select employee_id from Users where username=?)"
        c.execute(select_query, (username,))
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        users = []
        for row in result:
            user = dict(zip(columns, row))
            users.append(user)

        select_query = "SELECT * FROM Experiences WHERE employee_id=(select employee_id from Users where username=?)"
        c.execute(select_query, (username,))
        result1 = c.fetchall()
        columns = [desc[0] for desc in c.description]
        experiences = []
        for row in result1:
            experience = dict(zip(columns, row))
            experiences.append(experience)

        select_query = "SELECT * FROM Qualifications WHERE employee_id=(select employee_id from Users where username=?)"
        c.execute(select_query, (username,))
        result2 = c.fetchall()
        columns = [desc[0] for desc in c.description]
        qualifications = []
        for row in result2:
            qualification = dict(zip(columns, row))
            qualifications.append(qualification)

        select_query = "SELECT profile_image_path FROM Employees WHERE id =(select employee_id from Users where username=?)"
        c.execute(select_query, (username,))
        result = c.fetchone()
        pip = ''
        if result:
            pip = result[0]
            return render_template('profile.html', employee=users, experiences=experiences,
                                   qualifications=qualifications, profile_image_path=pip)
    return render_template('profile.html', employee=users, experiences=experiences, qualifications=qualifications)



@app.route('/employee_records')
@login_required
def employee_records():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''SELECT * FROM Employees''')
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        employees = []
        for row in result:
            employee = dict(zip(columns, row))
            employees.append(employee)
    return render_template('employee.html', employees=employees)



@app.route('/add_employee', methods=['GET', 'POST'])
@login_required
def add_employee():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    select_query = "SELECT * FROM Departments"
    c.execute(select_query)
    result = c.fetchall()
    columns = [desc[0] for desc in c.description]
    departments = []
    for row in result:
        department = dict(zip(columns, row))
        departments.append(department)
    select_query = "SELECT * FROM Designations"
    c.execute(select_query)
    result = c.fetchall()
    columns = [desc[0] for desc in c.description]
    designations = []
    for row in result:
        designation = dict(zip(columns, row))
        designations.append(designation)
    try:
        username = session['user_id']
        if request.method == 'POST':
            empid = request.form['id']
            name = request.form['name']
            father_name = request.form.get('father_name')
            mother_name = request.form.get('mother_name')
            grandfather_name = request.form.get('grandfather_name')
            gender = request.form['gender']
            date_of_birth = request.form.get('date_of_birth')
            email = request.form['email']
            phone = request.form['phone']
            address = request.form['address']
            citizenship_number = request.form.get('citizenship_number')
            designation = request.form['designation']
            department = request.form['department']
            joining_date = request.form.get('joining_date')
            terminated = bool(request.form.get('terminated'))
            termination_reason = request.form.get('termination_reason')
            bank_account_number = request.form.get('bank_account_number')
            marital_status = request.form.get('marital_status')
            profile_image = request.files['profile_image']
            active = bool(request.form.get('active'))
            termination_date = request.form.get('termination_date')
            pan_number = request.form.get('pan_number')
            spouse_name = request.form.get('spouse_name')
            if empid:
                folder_path = os.path.join(app.config['UPLOAD_FOLDER'], name + "_" + str(empid))
                os.makedirs(folder_path, exist_ok=True)
            else:
                c.execute('SELECT MAX(ID) FROM Employees')
                empid = c.fetchone()[0] + 1
                folder_path = os.path.join(app.config['UPLOAD_FOLDER'], name + "_" + str(empid))
                os.makedirs(folder_path, exist_ok=True)
            profile_image_path = ''
            if profile_image:
                filename = secure_filename(profile_image.filename)
                _, extension = os.path.splitext(filename)
                profile_image_path = os.path.join(folder_path, f'profile_image{extension}')
                profile_image.save(profile_image_path)
            if empid:
                data = (empid, name, email, phone, address, gender, father_name, mother_name, grandfather_name, designation,
                        department, citizenship_number, date_of_birth, joining_date, active, username, terminated,
                        termination_date, termination_reason, bank_account_number, pan_number, marital_status,
                        spouse_name, profile_image_path)
                query = '''INSERT INTO employees (ID, Name, Email, Phone, Address, Gender, Father_Name, Mother_Name,
                            Grandfather_Name, Designation, Department, Citizenship_number, Date_Of_Birth, Joining_Date,
                            active, Created_By, terminated, termination_date,
                            termination_reason, bank_account_number, PAN_number, marital_status, spouse_name,
                            profile_image_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                                            ?, ?, ?, ?, ?, ?)'''
                c.execute(query, data)
                conn.commit()
                if conn.total_changes>0:
                    flash("Employee Details Added Successfully", 'Success')
                    return redirect(url_for('add_employee'))
            else:
                data = (name, email, phone, address, gender, father_name, mother_name, grandfather_name, designation,
                department, citizenship_number, date_of_birth, joining_date, active, username, terminated,
                termination_date, termination_reason, bank_account_number, pan_number, marital_status,
                spouse_name, profile_image_path)
                query = '''INSERT INTO employees (Name, Email, Phone, Address, Gender, Father_Name, Mother_Name,
                            Grandfather_Name, Designation, Department, Citizenship_number, Date_Of_Birth, Joining_Date,
                            active, Created_By, terminated, termination_date,
                            termination_reason, bank_account_number, PAN_number, marital_status, spouse_name,
                            profile_image_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                            ?, ?, ?, ?, ?, ?)'''
                c.execute(query, data)
                conn.commit()
                if conn.total_changes > 0:
                    flash("Employee Details Added Successfully", 'Success')
                    return redirect(url_for('add_employee'))
    except Exception as e:
        flash('Error adding employee: ' + str(e), 'error')
    return render_template('add_employee.html', depart=departments, designation=designations)


@app.route('/edit_employee/<int:id>')
@login_required
def edit_employee(id):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''SELECT * FROM Employees''')
        conn.commit()
    return redirect(url_for('employee_records'))


@app.route('/Delete_employee/<int:id>')
@login_required
def delete_employee(id):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''DELETE FROM Employees where id=?''', (id,))
        conn.commit()
    return redirect(url_for('employee_records'))


@app.route('/qualifications', methods=['GET', 'POST'])
@login_required
def qualifications():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''SELECT * FROM Qualifications''')
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        qualifications = []
        for row in result:
            qualification = dict(zip(columns, row))
            qualifications.append(qualification)
    return render_template('qualification.html', qualifications=qualifications)


@app.route('/add_qualifications', methods=['GET', 'POST'])
@login_required
def add_qualifications():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        qualification_name = request.form.get('qualification_name')
        college_name = request.form.get('college_name')
        board = request.form.get('board')
        divisions = request.form.get('divisions')
        grade = request.form.get('grade')
        username = session['user_id']
        resume_file = request.files['doc_qualification']
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            select = '''SELECT Employee_ID, Name FROM Users WHERE Username=?'''
            c.execute(select, (username,))
            result = c.fetchone()
            name = result[1]
            id = result[0]

        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], name + "_" + str(id))
        os.makedirs(folder_path, exist_ok=True)
        resume_file_path = ''
        if resume_file:
            filename = secure_filename(resume_file.filename)
            extension = os.path.splitext(filename)[1]
            resume_file_path = os.path.join(folder_path, f'qualification{extension}')
            resume_file.save(resume_file_path)
        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            insert_query = '''INSERT INTO qualifications (employee_id, level, college_name, board, division, grade, 
                                Entered_by, doc_file_path) VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
            c.execute(insert_query, (employee_id, qualification_name, college_name, board, divisions, grade, username, resume_file_path))
            conn.commit()
            if conn.total_changes > 0:
                flash('Qualification added successfully', 'success')
                return redirect(url_for('qualifications'))
        except Exception as e:
            flash('Error adding qualification: ' + str(e), 'error')
    return redirect(url_for('qualifications'))


@app.route('/edit_qualification/<id>', methods=['GET', 'POST'])
@login_required
def edit_qualification(id):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        if request.method == 'POST':
            employee_id = request.form['employee_id']
            qualification_name = request.form['qualification_name']
            college_name = request.form['college_name']
            board = request.form['board']
            divisions = request.form['divisions']
            grade = request.form['grade']
            username = session['user_id']
            try:
                update_query = """
                       UPDATE qualifications
                       SET Employee_ID = ?,
                           Level = ?,
                           College_Name = ?,
                           Board = ?,
                           Division = ?,
                           Grade = ?,
                           updated_by =?
                       WHERE ID = ?
                   """
                c.execute(update_query, (employee_id, qualification_name, college_name, board, divisions, grade, username, id))
                conn.commit()
                if conn.total_changes > 0:
                    flash('Updated Successfully', 'success')
                    return redirect(url_for('qualifications'))
            except Exception as e:
                flash('Error While Updating. Please Try again Later', 'error')
                return redirect(url_for('qualifications'))
    return redirect(url_for('qualifications'))

@app.route('/Delete_qualification/<int:id>')
@login_required
def delete_qualification(id):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''DELETE FROM qualifications WHERE ID=? ''', (id,))
        conn.commit()
    return redirect(url_for('qualifications'))


@app.route('/experiences', methods=['GET', 'POST'])
@login_required
def experiences():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''SELECT * FROM Experiences''')
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        experiences = []
        for row in result:
            experience = dict(zip(columns, row))
            experiences.append(experience)
    return render_template('experience.html', experiences=experiences)


@app.route('/add_experience', methods=['GET', 'POST'])
@login_required
def add_experience():
    username = session['user_id']
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        description = request.form.get('job_description')
        company_name = request.form.get('company_name')
        position = request.form.get('position')
        duration = request.form.get('duration')
        resume_file = request.files['doc_experience']
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            select = '''SELECT Employee_ID, Name FROM Users WHERE Username=?'''
            c.execute(select, (username,))
            result = c.fetchone()
            name = result[1]
            id = result[0]

        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], name + "_" + str(id))
        os.makedirs(folder_path, exist_ok=True)
        resume_file_path = ''
        if resume_file:
            filename = secure_filename(resume_file.filename)
            extension = os.path.splitext(filename)[1]
            resume_file_path = os.path.join(folder_path, f'experienceletter{extension}')
            resume_file.save(resume_file_path)

        try:
            conn = sqlite3.connect(DATABASE)
            c = conn.cursor()
            insert_query = '''INSERT INTO experiences (employee_id, company_name, duration,
                                job_title, job_description, entered_by, doc_file_path)
                                VALUES (?, ?, ?, ?, ?, ?, ?)'''
            c.execute(insert_query,
                      (employee_id, company_name, duration, position, description, username, resume_file_path))
            conn.commit()
            if c.rowcount > 0:
                flash('Experience added successfully', 'success')
                return redirect(url_for('experiences'))
        except Exception as e:
            flash('Error adding experience: ' + str(e), 'error')
    return redirect(url_for('experiences'))


@app.route('/edit_experience/<id>', methods=['GET', 'POST'])
@login_required
def edit_experience(id):
    username = session['user_id']
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        if request.method == 'POST':
            employee_id = request.form.get('employee_id')
            company_name = request.form.get('company_name')
            position = request.form.get('position')
            description = request.form.get('job_description')
            duration = request.form.get('duration')
            try:
                update_query = '''UPDATE experiences SET employee_id=?, company_name=?, job_description=?,
                                job_title=?, duration=?, updated_by=? WHERE id=?'''
                c.execute(update_query, (employee_id, company_name, description, position, duration, username, id))
                conn.commit()
                if conn.total_changes > 0:
                    flash('Experience updated successfully', 'success')
                    return redirect(url_for('experiences'))
            except Exception as e:
                flash('Error eding experience: ' + str(e), 'error')
                return redirect(url_for('experiences'))
    return redirect(url_for('edit_experience', id=id))


@app.route('/delete_experience/<int:experience_id>', methods=['GET', 'POST'])
@login_required
def delete_experience(experience_id):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        try:
            delete_query = "DELETE FROM experiences WHERE id=?"
            c.execute(delete_query, (experience_id,))
            conn.commit()
            if conn.total_changes > 0:
                flash('Experience deleted successfully', 'success')
                return redirect(url_for('experiences'))
        except Exception as e:
            flash('Error deleting Experiences: ' + str(e), 'error')
            return redirect(url_for('experiences'))
    return redirect(url_for('experiences'))


@app.route('/department')
@login_required
def department():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        select_query = '''SELECT d.*, COUNT(e.ID) AS empcount FROM departments d
                            left join Employees e ON UPPER(d.Depart_Name) = UPPER(e.Department) GROUP BY e.Department;'''
        c.execute(select_query)
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        departments = []
        for row in result:
            department = dict(zip(columns, row))
            departments.append(department)
    return render_template('department.html', depart=departments)



@app.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_department():
    username = session['user_id']
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        if request.method == 'POST':
            dname = request.form['department']
            description = request.form['description']
            try:
                insert_query = '''INSERT INTO Departments (Depart_Name, Description, Entered_by) VALUES (?, ?, ?)'''
                c.execute(insert_query, (dname, description, username))
                conn.commit()
                if conn.total_changes > 0:
                    flash("Department Added Successfully", 'Success')
                    return redirect(url_for('department'))
            except Exception as e:
                flash("Error occured While Adding Department", 'Error')
                return redirect(url_for('department'))
    return redirect(url_for('add_department'))



@app.route('/edit_department/<id>', methods=['GET', 'POST'])
@login_required
def edit_department(id):
    username = session['user_id']
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        if request.method == 'POST':
            dname = request.form['department']
            description = request.form['description']
            try:
                update_query = "UPDATE departments SET Depart_Name=?, Description=?, updated_by=? WHERE id=?"
                c.execute(update_query, (dname, description, username))
                conn.commit()
                if conn.total_changes > 0:
                    flash('Department updated successfully', 'success')
                    return redirect(url_for('department'))
            except Exception as e:
                flash('Error editing department: ' + str(e), 'error')
                return redirect(url_for('department'))
    return redirect(url_for('department'))


@app.route('/delete_department/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_department(id):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        try:
            delete_query = "DELETE FROM departments WHERE id=?"
            c.execute(delete_query, (id,))
            conn.commit()
            if conn.total_changes > 0:
                flash('Department deleted successfully', 'success')
                return redirect(url_for('department'))
        except Exception as e:
            flash('Error deleting department: ' + str(e), 'error')
            return redirect(url_for('department'))
    return redirect(url_for('department'))


@app.route('/designation')
@login_required
def designation():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        select_query = '''SELECT d.*, COUNT(e.ID) AS empcount FROM Designations d
                            LEFT JOIN Employees e ON UPPER(d.Post_Name) = UPPER(e.Designation) GROUP BY d.Post_Name'''
        c.execute(select_query)
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        designations = []
        for row in result:
            designation = dict(zip(columns, row))
            designations.append(designation)
    return render_template('designation.html', designations=designations)


@app.route('/add_designation', methods=['GET', 'POST'])
@login_required
def add_designation():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        username = session['user_id']
        if request.method == 'POST':
            dname = request.form['designation']
            description = request.form['description']
            try:
                insert_query = '''INSERT INTO Designations (Post_Name, Description, Entered_by) VALUES (?, ?, ?)'''
                c.execute(insert_query, (dname, description, username))
                conn.commit()
                if conn.total_changes > 0:
                    flash("Designation Added Successfully", 'Success')
                    return redirect(url_for('designation'))
            except Exception as e:
                flash('Error adding Designation: ' + str(e), 'error')
                return redirect(url_for('designation'))
    return redirect(url_for('add_designation'))


@app.route('/edit_designation/<id>', methods=['GET', 'POST'])
@login_required
def edit_designation(id):
    username = session['user_id']
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        if request.method == 'POST':
            designation = request.form['designation']
            description = request.form['description']
            try:
                update_query = "UPDATE designations SET Post_Name=?, Description=?, updated_by=? WHERE id=?"
                c.execute(update_query, (designation, description, username, id))
                conn.commit()
                if conn.total_changes > 0:
                    flash('Designation updated successfully', 'success')
                    return redirect(url_for('designation'))
            except Exception as e:
                flash('Error updating designation: ' + str(e), 'error')
                return redirect(url_for('designation'))
    return redirect(url_for('edit_designation'))


@app.route('/delete_designation/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_designation(id):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        try:
            delete_query = "DELETE FROM designations WHERE id=?"
            c.execute(delete_query, (id,))
            conn.commit()
            if conn.total_changes > 0:
                flash('Designation deleted successfully', 'success')
                return redirect(url_for('designation'))
        except Exception as e:
            flash('Error Deleting designation: ' + str(e), 'error')
            return redirect(url_for('designation'))
    return redirect(url_for('delete_designation'))


@app.route('/role')
@login_required
def role():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        select_query = "SELECT * FROM roles"
        c.execute(select_query)
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        roles = []
        for row in result:
            role = dict(zip(columns, row))
            roles.append(role)
    return render_template('role.html', roles=roles)


@app.route('/add_role', methods=['GET', 'POST'])
@login_required
def add_role():
    username = session['user_id']
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        if request.method == 'POST':
            rname = request.form['role']
            description = request.form['description']
            try:
                insert_query = '''INSERT INTO Roles (Role_Name, Description, Entered_by) VALUES (?, ?, ?)'''
                c.execute(insert_query, (rname, description, username))
                conn.commit()
                if conn.total_changes > 0:
                    flash("Roles added Successfully", 'success')
                    return redirect(url_for('role'))
            except Exception as e:
                flash('Error adding roles: ' + str(e), 'error')
                return redirect(url_for('role'))
    return redirect(url_for(add_role))


@app.route('/edit_role', methods=['POST', 'GET'])
@login_required
def edit_role():
    username = session['user_id']
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        if request.method == 'POST':
            id = request.form.get('role_id')
            rname = request.form['role']
            description = request.form['description']
            try:
                update_query = "Update Roles set Role_Name= :r , Description= :d, Updated_by=:un where Id= :i "
                c.execute(update_query, {"r": rname, "d": description, "un": username, "i": id})
                conn.commit()
                if conn.total_changes > 0:
                    flash('Roles updated successfully', 'success')
                    return redirect(url_for('role'))
                else:
                    flash('Error updating role: ', 'error')
                    return redirect(url_for('role'))
            except Exception as e:
                flash('Error updating role: ' + str(e), 'error')
                return redirect(url_for('role'))


@app.route('/Delete_role/<int:id>')
@login_required
def delete_role(id):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        try:
            delet_query = '''DELETE FROM Roles where id=?'''
            c.execute(delet_query, (id,))
            conn.commit()
            if conn.total_changes > 0:
                flash('roles deleted successfully', 'success')
                return redirect(url_for('role'))
        except Exception as e:
            flash('Error adding qualification: ' + str(e), 'error')
            return redirect(url_for('role'))
    return redirect(url_for('delete_role'))


@app.route('/leave_management')
@login_required
def leave_management():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        select_query = "SELECT e.name,l.* FROM Leaves l left join employees e on l.employee_id=e.ID WHERE UPPER(Status)='PENDING'"
        c.execute(select_query)
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        leaves = []
        for row in result:
            leave = dict(zip(columns, row))
            leaves.append(leave)
    return render_template('leave.html', leaves=leaves)


@app.route('/add_leave', methods=['GET', 'POST'])
@login_required
def add_leave():
    username = session['user_id']
    if request.method == 'POST':
        employee_id = request.form['emp_id']
        start_date = request.form['fromdate']
        end_date = request.form['todate']
        typ = request.form['type']
        reason = request.form['reason']
        status = request.form['status']
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO Leaves (employee_id, start_date, end_date, type, reason, Status, Created_by)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''', (employee_id, start_date, end_date, typ, reason, status, username))
            conn.commit()
            if conn.total_changes > 0:
                flash('Leave applied successfully', 'success')
                return redirect(url_for('add_leave'))
        return redirect(url_for('add_leave'))
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        select_query = '''SELECT * FROM Leaves WHERE UPPER(Status)='PENDING' AND 
                            Employee_ID=(SELECT employee_id from users where username= :un)'''
        c.execute(select_query, {'un': username})
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        leaves = []
        for row in result:
            leave = dict(zip(columns, row))
            leaves.append(leave)
        select_query = "SELECT Employee_ID FROM users WHERE username= :u"
        c.execute(select_query, {"u": username})
        result = c.fetchone()
        columns = [desc[0] for desc in c.description]
        users = dict(zip(columns, result))
    return render_template('addleave.html', leaves=leaves, users=users)


@app.route('/approve_ leave/<int:id>', methods=['GET', 'POST'])
@login_required
def approve_leave(id):
    username = session['user_id']
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        status = 'approved'
        update_query = "UPDATE Leaves SET Status= :s, Approved_by= :un Where id= :i"
        c.execute(update_query, {"s": status, "un": username, "i": id})
        conn.commit()
        flash('Leave approved successfully', 'success')
    return redirect(url_for('leave_management'))


@app.route('/reject_ leave/<int:id>', methods=['GET', 'POST'])
@login_required
def reject_leave(id):
    username = session['user_id']
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        status = 'rejected'
        update_query = "UPDATE Leaves SET Status= :s, Approved_by= :un Where id= :i"
        c.execute(update_query, {"s": status, "un": username, "i": id})
        conn.commit()
        flash('Leave rejected successfully', 'success')
    return redirect(url_for('leave_management'))


@app.route('/leave_history')
@login_required
def leave_history():
    username = session['user_id']
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        select_query = "SELECT * FROM leaves where employee_id=(select employee_id from Users where username= :un)"
        c.execute(select_query, {"un": username})
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        leaves = []
        for row in result:
            leave = dict(zip(columns, row))
            leaves.append(leave)
    return render_template('leavehistory.html', leaves=leaves)


@app.route('/performance_prediction')
@login_required
def performance_prediction():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''SELECT * FROM performances''')
        result = c.fetchall()
        with open('G:/Kapil/study/final project/New folder/hrms/svm_model.pkl', 'rb') as file:
            model = pickle.load(file)
            new_data = {
                'MaritalStatusID': [1],
                'GenderID': [0],
                'EmpStatusID': [5],
                'DeptID': [5],
            }
            data_arrays = [np.array(values) for values in new_data.values()]
            input_data = np.column_stack(data_arrays)
            prediction = model.predict(input_data)
            print(prediction)
    return render_template('performance.html', performances=result, prediction=prediction)


def add_performance_db(emp_id, age, experience, comments):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''INSERT INTO performances (Employee_ID, Age, Experience, Comment)
                VALUES (?, ?, ?, ?)''', (emp_id, age, experience, comments))
        conn.commit()


@app.route('/add_performance', methods=['GET', 'POST'])
def add_performance():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        age = request.form['age']
        experience = request.form['experience']
        comments = request.form['comments']
        add_performance_db(emp_id, age, experience, comments)
        flash('Performance record added successfully')
        return redirect(url_for('performance_management'))
    else:
        return redirect(url_for('performance_management'))


@app.route('/edit_performance', methods=['GET', 'POST'])
def edit_performance():
    if request.method == 'POST':
        emp_id = request.form['emp_id']
        age = request.form['age']
        experience = request.form['experience']
        comments = request.form['comments']
        add_performance_db(emp_id, age, experience, comments)
        flash('Performance record added successfully')
        return redirect(url_for('performance_management'))
    else:
        return redirect(url_for('performance_management'))


@app.route('/index', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = 'Kapil'
        id = '1'
        profile_image = request.files['profile_image']
        resume_file = request.files['resume_file']
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], name + "_" + str(id))
        os.makedirs(folder_path, exist_ok=True)
        profile_image_path = ''
        resume_file_path = ''
        if profile_image:
            filename = secure_filename(profile_image.filename)
            _, extension = os.path.splitext(filename)
            profile_image_path = os.path.join(folder_path, f'profile_image{extension}')
            profile_image.save(profile_image_path)

        if resume_file:
            resume_file.save(os.path.join(folder_path, 'resume_file.pdf'))
            resume_file_path = os.path.join(folder_path, 'resume_file.pdf')
            resume_file.save(resume_file_path)
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO files (name, profile_image_path, resume_file_path) VALUES (?, ?, ?)",
                      (name, profile_image_path, resume_file_path))
            conn.commit()
            if conn.total_changes > 0:
                flash('File uploaded successfully', 'Success')
                return render_template('index.html')
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute("SELECT profile_image_path FROM files WHERE id = 1")
        result1 = c.fetchone()
        c.execute("SELECT resume_file_path FROM files WHERE id = 1")
        result = c.fetchone()
        if result1:
            if result:
                resume_file_path = result[0]
                profile_image_path = result1[0]
                return render_template('index.html', profile_image_path=profile_image_path,
                                       resume_file_path=resume_file_path)
    return render_template('index.html')


@app.route('/image/<path:filename>')
def display_image(filename):
    return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))


@app.route('/file/<filename>')
def display_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)


@app.route('/attendance', methods=['GET', 'POST'])
@login_required
def attendance():
    username = session['user_id']
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        if request.method == 'POST':
            userid = session['user_id']
            select_query = "SELECT Employee_ID FROM Users WHERE  username=:userid"
            c.execute(select_query, {"userid": userid})
            user_id = c.fetchone()[0]
            attendance_date = datetime.date.today()
            attendance_time = request.form['time']
            latitude = request.form['latitude']
            longitude = request.form['longitude']
            query = "SELECT * FROM Attendance where employee_id= :eid and attendance_date= :ad"
            c.execute(query, {"eid": user_id, "ad": attendance_date})
            if c.fetchone():
                flash("Attendance Already done For today")
                return redirect(url_for('attendance'))
            else:
                try:
                    insert_query = '''INSERT INTO attendance (Employee_id, attendance_date, 
                                attendance_time, latitude, longitude, Entered_by) VALUES (?, ?, ?, ?, ?, ?)'''
                    c.execute(insert_query, (user_id, attendance_date, attendance_time, latitude, longitude, username))
                    conn.commit()
                    if conn.total_changes > 0:
                        flash('Attendance recorded successfully', 'success')
                        return redirect(url_for('attendance'))
                except Exception as e:
                    flash('Error occurred while doing attendance try again: ' + str(e), 'error')
                    return redirect(url_for('attendance'))
    return render_template('attendance.html')


@app.route('/attendance_history')
@login_required
def attendance_history():
    username = session['user_id']
    today = datetime.date.today()
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        select_query = "SELECT * FROM attendance where employee_id=(select employee_id from users where username= :un)  "
        c.execute(select_query, {"un": username})
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        attendance_records = []
        for row in result:
            ar = dict(zip(columns, row))
            attendance_records.append(ar)
    return render_template('attendancehistory.html', attendance_records=attendance_records)


@app.template_filter('format_time')
def format_time(time_str):
    time = datetime.datetime.strptime(time_str, '%H:%M:%S')
    formatted_time = time.strftime('%I:%M:%S %p')
    return formatted_time


@app.route('/attendance_entry', methods=['GET', 'POST'])
@login_required
def attendance_entry():
    if request.method == 'POST':
        employee_id = request.form.get('employee')
        if employee_id is None:
            employee_id = request.form.get('empid')
        date = request.form.get('date')
        time = datetime.datetime.now()
        formatted_time = time.strftime('%I:%M:%S %p')
        username = session['user_id']
        print(employee_id)
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            select = '''SELECT count(*) FROM Attendance WHERE Employee_id=? and attendance_date=?'''
            c.execute(select, (employee_id, date))
            result = c.fetchone()[0]
            if result > 0:
                flash('Attendance already done for selected date', 'success')
                return redirect(url_for('attendance_entry'))
            else:
                try:
                    print('i am in else')
                    insert_query = '''INSERT INTO attendance (Employee_id, attendance_date, 
                                            attendance_time, Entered_by) VALUES (?, ?, ?, ?)'''
                    c.execute(insert_query, (employee_id, date, formatted_time, username))
                    conn.commit()
                    if conn.total_changes > 0:
                        flash('Attendance recorded successfully', 'success')
                        return redirect(url_for('attendance_entry'))
                except Exception as e:
                    flash('Error recoding attendance: ' + str(e), 'error')
                    return redirect(url_for('attendance_entry'))
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''SELECT * FROM Employees''')
        employees = c.fetchall()
    return render_template('attendanceentry.html', employees=employees)


@app.route('/fetch_employee_name', methods=['GET'])
def fetch_employee_name():
    employee_id = request.args.get('id')
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        query = "SELECT Name FROM employees WHERE id= :id"
        c.execute(query, {"id": employee_id})
        result = c.fetchone()
        c.close()
        if result is not None:
            name = result[0]
            return jsonify(
                {'name': name,})
        else:
            error_message = "Employee ID not found: {}. Please Check employee ID and enter".format(employee_id)
            return jsonify({'error': error_message}), 400


@app.route('/payroll', methods=['GET', 'POST'])
@login_required
def payroll():
    months = [calendar.month_name[i] for i in range(1, 13)]
    if request.method == 'POST':
        year = request.form.get('year')
        month = request.form.get('month')
        with sqlite3.connect(DATABASE) as conn:
            c = conn.cursor()
            query = '''SELECT e.name,e.ID,e.Designation,s.salary, count(*) FROM 
                        Employees e join attendance a on e.ID = a.Employee_ID 
                        JOIN salaryscale s ON e.Designation = s.Designation
                        WHERE strftime('%Y', attendance_date) = ? 
                        AND strftime('%m', attendance_date) = ? AND e.active='1'
                        GROUP BY Employee_id'''
            c.execute(query, (str(year), str(month)))
            result = c.fetchall()
            columns = [desc[0] for desc in c.description]
            data = []
            for row in result:
                ar = dict(zip(columns, row))
                data.append(ar)
            return render_template('payroll.html', data=data, months=months)
    return render_template('payroll.html', months=months)


@app.route('/set_salary', methods=['GET', 'POST'])
@login_required
def set_salary():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''SELECT * FROM Grades''')
        grades = c.fetchall()
        select_query = "SELECT * FROM Designations"
        c.execute(select_query)
        result = c.fetchall()
        select_query = "SELECT * FROM salaryscale"
        c.execute(select_query)
        salary = c.fetchall()
        if request.method == 'POST':
            designation = request.form.get('designation')
            grade_id = request.form.get('grade')
            grade = get_grade(grade_id)
            salary = request.form.get('salary')
            username = session['user_id']
            insert_query = '''INSERT INTO salaryscale (grade, designation, salary, entered_by)
                                values (?, ?, ?, ?)'''
            c.execute(insert_query, (grade, designation, salary, username))
            conn.commit()
            flash('Salary Scale set', 'Success')
            return redirect(url_for('set_salary'))
    return render_template('setsalary.html', grades=grades, designations=result, salaryscale=salary)


@app.route('/edit_salary', methods=['POST'])
@login_required
def edit_salary():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        if request.method == 'POST':
            designation = request.form.get('designation')
            grade_id = request.form.get('grade')
            grade = get_grade(grade_id)
            salary = request.form.get('salary')
            username = session['user_id']
            update_query = "Update Salaryscale set Grade= :r , Description= :d, Updated_by= :u where Id= :i "
            c.execute(update_query, {"r": grade}, {"d": description}, {"u": username}, {"i": id})
            conn.commit()
            flash('Salary Scale Updated', 'Success')
            return redirect(url_for('set_salary'))
    return redirect(url_for('set_salary'))


@app.route('/Delete_salary/<int:id>')
@login_required
def delete_salary(id):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''DELETE FROM Salaryscale where id=?''', (id,))
        conn.commit()
        flash('Salary Data deleted Successfully', 'Success')
        return redirect(url_for('set_salary'))
    return redirect(url_for('set_salary'))


def get_grade(id):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        select_query = "SELECT grade FROM grades WHERE id = :i"
        c.execute(select_query, {"i": id})
        result = c.fetchone()
        if result:
            return result[0]
        else:
            return None


@app.route('/grade', methods=['GET', 'POST'])
@login_required
def grade():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''SELECT * FROM Grades''')
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        grades = []
        for row in result:
            grade = dict(zip(columns, row))
            grades.append(grade)

        if request.method == 'POST':
            grade = request.form.get('grade')
            description = request.form.get('description')
            username = session['user_id']
            insert_query = "INSERT INTO Grades (grade, description, entered_by) values(?, ?, ?)"
            c.execute(insert_query, (grade, description, username))
            conn.commit()
            flash('Grades Added', 'Success')
            return redirect(url_for('grade'))
    return render_template('grade.html', grades=grades)


@app.route('/edit_grade/<id>', methods=['POST', 'GET'])
@login_required
def edit_grade(id):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        if request.method == 'POST':
            grade = request.form.get('grade')
            description = request.form.get('description')
            username = session['user_id']
            update_query = "UPDATE Grades SET Grade = :r, Description = :d, Updated_by = :u WHERE Id = :i"
            c.execute(update_query, {"r": grade, "d": description, "u": username, "i": id})
            conn.commit()
            flash('Grades Updated', 'Success')
            return redirect(url_for('grade'))
    return redirect(url_for('grade'))


@app.route('/Delete_grade/<int:id>')
@login_required
def delete_grade(id):
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''DELETE FROM Grades where id=?''', (id,))
        conn.commit()
        return redirect(url_for('grade'))
    return redirect(url_for('grade'))


@app.route('/tax', methods=['GET', 'POST'])
@login_required
def tax():
    with sqlite3.connect(DATABASE) as conn:
        c = conn.cursor()
        c.execute('''SELECT * FROM Tax ORDER BY Mstatus , Fiscalyear DESC ''')
        result = c.fetchall()
        columns = [desc[0] for desc in c.description]
        taxes = []
        for row in result:
            tax = dict(zip(columns, row))
            taxes.append(tax)
        fyear = fiscalyear()
        if request.method == 'POST':
            parameter = request.form.get('parameter')
            fromrange = request.form.get('fromrange')
            to = request.form.get('torange')
            percent = request.form.get('percent')
            username = session['user_id']
            query = """SELECT from_range, to_range FROM Tax 
                                WHERE Mstatus = ?  AND Fiscalyear = ? """
            existing_tax = c.execute(query, (parameter, fyear))
            if existing_tax:
                for row in existing_tax:
                    if row[0] < int(fromrange) < row[1]:
                        flash('Tax slab for given range or fiscal year is already present', 'success')
                        return redirect(url_for('tax'))
                    if row[0] < int(to) < row[1]:
                        flash('Tax slab for given range or fiscal year is already present', 'success')
                        return redirect(url_for('tax'))
            try:
                insert_query = '''INSERT INTO Tax (Mstatus, From_Range, To_Range, Tax_Percent, Fiscalyear, entered_by) 
                                values(?, ?, ?, ?, ?, ?)'''
                c.execute(insert_query, (parameter, fromrange, to, percent, fyear, username))
                conn.commit()
                if conn.total_changes > 0:
                    flash('Tax Slab Added', 'Success')
                    return redirect(url_for('tax'))
            except Exception as e:
                flash('Error adding Tax slab: ' + str(e), 'error')
                return redirect(url_for('tax'))
    return render_template('tax.html', tax=taxes)


def fiscalyear():
    date = nd.datetime.today()
    date_str = str(date)
    year, month, day = date_str.split('-')
    short_year = year[2:]
    fiscal_year = year
    if int(month) >= 4:
        short_year = int(short_year)+1
        fiscal_year += str(short_year)
    else:
        fiscal_year = str(int(fiscal_year)-1)
        fiscal_year += str(short_year)

    return fiscal_year


if __name__ == '__main__':
    app.run(debug=False)
