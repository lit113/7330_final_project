import mysql.connector

# connect to the Mysql database
connection = mysql.connector.connect(
  user="root",
  passwd="1234",
  database="7330proj"
)

cursor = connection.cursor()

# create Degree table
cursor.execute("""
CREATE TABLE Degree (
    name VARCHAR(255),
    level VARCHAR(50),
    PRIMARY KEY (name, level)
);
""")

# create Course table
cursor.execute("""
CREATE TABLE Course (
    course_id VARCHAR(255) PRIMARY KEY,
    course_name VARCHAR(255) UNIQUE
);
""")

# create Degree_course table
cursor.execute("""
CREATE TABLE DegreeCourses (
    name VARCHAR(255),
    level VARCHAR(50),
    course_id VARCHAR(255),
    is_core BOOLEAN,
    PRIMARY KEY (name, level, course_id),
    FOREIGN KEY (name, level) REFERENCES Degree(name, level),
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
);
""")

# create Section table
cursor.execute("""
CREATE TABLE Section (
    course_id VARCHAR(255),
    section_id VARCHAR(3),
    semester VARCHAR(50),
    year INT,
    enroll_count INT,
    PRIMARY KEY (course_id, section_id, semester, year),
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
);
""")

# create Instructor table
cursor.execute("""
CREATE TABLE Instructor (
    ID INT PRIMARY KEY,
    name VARCHAR(255)
);
""")

# create Teaches table
cursor.execute("""
CREATE TABLE Teaches (
    ID INT,
    course_id VARCHAR(255),
    section_id VARCHAR(3),
    semester VARCHAR(50),
    year INT,
    PRIMARY KEY (ID, course_id, section_id, semester, year),
    FOREIGN KEY (ID) REFERENCES Instructor(ID),
    FOREIGN KEY (course_id, section_id, semester, year) REFERENCES Section(course_id, section_id, semester, year)
);
""")

# create Objective table
cursor.execute("""
CREATE TABLE Objective (
    code VARCHAR(255),
    course_id VARCHAR(255),
    title VARCHAR(120) UNIQUE,
    description TEXT,
    PRIMARY KEY (code, course_id),
    FOREIGN KEY (course_id) REFERENCES Course(course_id)
);
""")

# create Evaluation table
cursor.execute("""
CREATE TABLE Evaluations (
    course_id VARCHAR(255),
    section_id VARCHAR(3),
    semester VARCHAR(50),
    year INT,
    code VARCHAR(255),
    assessment_method VARCHAR(255),
    instructor_note TEXT,
    A_count INT,
    B_count INT,
    C_count INT,
    F_count INT,
    FOREIGN KEY (course_id, section_id, semester, year) REFERENCES Section(course_id, section_id, semester, year),
    FOREIGN KEY (code) REFERENCES Objective(code),
    PRIMARY KEY (course_id, section_id, semester, year, code)
);
""")

connection.commit()
print("Tables created successfully")
# close connection
cursor.close()
connection.close()
print("MySQL connection is closed")
