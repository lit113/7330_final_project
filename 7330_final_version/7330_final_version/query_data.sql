-- query:get_degree_course
SELECT
    Course.course_id,
    Course.course_name,
    DegreeCourses.is_core
FROM
    DegreeCourses
JOIN
    Course ON DegreeCourses.course_id = Course.course_id
WHERE
    DegreeCourses.name = %s
    AND DegreeCourses.level = %s

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
SELECT *
FROM Section
WHERE course_id = %s
AND (
  (year > %s) OR
  (year = %s AND FIELD(semester, 'Spring', 'Summer', 'Fall', 'Winter') >= FIELD(%s, 'Spring', 'Summer', 'Fall', 'Winter'))
) AND (
  (year < %s) OR
  (year = %s AND FIELD(semester, 'Spring', 'Summer', 'Fall', 'Winter') <= FIELD(%s, 'Spring', 'Summer', 'Fall', 'Winter'))
)
ORDER BY year, FIELD(semester, 'Spring', 'Summer', 'Fall', 'Winter')

-- query:get_instructor_section
SELECT
     i.name,
     c.course_name,
     s.course_id,
     s.section_id,
     s.semester,
     s.year,
     s.enroll_count
FROM Teaches t
JOIN Instructor i ON t.ID = i.ID
JOIN Section s ON t.course_id = s.course_id AND t.section_id = s.section_id AND t.semester = s.semester AND t.year = s.year
JOIN Course c ON s.course_id = c.course_id
WHERE t.ID = %s
     AND s.semester IN (%s, %s, 'Spring', 'Summer', 'Fall', 'Winter')
     AND s.year BETWEEN %s AND %s
ORDER BY s.year, FIELD(s.semester, 'Spring', 'Summer', 'Fall', 'Winter');