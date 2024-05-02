-- query:insert_degree
INSERT INTO Degree (name, level) VALUES (%s, %s);

-- query:get_degree_course
SELECT Course.course_id, Course.course_name, DegreeCourses.is_core
FROM DegreeCourses JOIN Course ON DegreeCourses.course_id = Course.course_id
WHERE DegreeCourses.name = %s AND DegreeCourses.level = %s

-- query:get_degree_section
SELECT
    s.course_id,
    c.course_name,
    s.section_id,
    s.semester,
    s.year
FROM
    DegreeCourses dc
JOIN
    Course c ON dc.course_id = c.course_id
JOIN
    Section s ON c.course_id = s.course_id
WHERE
    dc.name = %s
    AND dc.level = %s
    AND (
        (s.year > %s) OR
        (s.year = %s AND CASE s.semester
            WHEN 'Spring' THEN 1
            WHEN 'Summer' THEN 2
            WHEN 'Fall' THEN 3
        END >= %s)
    ) AND (
        (s.year < %s) OR
        (s.year = %s AND CASE s.semester
            WHEN 'Spring' THEN 1
            WHEN 'Summer' THEN 2
            WHEN 'Fall' THEN 3
        END <= %s)
    )
ORDER BY
    s.year,
    CASE s.semester
        WHEN 'Spring' THEN 1
        WHEN 'Summer' THEN 2
        WHEN 'Fall' THEN 3
    END;


-- query:get_degree_objectives
SELECT DISTINCT
    o.code,
    o.title,
    o.description
FROM
    DegreeCourses dc
JOIN
    Course c ON dc.course_id = c.course_id
JOIN
    Objective o ON c.course_id = o.course_id
WHERE
    dc.name = %s
    AND dc.level = %s

-- query:get_degree_objective_course
SELECT
    c.course_id,
    c.course_name,
    o.code,
    o.title,
    o.description
FROM
    DegreeCourses dc
JOIN
    Course c ON dc.course_id = c.course_id
JOIN
    Objective o ON c.course_id = o.course_id
WHERE
    dc.name = %s
    AND dc.level = %s
    AND o.code IN (%s)
ORDER BY
    o.code, c.course_name;

-- query:get_course_section
SELECT course_id, section_id, semester, year
FROM Section
WHERE course_id = ?
  AND (
    (year > ?) OR (year = ? AND semester >= ?)
  )
  AND (
    (year < ?) OR (year = ? AND semester <= ?)
  )
ORDER BY year, semester;


