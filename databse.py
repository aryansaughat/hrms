import sqlite3
conn = sqlite3.connect('hrms.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS Employees (
             ID INTEGER PRIMARY KEY AUTOINCREMENT,
             Name TEXT NOT NULL,
             Email TEXT NOT NULL UNIQUE,
             Phone TEXT NOT NULL UNIQUE,
             Address TEXT NOT NULL,
             Gender TEXT NOT NULL,
             Father_Name TEXT NOT NULL,
             Mother_Name TEXT NOT NULL,
             Grandfather_Name TEXT NOT NULL,
             Designation TEXT NOT NULL,
             Department TEXT NOT NULL,
             Citizenship_number TEXT NOT NULL,
             Date_Of_Birth TIMESTAMP NOT NULL,
             Joining_Date TIMESTAMP NOT NULL,
             active BOOLEAN,entered_at
             Created_At TIMESTAMP DEFAULT (datetime('now', 'localtime')),
             Created_By TEXT,
             Updated_At TIMESTAMP,
             Updated_By TEXT,
             terminated BOOLEAN,
             termination_date DATE,
             termination_reason TEXT,
             bank_account_number BIGINT,
             PAN_number INTERGER,
             marital_status TEXT,
             profile_image_path TEXT,
             spouse_name TEXT)''')

c.execute('''CREATE TRIGGER IF NOT EXISTS update_employees_Updated_At
             AFTER UPDATE ON employees
             FOR EACH ROW
             BEGIN
             UPDATE employees
             SET Updated_At = datetime('now', 'localtime')
             WHERE id = OLD.id;
             END''')


c.execute('''CREATE TABLE IF NOT EXISTS Leaves (
             ID INTEGER PRIMARY KEY AUTOINCREMENT,
             Employee_ID INTEGER NOT NULL,
             Start_Date TEXT NOT NULL,
             End_Date TEXT NOT NULL,
             Type TEXT NOT NULL,
             Reason TEXT NOT NULL,
             Status TEXT NOT NULL,
             Created_At TIMESTAMP DEFAULT (datetime('now', 'localtime')),
             Created_By TEXT,
             Approved_by TEXT,
             Approved_at TIMESTAMP,
             FOREIGN KEY (Employee_ID) REFERENCES Employee(ID))''')

c.execute('''CREATE TRIGGER IF NOT EXISTS update_Leaves_approved_at
             AFTER Update ON Leaves
             FOR EACH ROW
             BEGIN
             UPDATE Leaves
             SET Approved_at = datetime('now', 'localtime')
             WHERE id = OLD.id;
             END''')

c.execute('''CREATE TABLE IF NOT EXISTS Performances (
             ID INTEGER PRIMARY KEY AUTOINCREMENT,
             Name TEXT NOT NULL,
             Age INTEGER NOT NULL,
             Experience INT NOT NULL,
             Education TEXT NOT NULL,
             Department TEXT NOT NULL,
             Performance TEXT NOT NULL,
             Entered_At TIMESTAMP DEFAULT (datetime('now', 'localtime')),
             Entered_By TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS Qualifications (
             ID INTEGER PRIMARY KEY AUTOINCREMENT,
             Employee_ID INTEGER NOT NULL,
             Level TEXT NOT NULL,
             College_Name TEXT NOT NULL,
             Board TEXT NOT NULL,
             Division TEXT NOT NULL,
             Grade TEXT NOT NULL,
             Entered_At TIMESTAMP DEFAULT (datetime('now', 'localtime')),
             Entered_By TEXT,
             Updated_At TIMESTAMP,
             Updated_By TEXT,
             doc_file_path TEXT,
             FOREIGN KEY (Employee_ID) REFERENCES Employees(ID))''')

c.execute('''CREATE TRIGGER IF NOT EXISTS update_qualifications_Updated_At
             AFTER UPDATE ON qualifications
             FOR EACH ROW
             BEGIN
             UPDATE Qualifications
             SET Updated_At = datetime('now', 'localtime')
             WHERE id = OLD.id;
             END''')


c.execute('''CREATE TABLE IF NOT EXISTS Designations (
             Id INTEGER PRIMARY KEY AUTOINCREMENT,
             Post_Name TEXT NOT NULL,
             Description TEXT NOT NULL,
             Entered_At TIMESTAMP DEFAULT (datetime('now', 'localtime')),
             Entered_By TEXT,
             Updated_At TIMESTAMP,
             Updated_By TEXT)''')

c.execute('''CREATE TRIGGER IF NOT EXISTS update_Designations_Updated_At
             AFTER UPDATE ON Designations
             FOR EACH ROW
             BEGIN
             UPDATE Designations
             SET Updated_At = datetime('now', 'localtime')
             WHERE id = OLD.id;
             END''')


c.execute('''CREATE TABLE IF NOT EXISTS Departments(
             Id INTEGER PRIMARY KEY AUTOINCREMENT,
             Depart_Name TEXT NOT NULL,
             Description TEXT NOT NULL,
             Entered_At TIMESTAMP DEFAULT (datetime('now', 'localtime')),
             Entered_By TEXT,
             Updated_At TIMESTAMP,
             Updated_By TEXT)''')

c.execute('''CREATE TRIGGER IF NOT EXISTS update_Departments_Updated_At
             AFTER UPDATE ON Departments
             FOR EACH ROW
             BEGIN
             UPDATE Departments
             SET Updated_At = datetime('now', 'localtime')
             WHERE id = OLD.id;
             END''')


c.execute('''CREATE TABLE IF NOT EXISTS Users(
             Id INTEGER PRIMARY KEY AUTOINCREMENT,
             Employee_ID INTEGER NOT NULL,
             Name TEXT NOT NULL,
             Username TEXT NOT NULL UNIQUE,
             Password TEXT NOT NULL,
             Email TEXT NOT NULL UNIQUE,
             Phone TEXT NOT NULL UNIQUE,
             Role TEXT NOT NULL,
             Designation TEXT NOT NULL,
             Department TEXT NOT NULL,
             Status TEXT NOT NULL,
             Created_At TIMESTAMP DEFAULT (datetime('now', 'localtime')),
             Created_By TEXT,
             Updated_At TIMESTAMP,
             Updated_By TEXT,
             FOREIGN KEY (Employee_ID) REFERENCES Employee(ID))''')

c.execute('''CREATE TRIGGER IF NOT EXISTS update_Users_Updated_At
             AFTER UPDATE ON Users
             FOR EACH ROW
             BEGIN
             UPDATE Users
             SET Updated_At = datetime('now', 'localtime')
             WHERE id = OLD.id;
             END''')


c.execute('''CREATE TABLE IF NOT EXISTS Roles(
             Id INTEGER PRIMARY KEY AUTOINCREMENT,
             Role_Name TEXT NOT NULL,
             Description TEXT NOT NULL,
             Entered_At TIMESTAMP DEFAULT (datetime('now', 'localtime')),
             Entered_By TEXT,
             Updated_At TIMESTAMP,
             Updated_By TEXT)''')

c.execute('''CREATE TRIGGER IF NOT EXISTS update_Roles_Updated_At
             AFTER UPDATE ON Roles
             FOR EACH ROW
             BEGIN
             UPDATE Roles
             SET Updated_At = datetime('now', 'localtime')
             WHERE id = OLD.id;
             END''')


c.execute('''CREATE TABLE IF NOT EXISTS Modulesassigned(
             Id INTEGER PRIMARY KEY AUTOINCREMENT,
             Role TEXT NOT NULL,
             Description TEXT NOT NULL,
             Entered_At TIMESTAMP DEFAULT (datetime('now', 'localtime')),
             Entered_By TEXT,
             Updated_At TIMESTAMP,
             Updated_By TEXT)''')

c.execute('''CREATE TRIGGER IF NOT EXISTS update_Modulesassigned_Updated_At
             AFTER UPDATE ON Modulesassigned
             FOR EACH ROW
             BEGIN
             UPDATE Modulesassigned
             SET Updated_At = datetime('now', 'localtime')
             WHERE id = OLD.id;
             END''')

c.execute('''CREATE TABLE IF NOT EXISTS Modules(
             Id INTEGER PRIMARY KEY AUTOINCREMENT,
             Module_Name TEXT NOT NULL,
             Description TEXT NOT NULL,
             Entered_At TIMESTAMP DEFAULT (datetime('now', 'localtime')),
             Entered_By TEXT,
             Updated_At TIMESTAMP,
             Updated_By TEXT)''')

c.execute('''CREATE TRIGGER IF NOT EXISTS update_Modules_Updated_At
             AFTER UPDATE ON Modules
             FOR EACH ROW
             BEGIN
             UPDATE Modules
             SET Updated_At = datetime('now', 'localtime')
             WHERE id = OLD.id;
             END''')

c.execute('''CREATE TABLE IF NOT EXISTS Experiences(
             Id INTEGER PRIMARY KEY AUTOINCREMENT,
             Employee_ID INTEGER NOT NULL,
             Company_Name TEXT NOT NULL,
             Duration TEXT NOT NULL,
             Job_Title TEXT NOT NULL,
             Job_Description TEXT NOT NULL,
             Entered_At TIMESTAMP DEFAULT (datetime('now', 'localtime')),
             Entered_By TEXT,
             Updated_At TIMESTAMP,
             Updated_By TEXT,
             doc_file_path TEXT,
             FOREIGN KEY (Employee_ID) REFERENCES Employee(ID))''')

c.execute('''CREATE TRIGGER IF NOT EXISTS update_Experiences_Updated_At
             AFTER UPDATE ON Experiences
             FOR EACH ROW
             BEGIN
             UPDATE Experiences
             SET Updated_At = datetime('now', 'localtime')
             WHERE id = OLD.id;
             END''')


c.execute('''CREATE TABLE IF NOT EXISTS Attendance(
             Id INTEGER PRIMARY KEY AUTOINCREMENT,
             Employee_ID INTEGER NOT NULL,
             Attendance_Date DATE NOT NULL,
             Attendance_Time TIME NOT NULL,
             Latitude FLOAT,
             Longitude FLOAT,
             Entered_At TIMESTAMP DEFAULT (datetime('now', 'localtime')),
             Entered_By TEXT,
             FOREIGN KEY (Employee_ID) REFERENCES Employee(ID))''')


c.execute('''CREATE TABLE IF NOT EXISTS Grades(
             Id INTEGER PRIMARY KEY AUTOINCREMENT,
             Grade TEXT NOT NULL,
             Description TEXT NOT NULL,
             Entered_By TEXT NOT NULL,
             Entered_At TIMESTAMP DEFAULT (datetime('now', 'localtime')),
             Updated_At TIMESTAMP,
             Updated_By TEXT)''')


c.execute('''CREATE TRIGGER IF NOT EXISTS update_grades_Updated_At
             AFTER UPDATE ON grades
             FOR EACH ROW
             BEGIN
             UPDATE grades
             SET Updated_At = datetime('now', 'localtime')
             WHERE id = OLD.id;
             END''')


c.execute('''CREATE TABLE IF NOT EXISTS Salaryscale(
             Id INTEGER PRIMARY KEY AUTOINCREMENT,
             Designation TEXT NOT NULL,
             Grade TEXT NOT NULL,
             Salary BIGINT NOT NULL,
             Entered_By TEXT NOT NULL,
             Entered_At TIMESTAMP DEFAULT (datetime('now', 'localtime')),
             Updated_At TIMESTAMP,
             Updated_By TEXT)''')


c.execute('''CREATE TRIGGER IF NOT EXISTS update_salaryscale_Updated_At
             AFTER UPDATE ON Salaryscale
             FOR EACH ROW
             BEGIN
             UPDATE Salaryscale
             SET Updated_At = datetime('now', 'localtime')
             WHERE id = OLD.id;
             END''')

c.execute('''CREATE TABLE IF NOT EXISTS Tax(
             Id INTEGER PRIMARY KEY AUTOINCREMENT,
             Mstatus TEXT NOT NULL,
             From_Range BIGINT NOT NULL,
             To_Range BIGINT NOT NULL,
             Tax_Percent INT NOT NULL,
             Fiscalyear INT NOT NULL,
             Entered_By TEXT NOT NULL,
             Entered_At TIMESTAMP DEFAULT (datetime('now', 'localtime')),
             Updated_At TIMESTAMP,
             Updated_By TEXT)''')


c.execute('''CREATE TRIGGER IF NOT EXISTS update_salaryscale_Updated_At
             AFTER UPDATE ON Salaryscale
             FOR EACH ROW
             BEGIN
             UPDATE Salaryscale
             SET Updated_At = datetime('now', 'localtime')
             WHERE id = OLD.id;
             END''')

conn.commit()