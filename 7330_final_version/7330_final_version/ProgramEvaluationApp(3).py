import json
import re
from mysql.connector import connect, Error
import tkinter as tk
from tkinter import messagebox, Toplevel, Label, StringVar, ttk, \
    OptionMenu, Button, Entry, Text, Scrollbar, VERTICAL, END, scrolledtext, simpledialog, Checkbutton, IntVar


# load SQL query file
def load_query(file_path, query_name):
    queries = {}
    current_query_name = None
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('-- query:'):
                current_query_name = line.strip().split(':')[1]
                queries[current_query_name] = ''
            elif current_query_name:
                queries[current_query_name] += line
    return queries[query_name].strip()


class ProgramEvaluationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.entries = {}
        self.title("Program Evaluation Application")
        self.geometry("600x400")
        self.center_window(self)

        # status bar
        self.status_bar = tk.Label(self, text="Disconnected", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.db_config = self.load_db_config()
        self.connection = self.connect_to_database()

        if not self.connection:
            messagebox.showerror("Initialization Error",
                                 "Database connection could not be established. The application will close.")
            self.destroy()

        # Main Menu Label
        # in this window, the three buttons correspond to insert basic data, add evaluation and query data respectively
        menu_label = Label(self, text="Program Evaluation Menu", font=("Arial", 16))
        menu_label.pack(pady=10)

        # insert basic information button
        self.insert_basic_btn = Button(self, text="Add Basic Information", command=self.open_insert_basic_window)
        self.insert_basic_btn.pack(pady=10)

        # add evaluation button
        self.insert_evaluation_btn = Button(self, text="Evaluate", command=self.create_evaluation_form)
        self.insert_evaluation_btn.pack(pady=10)

        # retrieval button
        self.retrieval_btn = Button(self, text="Retrieve", command=self.open_retrieval_window)
        self.retrieval_btn.pack(pady=10)

    def get_course_id(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT DISTINCT course_id FROM Course")
            course_ids = [cid[0] for cid in cursor.fetchall()]
            cursor.close()
            return course_ids
        except Error as e:
            messagebox.showerror("Error", f"Error fetching degrees: {e}")
            return []

    def get_instructor_id(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT DISTINCT ID FROM Instructor")
            IDs = [iid[0] for iid in cursor.fetchall()]
            cursor.close()
            return IDs
        except Error as e:
            messagebox.showerror("Error", f"Error fetching degrees: {e}")
            return []

    def get_degree_name(self):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT DISTINCT name FROM Degree")
            degrees = [degree[0] for degree in cursor.fetchall()]
            cursor.close()
            return degrees
        except Error as e:
            messagebox.showerror("Error", f"Error fetching degrees: {e}")
            return []

    def update_degree_levels(self):
        # update levels when you choose a degree
        degree = self.degree_name_var.get()
        try:
            cursor = self.connection.cursor()
            query = "SELECT DISTINCT level FROM Degree WHERE name = %s"
            cursor.execute(query, (degree,))
            levels = [level[0] for level in cursor.fetchall()]
            cursor.close()

            menu = self.degree_level_menu['menu']
            menu.delete(0, 'end')
            for level in levels:
                menu.add_command(label=level, command=lambda value=level: self.degree_level_var.set(value))
            if levels:
                self.degree_level_var.set(levels[0])
        except Error as e:
            messagebox.showerror("Error", f"Error fetching levels: {e}")

    def get_degrees(self):
        # get all degrees name from DC to make a list
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT DISTINCT name FROM DegreeCourses")
            degrees = [degree[0] for degree in cursor.fetchall()]
            cursor.close()
            return degrees
        except Error as e:
            messagebox.showerror("Error", f"Error fetching degrees: {e}")
            return []

    def update_levels(self, *args):
        # update levels when you choose a degree
        degree = self.degree_name_var.get()
        try:
            cursor = self.connection.cursor()
            query = "SELECT DISTINCT level FROM DegreeCourses WHERE name = %s"
            cursor.execute(query, (degree,))
            levels = [level[0] for level in cursor.fetchall()]
            cursor.close()

            menu = self.degree_level_menu['menu']
            menu.delete(0, 'end')
            for level in levels:
                menu.add_command(label=level, command=lambda value=level: self.degree_level_var.set(value))
            if levels:
                self.degree_level_var.set(levels[0])
        except Error as e:
            messagebox.showerror("Error", f"Error fetching levels: {e}")

    def get_objectives(self):
        # get all objectives code to make a list
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT DISTINCT code FROM Objective")
            code = [code[0] for code in cursor.fetchall()]
            cursor.close()
            return code
        except Error as e:
            messagebox.showerror("Error", f"Error fetching degrees: {e}")
            return []

    def open_insert_basic_window(self):
        try:
            self.insert_basic_window = Toplevel(self)
            self.insert_basic_window.title("Insert Basic Info")
            self.insert_basic_window.geometry("600x400")
            self.center_window(self.insert_basic_window)

            #
            degree_form_btn = Button(self.insert_basic_window, text="Add New Degree", command=self.create_degree_form)
            degree_form_btn.pack(pady=5)
            #
            course_form_btn = Button(self.insert_basic_window, text="Add New Course", command=self.create_course_form)
            course_form_btn.pack(pady=5)
            #
            instructor_form_btn = Button(self.insert_basic_window, text="Add New Instructor",
                                         command=self.create_instructor_form)
            instructor_form_btn.pack(pady=5)
            #
            section_form_btn = Button(self.insert_basic_window, text="Add New Section",
                                      command=self.create_section_form)
            section_form_btn.pack(pady=5)
            #
            objective_form_btn = Button(self.insert_basic_window, text="Add New Objective",
                                        command=self.create_objective_form)
            objective_form_btn.pack(pady=5)
            # insert degree_course
            degree_course_form_btn = Button(self.insert_basic_window, text="Associate Course with Degree",
                                            command=self.create_degree_course_form)
            degree_course_form_btn.pack(pady=5)
            # insert teaches
            teaches_form_btn = Button(self.insert_basic_window, text="Associate Instructor with Section",
                                      command=self.create_teaches_form)
            teaches_form_btn.pack(pady=5)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def create_degree_form(self):
        # Create a new window for the degree form
        self.degree_window = Toplevel(self)
        self.degree_window.title("Add New Degree")
        self.degree_window.geometry("600x400")  # Width x Height
        self.center_window(self.degree_window)
        # Name
        Label(self.degree_window, text="Name:").pack()
        self.degree_name_entry = Entry(self.degree_window, width=30)
        self.degree_name_entry.pack()

        # Level
        Label(self.degree_window, text="Degree Level:").pack()
        self.degree_level_var = StringVar(self.degree_window)
        self.degree_level_var.set("Choose Level")  # default value
        self.levels = ['BA', 'BS', 'MS', 'PhD', 'Other']
        self.degree_level_menu = OptionMenu(self.degree_window, self.degree_level_var, *self.levels,
                                            command=self.check_other_option)
        self.degree_level_menu.pack()

        self.custom_level_entry = Entry(self.degree_window)
        self.custom_level_entry.pack()
        self.custom_level_entry.pack_forget()

        # Submit Button
        submit_btn = Button(self.degree_window, text="Submit", command=self.insert_degree)
        submit_btn.pack()

    def check_other_option(self, choice):
        if choice == "Other":
            self.custom_level_entry.pack()
        else:
            self.custom_level_entry.pack_forget()

    def insert_degree(self):
        name = self.degree_name_entry.get()
        level = self.custom_level_entry.get().strip() \
            if self.degree_level_var.get() == "Other" else self.degree_level_var.get()

        if not name:
            messagebox.showerror("Input Error", "Degree name cannot be empty.")
            return
        if not level:
            messagebox.showerror("Input Error", "Degree level cannot be empty.")
            return

        insert_query = load_query("data_entry.sql", "insert_degree")
        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_query, (name, level))
            self.connection.commit()
            cursor.close()
            messagebox.showinfo("Insert", "Successfully inserted the degree.")
            self.degree_window.destroy()  # Close the form window after insertion
        except Error as e:
            messagebox.showerror("Insert", f"Error inserting the degree:\n{e}")

    def create_course_form(self):
        self.course_window = tk.Toplevel(self)
        self.course_window.title("Add New Course")
        self.course_window.geometry("600x400")
        self.center_window(self.course_window)

        # Course ID
        tk.Label(self.course_window, text="Course ID:").grid(row=0, column=0, sticky="e")
        self.course_id_entry = tk.Entry(self.course_window)
        self.course_id_entry.grid(row=0, column=1)

        # Course Name
        tk.Label(self.course_window, text="Course Name:").grid(row=1, column=0, sticky="e")
        self.course_name_entry = tk.Entry(self.course_window)
        self.course_name_entry.grid(row=1, column=1)

        # Submit Button
        submit_btn = tk.Button(self.course_window, text="Submit", command=self.insert_course)
        submit_btn.grid(row=3, column=1)

    def insert_course(self):
        course_id = self.course_id_entry.get()
        course_name = self.course_name_entry.get()

        if not course_name:
            messagebox.showerror("Input Error", "Course name cannot be empty.")
            return
        if not course_id:
            messagebox.showerror("Input Error", "Course ID cannot be empty.")
            return

        # data entry detection
        pattern = re.compile(r'^[A-Za-z]{2,4}\d{4}$')

        if not pattern.match(course_id):
            messagebox.showerror("Invalid Input", "Course ID must be 2-4 letters followed by 4 digits (e.g., CS1234).")
            return

        insert_query = load_query("data_entry.sql", "insert_course")

        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_query, (course_id, course_name))
            self.connection.commit()
            cursor.close()
            messagebox.showinfo("Insert", "Successfully inserted the course.")
            self.course_window.destroy()
        except Error as e:
            messagebox.showerror("Insert", f"Error inserting the course:\n{e}")

    def create_instructor_form(self):
        self.instructor_window = tk.Toplevel(self)
        self.instructor_window.title("Add New Instructor")
        self.instructor_window.geometry("600x400")
        self.center_window(self.instructor_window)

        # Instructor ID
        tk.Label(self.instructor_window, text="Instructor ID:").grid(row=0, column=0, sticky="e")
        self.instructor_id_entry = tk.Entry(self.instructor_window)
        self.instructor_id_entry.grid(row=0, column=1)

        # Instructor Name
        tk.Label(self.instructor_window, text="Instructor Name:").grid(row=1, column=0, sticky="e")
        self.instructor_name_entry = tk.Entry(self.instructor_window)
        self.instructor_name_entry.grid(row=1, column=1)

        # Submit Button
        submit_btn = tk.Button(self.instructor_window, text="Submit", command=self.insert_instructor)
        submit_btn.grid(row=2, column=1)

    def insert_instructor(self):
        instructor_id = self.instructor_id_entry.get()
        instructor_name = self.instructor_name_entry.get()

        if not instructor_name:
            messagebox.showerror("Input Error", "Instructor name cannot be empty.")
            return
        if not instructor_id:
            messagebox.showerror("Input Error", "Instructor ID cannot be empty.")
            return

        insert_query = load_query("data_entry.sql", "insert_instructor")

        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_query, (instructor_id, instructor_name))
            self.connection.commit()
            cursor.close()
            messagebox.showinfo("Insert", "Successfully inserted the instructor.")
            self.instructor_window.destroy()
        except Error as e:
            messagebox.showerror("Insert", f"Error inserting the instructor:\n{e}")

    def create_section_form(self):
        self.section_window = tk.Toplevel(self)
        self.section_window.title("Add New Section")
        self.section_window.geometry("600x400")
        self.center_window(self.section_window)

        # select Course ID
        Label(self.section_window, text="Course ID:").grid(row=0, column=0, sticky="e")
        self.course_id_var = StringVar(self.section_window)
        self.course_id_menu = OptionMenu(self.section_window, self.course_id_var, *self.get_course_id())
        self.course_id_menu.grid(row=0, column=1)

        # Section ID
        tk.Label(self.section_window, text="Section ID:").grid(row=1, column=0, sticky="e")
        self.section_id_entry = tk.Entry(self.section_window)
        self.section_id_entry.grid(row=1, column=1)

        # Semester with OptionMenu
        Label(self.section_window, text="Semester:").grid(row=2, column=0, sticky="e")
        self.semester_var = StringVar(self.section_window)
        self.semester_var.set("Spring")  # default
        self.semester_menu = OptionMenu(self.section_window, self.semester_var, "Spring", "Summer", "Fall")
        self.semester_menu.grid(row=2, column=1)

        # Year
        tk.Label(self.section_window, text="Year:").grid(row=3, column=0, sticky="e")
        self.year_entry = tk.Entry(self.section_window)
        self.year_entry.grid(row=3, column=1)

        # Enrollment Count
        tk.Label(self.section_window, text="Enrollment Count:").grid(row=4, column=0, sticky="e")
        self.enrollment_count_entry = tk.Entry(self.section_window)
        self.enrollment_count_entry.grid(row=4, column=1)

        # Submit Button
        submit_btn = tk.Button(self.section_window, text="Submit", command=self.insert_section)
        submit_btn.grid(row=5, column=1)

    def insert_section(self):
        course_id = self.course_id_var.get()
        section_id = self.section_id_entry.get()
        semester = self.semester_var.get()
        year = self.year_entry.get()
        enrollment_count = self.enrollment_count_entry.get()  # detect negative input

        try:
            enrollment_count = int(enrollment_count)
            if enrollment_count < 0:
                messagebox.showerror("Input Error", "Enrollment count must be a positive number.")
                return
        except ValueError:
            messagebox.showerror("Input Error", "Invalid input for enrollment count; it must be a number.")
            return

        if not section_id:
            messagebox.showerror("Input Error", "Section ID cannot be empty.")
            return
        if not year:
            messagebox.showerror("Input Error", "Year cannot be empty.")
            return

        # input detection
        pattern = re.compile(r'^\d{3}$')

        if not pattern.match(section_id):
            messagebox.showerror("Invalid Input", "Section ID must be exactly 3 digits.")
            return

        insert_query = load_query("data_entry.sql", "insert_section")

        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_query, (course_id, section_id, semester, year, enrollment_count))
            self.connection.commit()
            cursor.close()
            messagebox.showinfo("Insert", "Successfully inserted the section.")
            self.section_window.destroy()
        except Error as e:
            messagebox.showerror("Insert", f"Error inserting the section:\n{e}")

    def create_objective_form(self):
        self.objective_window = tk.Toplevel(self)
        self.objective_window.title("Add New Learning Objective")
        self.objective_window.geometry("600x400")  # Adjusted size for additional field
        self.center_window(self.objective_window)

        # Objective Code
        tk.Label(self.objective_window, text="Objective Code:").grid(row=0, column=0, sticky="e")
        self.objective_code_entry = tk.Entry(self.objective_window)
        self.objective_code_entry.grid(row=0, column=1)

        # Title
        tk.Label(self.objective_window, text="Title:").grid(row=1, column=0, sticky="e")
        self.title_entry = tk.Entry(self.objective_window)
        self.title_entry.grid(row=1, column=1)

        # Description
        tk.Label(self.objective_window, text="Description:").grid(row=2, column=0, sticky="e")
        self.description_entry = tk.Text(self.objective_window, height=5, width=25)
        self.description_entry.grid(row=2, column=1)

        # select Course ID
        Label(self.objective_window, text="Course ID:").grid(row=3, column=0, sticky="e")
        self.course_id_var = StringVar(self.objective_window)
        self.course_id_menu = OptionMenu(self.objective_window, self.course_id_var, *self.get_course_id())
        self.course_id_menu.grid(row=3, column=1)

        # Submit Button
        submit_btn = tk.Button(self.objective_window, text="Submit", command=self.insert_objective)
        submit_btn.grid(row=4, column=1, pady=10)

    def insert_objective(self):
        objective_code = self.objective_code_entry.get()
        title = self.title_entry.get()
        description = self.description_entry.get("1.0", tk.END)
        course_id = self.course_id_var.get()  # Retrieve course ID from the form

        if not objective_code:
            messagebox.showerror("Input Error", "Objective code cannot be empty.")
            return
        if not title:
            messagebox.showerror("Input Error", "Title cannot be empty.")
            return

        insert_query = load_query("data_entry.sql", "insert_objective")

        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_query, (objective_code, title, description, course_id))
            self.connection.commit()
            cursor.close()
            messagebox.showinfo("Insert", "Successfully inserted the learning objective.")
            self.objective_window.destroy()
        except Error as e:
            messagebox.showerror("Insert", f"Error inserting the learning objective:\n{e}")

    # insert other information #
    def create_degree_course_form(self):
        self.degree_course_window = tk.Toplevel(self)
        self.degree_course_window.title("Add Degree-Course Association")
        self.degree_course_window.geometry("600x400")
        self.center_window(self.degree_course_window)

        # select for Degree Name
        Label(self.degree_course_window, text="Degree Name:").grid(row=0, column=0, sticky="e")
        self.degree_name_var = StringVar(self.degree_course_window)
        self.degree_name_menu = OptionMenu(self.degree_course_window, self.degree_name_var, *self.get_degree_name())
        self.degree_name_menu.grid(row=0, column=1)

        # select for Degree Level
        Label(self.degree_course_window, text="Degree Level:").grid(row=1, column=0, sticky="e")
        self.degree_level_var = StringVar(self.degree_course_window)
        self.degree_level_menu = OptionMenu(self.degree_course_window, self.degree_level_var, '')
        self.degree_level_menu.grid(row=1, column=1)
        self.degree_name_var.trace('w', lambda name, index, mode: self.update_degree_levels())


        # select for Course ID
        Label(self.degree_course_window, text="Course ID:").grid(row=2, column=0, sticky="e")
        self.course_id_var = StringVar(self.degree_course_window)
        self.course_id_menu = OptionMenu(self.degree_course_window, self.course_id_var, *self.get_course_id())
        self.course_id_menu.grid(row=2, column=1)

        # Checkbox for Core Course
        self.is_core_var = tk.IntVar()
        core_course_check = tk.Checkbutton(self.degree_course_window, text="Core Course", variable=self.is_core_var)
        core_course_check.grid(row=3, column=1, sticky="w")

        # Button to submit the form
        submit_btn = tk.Button(self.degree_course_window, text="Add Association", command=self.insert_degree_course)
        submit_btn.grid(row=4, column=1, pady=10)

    def insert_degree_course(self):
        degree_name = self.degree_name_var.get()
        degree_level = self.degree_level_var.get()
        course_id = self.course_id_var.get()
        is_core = self.is_core_var.get() == 1  # This will be True if checkbox is checked

        insert_query = load_query("data_entry.sql", "insert_degree_course")

        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_query, (degree_name, degree_level, course_id, is_core))
            self.connection.commit()
            cursor.close()
            messagebox.showinfo("Success", "Degree-Course association added successfully.")
            self.degree_course_window.destroy()
        except Error as e:
            messagebox.showerror("Error", f"Failed to add degree-course association:\n{e}")

    def create_teaches_form(self):
        self.teaches_window = tk.Toplevel(self)
        self.teaches_window.title("Add Teaching Record")
        self.teaches_window.geometry("600x400")
        self.center_window(self.teaches_window)

        # select Instructor ID
        Label(self.teaches_window, text="Instructor ID:").grid(row=0, column=0, sticky="e")
        self.instructor_id_var = StringVar(self.teaches_window)
        self.instructor_id_menu = OptionMenu(self.teaches_window, self.instructor_id_var,
                                             *self.get_instructor_id())
        self.instructor_id_menu.grid(row=0, column=1)

        # select Course ID
        Label(self.teaches_window, text="Course ID:").grid(row=1, column=0, sticky="e")
        self.course_id_var = StringVar(self.teaches_window)
        self.course_id_menu = OptionMenu(self.teaches_window, self.course_id_var,
                                         *self.get_course_id())
        self.course_id_menu.grid(row=1, column=1)

        # entry Section ID
        tk.Label(self.teaches_window, text="Section ID:").grid(row=2, column=0, sticky="e")
        self.section_id_entry = tk.Entry(self.teaches_window)
        self.section_id_entry.grid(row=2, column=1)

        # select Semester
        Label(self.teaches_window, text="Semester:").grid(row=3, column=0, sticky="e")
        self.semester_var = StringVar(self.teaches_window)
        self.semester_var.set("Spring")  # default
        self.semester_menu = OptionMenu(self.teaches_window, self.semester_var, "Spring", "Summer", "Fall")
        self.semester_menu.grid(row=3, column=1)

        # entry Year
        tk.Label(self.teaches_window, text="Year:").grid(row=4, column=0, sticky="e")
        self.year_entry = tk.Entry(self.teaches_window)
        self.year_entry.grid(row=4, column=1)

        # Button to submit the record
        submit_btn = tk.Button(self.teaches_window, text="Add Record", command=self.insert_teaches)
        submit_btn.grid(row=5, column=1, pady=10)

    def insert_teaches(self):
        instructor_id = self.instructor_id_var.get()
        course_id = self.course_id_var.get()
        section_id = self.section_id_entry.get()
        semester = self.semester_var.get()
        year = self.year_entry.get()

        insert_query = load_query("data_entry.sql", "insert_teaches")
        try:
            cursor = self.connection.cursor()
            cursor.execute(insert_query, (instructor_id, course_id, section_id, semester, year))
            self.connection.commit()
            cursor.close()
            messagebox.showinfo("Success", "Teaching record added successfully.")
            self.teaches_window.destroy()
        except Error as e:
            messagebox.showerror("Error", f"Failed to add teaching record:\n{e}")

    # ------- Evaluation ------- #
    def create_evaluation_form(self):
        self.evaluation_entry_window = tk.Toplevel(self)
        self.evaluation_entry_window.title("Evaluation Entry")
        self.evaluation_entry_window.geometry("600x400")
        self.center_window(self.evaluation_entry_window)

        # Entry for Year
        tk.Label(self.evaluation_entry_window, text="Year:").grid(row=0, column=0, sticky="e")
        self.evaluation_year_entry = tk.Entry(self.evaluation_entry_window)
        self.evaluation_year_entry.grid(row=0, column=1)

        # Entry for Semester
        tk.Label(self.evaluation_entry_window, text="Semester:").grid(row=1, column=0, sticky="e")
        self.evaluation_semester_entry = tk.Entry(self.evaluation_entry_window)
        self.evaluation_semester_entry.grid(row=1, column=1)

        # Entry for Instructor ID
        tk.Label(self.evaluation_entry_window, text="Instructor ID:").grid(row=2, column=0, sticky="e")
        self.evaluation_instructor_id_entry = tk.Entry(self.evaluation_entry_window)
        self.evaluation_instructor_id_entry.grid(row=2, column=1)

        # Button to List Sections for the given Year and Semester
        list_sections_btn = tk.Button(self.evaluation_entry_window, text="List Sections", command=self.list_sections)
        list_sections_btn.grid(row=3, column=1, pady=10)

    def list_sections(self):
        year = self.evaluation_year_entry.get()
        semester = self.evaluation_semester_entry.get()
        instructor_id = self.evaluation_instructor_id_entry.get()

        # Query to retrieve the sections taught by the instructor
        query = """
        SELECT Section.course_id, Section.section_id
        FROM Teaches
        INNER JOIN Section ON Teaches.course_id = Section.course_id
          AND Teaches.section_id = Section.section_id
          AND Teaches.semester = Section.semester
          AND Teaches.year = Section.year
        WHERE Teaches.ID = %s AND Teaches.semester = %s AND Teaches.year = %s
        """

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, (instructor_id, semester, year))
            sections = cursor.fetchall()

            if not sections:  # If no sections are found
                tk.Label(self.evaluation_entry_window, text="No results found").grid(row=4, column=0, sticky="w")
                return

            row_offset = 4  # Start displaying sections from row 4
            for course_id, section_id in sections:
                # Fetch evaluation data
                eval_query = """
                SELECT assessment_method, instructor_note, A_count, B_count, C_count, F_count
                FROM Evaluations
                WHERE section_id = %s AND course_id = %s AND semester = %s AND year = %s
                """
                cursor.execute(eval_query, (section_id, course_id, semester, year))
                evaluation_data = cursor.fetchone()

                # Label for course and section identifier
                tk.Label(self.evaluation_entry_window, text=f"Course {course_id}, Section {section_id}").grid(
                    row=row_offset, column=0, columnspan=2, sticky="w")
                row_offset += 1  # Increment row offset for details

                # Display evaluation status vertically
                if evaluation_data:
                    for i, attr in enumerate(
                            ["Assessment method", "Instructor note", "A count", "B count", "C count", "F count"]):
                        status = "entered" if evaluation_data[i] is not None else "not entered"
                        tk.Label(self.evaluation_entry_window, text=f"{attr}: {status}").grid(row=row_offset + i,
                                                                                              column=0, sticky="w")
                    row_offset += 6  # Increment for next section's start after 6 attributes
                else:
                    tk.Label(self.evaluation_entry_window, text="Evaluation not entered").grid(row=row_offset, column=0,
                                                                                               sticky="w")
                    row_offset += 1  # Increment for next section's start

                # Button to edit or enter evaluations
                edit_btn_text = "Edit Evaluation" if evaluation_data else "Enter Evaluation"
                edit_btn = Button(self.evaluation_entry_window, text=edit_btn_text,
                                  command=lambda c_id=course_id, s_id=section_id, yr=year, sem=semester:
                                  self.enter_or_edit_evaluation(c_id, s_id, yr, sem))
                edit_btn.grid(row=row_offset, column=0, sticky="ew")
                row_offset += 1  # Prepare for next section's button

            cursor.close()
        except Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    # def enter_or_edit_evaluation(self, course_id, section_id, year, semester):
    #     self.evaluation_edit_window = tk.Toplevel(self)
    #     self.evaluation_edit_window.title("Enter/Edit Evaluation")
    #     self.center_window(self.evaluation_edit_window)
    #     self.evaluation_edit_window.geometry('600x400')
    #
    #     # Fetch code from Objective table based on course_id
    #     code_query = "SELECT code FROM Objective WHERE course_id = %s"
    #     cursor = self.connection.cursor()
    #     cursor.execute(code_query, (course_id,))
    #     code_result = cursor.fetchone()
    #     code = code_result[0] if code_result else None
    #
    #     # Fetch existing evaluation data if any
    #     eval_query = """
    #     SELECT assessment_method, instructor_note, A_count, B_count, C_count, F_count
    #     FROM Evaluations
    #     WHERE course_id = %s AND section_id = %s AND year = %s AND semester = %s AND code = %s
    #     """
    #     cursor.execute(eval_query, (course_id, section_id, year, semester, code))
    #     evaluation_data = cursor.fetchone()
    #
    #     labels = ["Assessment Method", "Instructor Note", "A Count", "B Count", "C Count", "F Count"]
    #     row = 0
    #
    #     for i, label in enumerate(labels):
    #         tk.Label(self.evaluation_edit_window, text=f"{label}:").grid(row=row, column=0, sticky="e")
    #         entry = Text(self.evaluation_edit_window, height=4, width=40) if "Note" in label else tk.Entry(
    #             self.evaluation_edit_window)
    #         entry.grid(row=row, column=1)
    #         if evaluation_data and evaluation_data[i] is not None:
    #             entry.insert(END if "Note" in label else 0, str(evaluation_data[i]))
    #         self.entries[label] = entry
    #         row += 1
    #
    #     submit_button = tk.Button(self.evaluation_edit_window, text="Submit",
    #                               command=lambda: self.save_evaluation(
    #                                   course_id, section_id, semester, year, code,
    #                                   self.entries["Assessment Method"].get(),
    #                                   self.entries["Instructor Note"].get("1.0", tk.END).strip(),
    #                                   self.entries["A Count"].get(),
    #                                   self.entries["B Count"].get(),
    #                                   self.entries["C Count"].get(),
    #                                   self.entries["F Count"].get(),
    #                                   bool(evaluation_data)
    #                               ))
    #     submit_button.grid(row=row + 1, column=1, pady=10)
    #
    #     cursor.close()
    #
    # def save_evaluation(self, course_id, section_id, semester, year, code, assessment_method, instructor_note, a_count,
    #                     b_count, c_count, f_count, is_update):
    #     try:
    #         cursor = self.connection.cursor()
    #         if is_update:
    #             update_query = """
    #             UPDATE Evaluations
    #             SET assessment_method = %s, instructor_note = %s, A_count = %s, B_count = %s, C_count = %s, F_count = %s, code = %s
    #             WHERE course_id = %s AND section_id = %s AND semester = %s AND year = %s
    #             """
    #             cursor.execute(update_query, (
    #                 assessment_method, instructor_note, a_count, b_count, c_count, f_count, code, course_id, section_id,
    #                 semester, year))
    #         else:
    #             insert_query = """
    #             INSERT INTO Evaluations (course_id, section_id, semester, year, code, assessment_method, instructor_note, A_count, B_count, C_count, F_count)
    #             VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    #             """
    #             cursor.execute(insert_query, (
    #                 course_id, section_id, semester, year, code, assessment_method, instructor_note, a_count, b_count,
    #                 c_count, f_count))
    #
    #         self.connection.commit()
    #         messagebox.showinfo("Success", "Evaluation data saved successfully.")
    #     except Exception as e:
    #         messagebox.showerror("Error", f"Failed to save evaluation data: {e}")
    #     finally:
    #         cursor.close()
    #         self.evaluation_edit_window.destroy()

    def enter_or_edit_evaluation(self, course_id, section_id, year, semester):
        self.evaluation_edit_window = tk.Toplevel(self)
        self.evaluation_edit_window.title("Enter/Edit Evaluation")
        self.center_window(self.evaluation_edit_window)
        self.evaluation_edit_window.geometry('600x400')

        cursor = self.connection.cursor()

        # Fetch enrollment count from Section table
        enrollment_query = "SELECT enroll_count FROM Section WHERE course_id = %s AND section_id = %s AND year = %s AND semester = %s"
        cursor.execute(enrollment_query, (course_id, section_id, year, semester))
        enrollment_result = cursor.fetchone()
        enrollment_count = enrollment_result[0] if enrollment_result else 0

        # Fetch code from Objective table based on course_id
        code_query = "SELECT code FROM Objective WHERE course_id = %s"
        cursor.execute(code_query, (course_id,))
        code_result = cursor.fetchone()
        code = code_result[0] if code_result else None

        # Fetch existing evaluation data if any
        eval_query = """
        SELECT assessment_method, instructor_note, A_count, B_count, C_count, F_count
        FROM Evaluations
        WHERE course_id = %s AND section_id = %s AND year = %s AND semester = %s AND code = %s
        """
        cursor.execute(eval_query, (course_id, section_id, year, semester, code))
        evaluation_data = cursor.fetchone()

        labels = ["Assessment Method", "Instructor Note", "A Count", "B Count", "C Count", "F Count"]
        row = 0

        for i, label in enumerate(labels):
            tk.Label(self.evaluation_edit_window, text=f"{label}:").grid(row=row, column=0, sticky="e")
            entry = Text(self.evaluation_edit_window, height=4, width=40) if "Note" in label else tk.Entry(
                self.evaluation_edit_window)
            entry.grid(row=row, column=1)
            if evaluation_data and evaluation_data[i] is not None:
                entry.insert(END if "Note" in label else 0, str(evaluation_data[i]))
            self.entries[label] = entry
            row += 1

        submit_button = tk.Button(self.evaluation_edit_window, text="Submit",
                                  command=lambda: self.save_evaluation(
                                      course_id, section_id, semester, year, code,
                                      self.entries["Assessment Method"].get(),
                                      self.entries["Instructor Note"].get("1.0", tk.END).strip(),
                                      self.entries["A Count"].get(),
                                      self.entries["B Count"].get(),
                                      self.entries["C Count"].get(),
                                      self.entries["F Count"].get(),
                                      bool(evaluation_data),
                                      enrollment_count
                                  ))
        submit_button.grid(row=row + 1, column=1, pady=10)

        cursor.close()

    def save_evaluation(self, course_id, section_id, semester, year, code, assessment_method, instructor_note, a_count,
                        b_count, c_count, f_count, is_update, enrollment_count):
        try:
            a_count = int(a_count or 0)
            b_count = int(b_count or 0)
            c_count = int(c_count or 0)
            f_count = int(f_count or 0)
            total_count = a_count + b_count + c_count + f_count

            if total_count > enrollment_count:
                messagebox.showerror("Validation Error",
                                     "The total count of grades exceeds the number of enrolled students.")
                return

            cursor = self.connection.cursor()
            if is_update:
                update_query = """
                UPDATE Evaluations
                SET assessment_method = %s, instructor_note = %s, A_count = %s, B_count = %s, C_count = %s, F_count = %s, code = %s
                WHERE course_id = %s AND section_id = %s AND semester = %s AND year = %s
                """
                cursor.execute(update_query, (
                    assessment_method, instructor_note, a_count, b_count, c_count, f_count, code, course_id, section_id,
                    semester, year))
            else:
                insert_query = """
                INSERT INTO Evaluations (course_id, section_id, semester, year, code, assessment_method, instructor_note, A_count, B_count, C_count, F_count)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (
                    course_id, section_id, semester, year, code, assessment_method, instructor_note, a_count, b_count,
                    c_count, f_count))

            self.connection.commit()
            messagebox.showinfo("Success", "Evaluation data saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save evaluation data: {e}")
        finally:
            cursor.close()
            self.evaluation_edit_window.destroy()

    # ------- QUERY DATA ------- #
    # including Given a degree, Given a course, Given an instructor and Queries involving evaluations

    def open_retrieval_window(self):
        self.retrieval_window = Toplevel(self)
        self.retrieval_window.title("Retrieval")
        self.retrieval_window.geometry("600x400")
        self.center_window(self.retrieval_window)

        # Give a degree, list all the courses
        degree_course_btn = Button(self.retrieval_window, text="Get Degree Course", command=self.degree_course_form)
        degree_course_btn.pack(pady=5)

        # Give a degree, list all the sections (time range)
        degree_section_btn = Button(self.retrieval_window, text="Get Degree Section",
                                    command=self.degree_section_form)
        degree_section_btn.pack(pady=5)

        # Give a degree, list all the objectives
        degree_objective_btn = Button(self.retrieval_window, text="Get Degree Objective",
                                      command=self.degree_objective_form)
        degree_objective_btn.pack(pady=5)

        # Give a degree and objective, list all the courses
        degree_obj_course_btn = Button(self.retrieval_window, text="Get Degree Courses Associate Objective",
                                       command=self.degree_obj_course_form)
        degree_obj_course_btn.pack(pady=5)

        # Give a course
        course_section_btn = Button(self.retrieval_window, text="Get Course Section",
                                    command=self.course_section_form)
        course_section_btn.pack(pady=5)

        # Give an instructor
        instructor_section_btn = Button(self.retrieval_window, text="Get Instructor Section",
                                        command=self.instructor_section)
        instructor_section_btn.pack(pady=5)

        get_evaluation_btn = Button(self.retrieval_window, text="Get Evaluation",
                                    command=self.check_evaluation_window)
        get_evaluation_btn.pack(pady=5)

        get_percentage_btn = Button(self.retrieval_window, text="Get Percentage",
                                    command=self.check_percentage_window)
        get_percentage_btn.pack(pady=5)

        # Queries involving evaluations

    def degree_course_form(self):
        # create new window
        self.degree_course_window = Toplevel(self)
        self.degree_course_window.title("Query Courses by Degree")
        self.degree_course_window.geometry("600x400")
        self.center_window(self.degree_course_window)

        # select degree name
        Label(self.degree_course_window, text="Degree Name:").pack()
        self.degree_name_var = StringVar(self.degree_course_window)
        self.degree_name_menu = OptionMenu(self.degree_course_window, self.degree_name_var, *self.get_degrees())
        self.degree_name_menu.pack()

        # select degree level
        Label(self.degree_course_window, text="Degree Level:").pack()
        self.degree_level_var = StringVar(self.degree_course_window)
        self.degree_level_menu = OptionMenu(self.degree_course_window, self.degree_level_var, '')
        self.degree_level_menu.pack()
        self.degree_name_var.trace('w', self.update_levels)

        # submit button
        submit_btn = Button(self.degree_course_window, text="Submit", command=self.get_degree_course)
        submit_btn.pack(pady=10)

        # text area
        self.results_text = Text(self.degree_course_window, height=10, width=50)
        self.results_text.pack(pady=10)
        scroll = Scrollbar(self.degree_course_window, command=self.results_text.yview, orient=VERTICAL)
        scroll.pack(side='right', fill='y')
        self.results_text.configure(yscrollcommand=scroll.set)

    def get_degree_course(self):
        name = self.degree_name_var.get()
        level = self.degree_level_var.get()

        # input empty detection
        if not name:
            messagebox.showerror("Input Error", "Degree name cannot be empty.")
            return
        if not level:
            messagebox.showerror("Input Error", "Degree level cannot be empty.")
            return

        try:
            query = load_query("query_data.sql", "get_degree_course")
            cursor = self.connection.cursor()
            cursor.execute(query, (name, level))
            rows = cursor.fetchall()
            cursor.close()
            self.results_text.delete('1.0', END)
            if rows:
                for row in rows:
                    course_type = "Core Course" if row[2] else "Elective Course"
                    self.results_text.insert(END, f"Course ID: {row[0]}, Course Name: {row[1]}, Type: {course_type}\n")
            else:
                self.results_text.insert(END, "No courses found for this degree.\n")
        except Error as e:
            messagebox.showerror("Query Error", f"Failed to execute query:\n{e}")

    def degree_section_form(self):
        self.degree_section_window = Toplevel(self)
        self.degree_section_window.title("Query Section by Degree")
        self.degree_section_window.geometry("600x400")
        self.center_window(self.degree_section_window)

        # select degree name
        Label(self.degree_section_window, text="Degree Name:").pack()
        self.degree_name_var = StringVar(self.degree_section_window)
        self.degree_name_menu = OptionMenu(self.degree_section_window, self.degree_name_var, *self.get_degrees())
        self.degree_name_menu.pack()

        # select degree level
        Label(self.degree_section_window, text="Degree Level:").pack()
        self.degree_level_var = StringVar(self.degree_section_window)
        self.degree_level_menu = OptionMenu(self.degree_section_window, self.degree_level_var, '')
        self.degree_level_menu.pack()
        self.degree_name_var.trace('w', self.update_levels)

        # entry start year
        Label(self.degree_section_window, text="Start Year:").pack()
        self.degree_start_year_entry = Entry(self.degree_section_window)
        self.degree_start_year_entry.pack()

        # select start semester
        Label(self.degree_section_window, text="Semester:").pack()
        self.degree_start_sem_var = StringVar(self.degree_section_window)
        self.degree_start_sem_var.set("Choose Semester")  # default value
        self.semesters = ['Spring', 'Summer', 'Fall']
        self.degree_start_sem_menu = OptionMenu(self.degree_section_window, self.degree_start_sem_var, *self.semesters)
        self.degree_start_sem_menu.pack()

        # entry end year
        Label(self.degree_section_window, text="End Year:").pack()
        self.degree_end_year_entry = Entry(self.degree_section_window)
        self.degree_end_year_entry.pack()

        # select end semester
        Label(self.degree_section_window, text="Semester:").pack()
        self.degree_end_sem_var = StringVar(self.degree_section_window)
        self.degree_end_sem_var.set("Choose Semester")  # default value
        self.degree_end_sem_menu = OptionMenu(self.degree_section_window, self.degree_end_sem_var, *self.semesters)
        self.degree_end_sem_menu.pack()

        # submit button
        submit_btn = Button(self.degree_section_window, text="Submit", command=self.get_degree_section)
        submit_btn.pack(pady=10)

        # text area
        self.results_text = Text(self.degree_section_window, height=10, width=50)
        self.results_text.pack(pady=10)
        scroll = Scrollbar(self.degree_section_window, command=self.results_text.yview, orient=VERTICAL)
        scroll.pack(side='right', fill='y')
        self.results_text.configure(yscrollcommand=scroll.set)

    def get_degree_section(self):
        name = self.degree_name_var.get()
        level = self.degree_level_var.get()
        start_year = self.degree_start_year_entry.get()
        start_sem = self.degree_start_sem_var.get()
        end_year = self.degree_end_year_entry.get()
        end_sem = self.degree_end_sem_var.get()

        # input empty detection
        if not name:
            messagebox.showerror("Input Error", "Degree name cannot be empty.")
            return
        if not level:
            messagebox.showerror("Input Error", "Degree level cannot be empty.")
            return

        try:
            semester_to_number = {'Spring': 1, 'Summer': 2, 'Fall': 3}
            start_sem_num = semester_to_number[start_sem]
            end_sem_num = semester_to_number[end_sem]
            query = load_query("query_data.sql", "get_degree_section")
            cursor = self.connection.cursor()
            cursor.execute(query, (name, level, start_year, start_year, start_sem_num, end_year, end_year, end_sem_num))
            rows = cursor.fetchall()
            cursor.close()
            self.results_text.delete('1.0', END)
            if rows:
                for row in rows:
                    self.results_text.insert(END, f"Course ID: {row[0]}, Course Name: {row[1]}, "
                                             f"Section ID: {row[2]}, Semester: {row[3]}, Year: {row[4]}\n")
            else:
                self.results_text.insert(END, "No section found for this degree.\n")
        except Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def degree_objective_form(self):
        # create new window
        self.degree_objective_window = Toplevel(self)
        self.degree_objective_window.title("Query objective by Degree")
        self.degree_objective_window.geometry("600x400")
        self.center_window(self.degree_objective_window)

        # select degree name
        Label(self.degree_objective_window, text="Degree Name:").pack()
        self.degree_name_var = StringVar(self.degree_objective_window)
        self.degree_name_menu = OptionMenu(self.degree_objective_window, self.degree_name_var, *self.get_degrees())
        self.degree_name_menu.pack()

        # select degree level
        Label(self.degree_objective_window, text="Degree Level:").pack()
        self.degree_level_var = StringVar(self.degree_objective_window)
        self.degree_level_menu = OptionMenu(self.degree_objective_window, self.degree_level_var, '')
        self.degree_level_menu.pack()
        self.degree_name_var.trace('w', self.update_levels)

        # select objective
        # Label(self.degree_objective_window, text="Objective:").pack()
        # self.degree_objective_var = StringVar(self.degree_objective_window)
        # self.degree_objective_menu = OptionMenu(self.degree_objective_window, self.degree_name_var,
        #                                         *self.get_objectives())
        # self.degree_objective_menu.pack()

        # submit button
        submit_btn = Button(self.degree_objective_window, text="Submit", command=self.get_degree_objective)
        submit_btn.pack(pady=10)

        # text area
        self.results_text = Text(self.degree_objective_window, height=10, width=50)
        self.results_text.pack(pady=10)
        scroll = Scrollbar(self.degree_objective_window, command=self.results_text.yview, orient=VERTICAL)
        scroll.pack(side='right', fill='y')
        self.results_text.configure(yscrollcommand=scroll.set)

    def get_degree_objective(self):
        name = self.degree_name_var.get()
        level = self.degree_level_var.get()

        # input empty detection
        if not name:
            messagebox.showerror("Input Error", "Degree name cannot be empty.")
            return
        if not level:
            messagebox.showerror("Input Error", "Degree level cannot be empty.")
            return

        try:
            query = load_query("query_data.sql", "get_degree_objectives")
            cursor = self.connection.cursor()
            cursor.execute(query, (name, level))
            rows = cursor.fetchall()
            cursor.close()
            self.results_text.delete('1.0', END)
            if rows:
                for row in rows:
                    self.results_text.insert(END, f"Objective CODE: {row[0]}, Title: {row[1]}, Description: {row[2]}\n")
            else:
                self.results_text.insert(END, "No objective found for this degree.\n")
        except Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def degree_obj_course_form(self):
        # create new window
        self.degree_obj_course_window = Toplevel(self)
        self.degree_obj_course_window.title("Query courses by Degree and objective")
        self.degree_obj_course_window.geometry("600x400")
        self.center_window(self.degree_obj_course_window)

        # select degree name
        Label(self.degree_obj_course_window, text="Degree Name:").pack()
        self.degree_name_var = StringVar(self.degree_obj_course_window)
        self.degree_name_menu = OptionMenu(self.degree_obj_course_window, self.degree_name_var, *self.get_degrees())
        self.degree_name_menu.pack()

        # select degree level
        Label(self.degree_obj_course_window, text="Degree Level:").pack()
        self.degree_level_var = StringVar(self.degree_obj_course_window)
        self.degree_level_menu = OptionMenu(self.degree_obj_course_window, self.degree_level_var, '')
        self.degree_level_menu.pack()
        self.degree_name_var.trace('w', self.update_levels)

        # select objective code
        Label(self.degree_obj_course_window, text="Objective:").pack()
        self.objective_code_var = StringVar(self.degree_obj_course_window)
        self.objective_code_menu = OptionMenu(self.degree_obj_course_window,
                                              self.objective_code_var, *self.get_objectives())
        self.objective_code_menu.pack()

        # submit button
        submit_btn = Button(self.degree_obj_course_window, text="Submit", command=self.get_degree_objective_course)
        submit_btn.pack(pady=10)

        # text area
        self.results_text = Text(self.degree_obj_course_window, height=10, width=50)
        self.results_text.pack(pady=10)
        scroll = Scrollbar(self.degree_obj_course_window, command=self.results_text.yview, orient=VERTICAL)
        scroll.pack(side='right', fill='y')
        self.results_text.configure(yscrollcommand=scroll.set)

    def get_degree_objective_course(self):
        name = self.degree_name_var.get()
        level = self.degree_level_var.get()
        code = self.objective_code_var.get()

        # input empty detection
        if not name:
            messagebox.showerror("Input Error", "Degree name cannot be empty.")
            return
        if not level:
            messagebox.showerror("Input Error", "Degree level cannot be empty.")
            return

        try:
            query = load_query("test.sql", "get_degree_objective_course")
            cursor = self.connection.cursor()
            cursor.execute(query, (name, level, code))
            rows = cursor.fetchall()
            cursor.close()
            self.results_text.delete('1.0', END)
            if rows:
                for row in rows:
                    self.results_text.insert(END, f"Course ID: {row[0]}, Course Name: {row[1]}, "
                                             f"Code: {row[2]}, Title: {row[3]}, Description: {row[4]}\n")
            else:
                self.results_text.insert(END, "No course found for this objective.\n")

        except Error as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def course_section_form(self):
        # create new window
        self.course_section_window = Toplevel(self)
        self.course_section_window.title("Query Section by Course")
        self.course_section_window.geometry("600x600")
        self.center_window(self.course_section_window)

        self.course_id_label = Label(self.course_section_window, text="Course ID:")
        self.course_id_label.pack(pady=5)
        self.course_id_entry = tk.Entry(self.course_section_window)
        self.course_id_entry.pack(pady=5)

        semesters = ['Spring', 'Summer', 'Fall']  # List of semesters for the dropdown

        self.start_semester_label = Label(self.course_section_window, text="Start Semester:")
        self.start_semester_label.pack(pady=5)
        self.start_semester_entry = ttk.Combobox(self.course_section_window, values=semesters, state='readonly')
        self.start_semester_entry.pack(pady=5)

        self.start_year_label = Label(self.course_section_window, text="Start Year:")
        self.start_year_label.pack(pady=5)
        self.start_year_entry = tk.Entry(self.course_section_window)
        self.start_year_entry.pack(pady=5)

        self.end_semester_label = tk.Label(self.course_section_window, text="End Semester:")
        self.end_semester_label.pack(pady=5)
        self.end_semester_entry = ttk.Combobox(self.course_section_window, values=semesters, state='readonly')
        self.end_semester_entry.pack(pady=5)

        self.end_year_label = tk.Label(self.course_section_window, text="End Year:")
        self.end_year_label.pack(pady=5)
        self.end_year_entry = tk.Entry(self.course_section_window)
        self.end_year_entry.pack(pady=5)

        self.query_button = tk.Button(self.course_section_window, text="Query Sections", command=self.perform_query)
        self.query_button.pack(pady=10)

        self.text_area = scrolledtext.ScrolledText(self.course_section_window, width=60, height=10)
        self.text_area.pack(pady=10)

    def perform_query(self):
        course_id = self.course_id_entry.get()
        start_semester = self.start_semester_entry.get()
        start_year = self.start_year_entry.get()
        end_semester = self.end_semester_entry.get()
        end_year = self.end_year_entry.get()

        try:
            start_year = int(start_year)  # Convert year to integer
            end_year = int(end_year)  # Convert year to integer
        except ValueError:
            self.text_area.insert(tk.END, "Please enter valid integers for the years.\n")
            return

        results = self.query_sections(course_id, start_semester, start_year, end_semester, end_year)

        self.text_area.delete('1.0', tk.END)
        for result in results:
            self.text_area.insert(tk.END, f'Section ID: {result[1]}, Semester: {result[2]}, '
                                          f'Year: {result[3]}, Enroll Count: {result[4]}\n')

    def query_sections(self, course_id, start_semester, start_year, end_semester, end_year):
        try:
            with self.connection.cursor() as cursor:
                query = load_query("query_data.sql", "get_course_section")
                cursor.execute(query,
                               (course_id, start_year, start_year, start_semester, end_year, end_year, end_semester))
                results = cursor.fetchall()
                return results
        except Exception as e:
            self.text_area.insert(tk.END, f"An error occurred: {e}\n")
            return []

    def instructor_section(self):
        # create new window
        self.instructor_section_window = Toplevel(self)
        self.instructor_section_window.title("Query Section by Instructor")
        self.instructor_section_window.geometry("600x600")
        self.center_window(self.instructor_section_window)

        self.instructor_label = tk.Label(self.instructor_section_window, text="Instructor ID:")
        self.instructor_label.pack(pady=5)
        self.instructor_entry = tk.Entry(self.instructor_section_window)
        self.instructor_entry.pack(pady=5)

        self.start_semester_label = tk.Label(self.instructor_section_window, text="Start Semester:")
        self.start_semester_label.pack(pady=5)
        self.start_semester_entry = ttk.Combobox(self.instructor_section_window,
                                                 values=["Spring", "Summer", "Fall"])
        self.start_semester_entry.pack(pady=5)

        self.end_semester_label = tk.Label(self.instructor_section_window, text="End Semester:")
        self.end_semester_label.pack(pady=5)
        self.end_semester_entry = ttk.Combobox(self.instructor_section_window,
                                               values=["Spring", "Summer", "Fall"])
        self.end_semester_entry.pack(pady=5)

        self.start_year_label = tk.Label(self.instructor_section_window, text="Start Year:")
        self.start_year_label.pack(pady=5)
        self.start_year_entry = tk.Entry(self.instructor_section_window)
        self.start_year_entry.pack(pady=5)

        self.end_year_label = tk.Label(self.instructor_section_window, text="End Year:")
        self.end_year_label.pack(pady=5)
        self.end_year_entry = tk.Entry(self.instructor_section_window)
        self.end_year_entry.pack(pady=5)

        self.query_button = tk.Button(self.instructor_section_window, text="Query Sections",
                                      command=self.perform_query2)
        self.query_button.pack(pady=10)

        self.text_area = scrolledtext.ScrolledText(self.instructor_section_window, width=60, height=10)
        self.text_area.pack(pady=10)

    def query_sections2(self, instructor_id, start_semester, end_semester, start_year, end_year):
        if self.connection:
            try:
                with self.connection.cursor() as cursor:
                    query = load_query("query_data.sql", "get_instructor_section")
                    # Add semesters explicitly
                    semesters = ['Spring', 'Summer', 'Fall']
                    start_index = semesters.index(start_semester)
                    end_index = semesters.index(end_semester)

                    if start_index <= end_index:
                        semester_range = semesters[start_index:end_index + 1]
                    else:
                        semester_range = semesters[start_index:] + semesters[:end_index + 1]

                    cursor.execute(query, (instructor_id, semester_range[0], semester_range[-1], start_year, end_year))
                    return cursor.fetchall()
            except Exception as e:
                self.text_area.insert(tk.END, f"An error occurred: {e}\n")
                return []

    def perform_query2(self):
        """ Gather inputs and call the query_sections function to display results. """
        instructor_id = self.instructor_entry.get()
        start_semester = self.start_semester_entry.get()
        end_semester = self.end_semester_entry.get()
        start_year = self.start_year_entry.get()
        end_year = self.end_year_entry.get()

        if not all([instructor_id, start_semester, end_semester, start_year, end_year]):
            messagebox.showinfo("Error", "All fields must be filled out.")
            return

        try:
            start_year = int(start_year)
            end_year = int(end_year)
        except ValueError:
            self.text_area.insert(tk.END, "Please enter valid integers for the years.\n")
            return

        self.text_area.delete('1.0', tk.END)

        results = self.query_sections2(instructor_id, start_semester, end_semester, start_year, end_year)
        if results:
            for result in results:
                self.text_area.insert(tk.END, f"{result}\n")
        else:
            self.text_area.insert(tk.END, "No results found.\n")

    def check_evaluation_window(self):
        window = tk.Toplevel(self)
        window.title("Database Query Inputs")
        window.geometry("600x300")  # Adjust size as needed
        self.center_window(window)

        # Create a Text widget for results within the input window
        self.results_text = scrolledtext.ScrolledText(window, height=10, width=50)
        self.results_text.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=10)

        def get_input():
            year = simpledialog.askinteger("Input", "Enter the year:", parent=window)
            semester = simpledialog.askstring("Input", "Enter the semester (e.g., 'Fall'):", parent=window)
            if year and semester:
                self.check_section_entries(year, semester)
            else:
                messagebox.showwarning("Warning", "Year and Semester are required to proceed.", parent=window)

        input_button = tk.Button(window, text="Enter Details", command=get_input)
        input_button.pack(pady=10)

        close_button = tk.Button(window, text="Close", command=window.destroy)
        close_button.pack(pady=10)

    def check_section_entries(self, year, semester):
        cursor = self.connection.cursor()
        query = """
            SELECT course_id, section_id, semester, year,
                   CASE
                       WHEN A_count IS NOT NULL AND B_count IS NOT NULL AND C_count IS NOT NULL AND F_count IS NOT NULL THEN 'Fully Entered'
                       WHEN A_count IS NULL AND B_count IS NULL AND C_count IS NULL AND F_count IS NULL THEN 'Not Entered'
                       ELSE 'Partially Entered'
                   END AS grade_entry_status,
                   CASE
                       WHEN assessment_method IS NULL THEN 'Assessment method not entered'
                       ELSE 'Assessment method entered'
                   END AS assessment_method_status,
                   CASE
                       WHEN instructor_note IS NULL THEN 'Instructor note not entered'
                       ELSE 'Instructor note entered'
                   END AS instructor_note_status
            FROM Evaluations
            WHERE year = %s AND semester = %s;
            """
        cursor.execute(query, (year, semester))
        results = cursor.fetchall()

        # Clear previous results
        self.results_text.delete('1.0', tk.END)

        for result in results:
            self.results_text.insert(tk.END,
                                     f"Course ID: {result[0]}, Section ID: {result[1]}, Semester: {result[2]}, Year: {result[3]}, Grades Status: {result[4]}, {result[5]}, {result[6]}\n")
        cursor.close()

    def check_percentage_window(self):
        window = Toplevel(self.master)
        window.title("Input Parameters")
        window.geometry("600x600")
        self.center_window(window)


        Label(window, text="Year:").pack()
        year_entry = simpledialog.askinteger("Input", "Enter the year:", parent=window)

        Label(window, text="Semester:").pack()
        semester_entry = simpledialog.askstring("Input", "Enter the semester (e.g., 'Fall'):", parent=window)

        Label(window, text="Minimum Percentage (without '%'):").pack()
        percentage_entry = simpledialog.askinteger("Input", "Enter the minimum percentage:", parent=window)

        if year_entry and semester_entry and percentage_entry is not None:
            self.fetch_sections(year_entry, semester_entry, percentage_entry, window)
        else:
            messagebox.showinfo("Input Error", "All inputs must be filled out.", parent=window)

    def fetch_sections(self, year, semester, min_percentage, window):
        cursor = self.connection.cursor()
        query = """
            SELECT course_id, section_id, semester, year,
                   100.0 * (A_count + B_count + C_count) / (A_count + B_count + C_count + F_count) AS non_f_percentage
            FROM Evaluations
            WHERE year = %s AND semester = %s;
            """
        try:
            cursor.execute(query, (year, semester))  # Ensure two parameters are passed
            results = cursor.fetchall()

            # Displaying results
            result_listbox = tk.Listbox(window)
            result_listbox.pack(fill=tk.BOTH, expand=True)

            for result in results:
                non_f_percentage = float(result[4])
                if non_f_percentage >= min_percentage:
                    result_listbox.insert(END, f"Course ID: {result[0]}, Section ID: {result[1]}, "
                                               f"Semester: {result[2]}, Year: {result[3]}, Non-F Percentage: {non_f_percentage:.2f}%")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch sections: {e}", parent=window)
        finally:
            cursor.close()

    def center_window(self, win=None):
        win = win or self
        win.update_idletasks()  # Update "idle" tasks to get correct dimensions
        width = win.winfo_width()
        height = win.winfo_height()
        x = (win.winfo_screenwidth() // 2) - (width // 2)
        y = (win.winfo_screenheight() // 2) - (height // 2)
        win.geometry(f'{width}x{height}+{x}+{y}')

    def load_db_config(self):
        try:
            with open('db_config.json', 'r') as config_file:  # remember to load your bd info file
                return json.load(config_file)
        except FileNotFoundError:
            messagebox.showerror("File Error", "Database configuration file not found.")
            return None
        except json.JSONDecodeError:
            messagebox.showerror("File Error", "Error decoding the configuration file.")
            return None

    def connect_to_database(self):
        if not self.db_config:
            return None
        try:
            # Prepare the connection configuration with automatic result consumption
            connection_config = {
                'user': self.db_config['user'],
                'password': self.db_config['password'],
                'database': self.db_config['database'],
                'consume_results': True  # Enable automatic clearing of results
            }

            connection = connect(**connection_config)  # Use the updated config dictionary
            if connection.is_connected():
                self.status_bar.config(text="Connected to MySQL Server")
                messagebox.showinfo("Connection", "Successfully connected to the database.")
                return connection
        except Error as e:
            messagebox.showerror("Connection", f"Error while connecting to MySQL:\n{e}")
            self.status_bar.config(text="Disconnected")
            return None


if __name__ == "__main__":
    app = ProgramEvaluationApp()
    app.mainloop()
