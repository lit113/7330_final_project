-- query:insert_degree
INSERT INTO Degree (name, level) VALUES (%s, %s);

-- query:insert_course
INSERT INTO Course (course_id, course_name) VALUES (%s, %s)

-- query:insert_instructor
INSERT INTO Instructor (ID, name) VALUES (%s, %s)

-- query:insert_section
INSERT INTO Section (course_id, section_id, semester, year, enroll_count) VALUES (%s, %s, %s, %s, %s)

-- query:insert_objective
INSERT INTO Objective (code, title, description, course_id) VALUES (%s, %s, %s, %s)

-- query:insert_degree_course
INSERT INTO DegreeCourses (name, level, course_id, is_core) VALUES (%s, %s, %s, %s)

-- query:insert_teaches
INSERT INTO Teaches (ID, course_id, section_id, semester, year) VALUES (%s, %s, %s, %s, %s)