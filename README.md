# Student Grade Calculator — Project Plan & README

**Topic:** 4 — Student Grade Calculator
**Course:** Introduction to Software Development — Mini Project Exam
**Language/Stack:** Python 3, Tkinter (GUI), SQLite3 (persistent storage)

---

## 1. What This Project Does

This application lets a lecturer or student enter a student's name and at
least three assessment scores. It calculates the total score, the average
score, assigns a letter grade (A–F), and shows whether the student passed
or failed. All records are saved to a local SQLite database, so they're
still there the next time the app is opened. Records can also be deleted.

## 2. How to Run It

**Requirements:** Python 3.8+ (Tkinter ships with the standard Python
installer on Windows and macOS; on Linux, install it with
`sudo apt install python3-tk` if it's missing).

```bash
git clone <your-repo-url>
cd grade-calculator
python3 grade_calculator.py
```

No external packages are required — everything used (`tkinter`, `sqlite3`)
is part of the Python standard library. A file named `grades.db` will be
created automatically in the project folder the first time you run it;
that's where records are stored between sessions.

---

## 3. Requirements

These are the 3–5 core requirements the app is built to satisfy:

1. The system shall let the user enter a student's name and at least
   three assessment scores (0–100 each).
2. The system shall calculate the total and average of the entered scores.
3. The system shall assign a letter grade (A–F) based on the average, and
   display whether the student passed or failed.
4. The system shall display all previously entered student records,
   loaded from persistent storage (SQLite database).
5. The system shall let the user delete an existing student record.

---

## 4. Classes and Functions Needed

| Name | Type | Responsibility |
|---|---|---|
| `StudentRecord` | class | Holds one student's name and scores; computes `total`, `average`, `grade`, and `is_pass` as properties. |
| `GradeDatabase` | class | Wraps the SQLite connection. Methods: `init_db()`, `add_record()`, `get_all_records()`, `delete_record(record_id)`. |
| `GradeCalculatorApp` | class (extends `tk.Tk`) | Builds the window and widgets. Methods: `build_form()`, `on_calculate()`, `on_delete()`, `refresh_table()`, `validate_scores()`. |
| `validate_scores(raw_list)` | function | Checks that at least 3 scores were entered and that each is a number between 0 and 100; raises a clear error otherwise. |
| `assign_grade(average)` | function | Applies the grading scale (A ≥70, B ≥60, C ≥50, D ≥45, E ≥40, F <40) and returns the letter grade. |

---

## 5. Expected Input and Output, per Feature

**Feature: Add a student record**
- Input: name (text), 3+ scores (numbers, 0–100, entered in separate fields)
- Output: total, average, letter grade, and pass/fail status shown on
  screen; the record is saved to the database and appears in the table
  below.

**Feature: Calculate grade**
- Input: a list of numeric scores
- Output: a single letter grade (A–F) and a pass/fail boolean

**Feature: Display all records**
- Input: none (reads from the SQLite database on startup and after any change)
- Output: a table with columns — Name, Scores, Total, Average, Grade, Status

**Feature: Delete a record**
- Input: the record selected in the table
- Output: that row is removed from the table and permanently deleted
  from the database

**Feature: Input validation**
- Input: an empty name, an empty score field, a non-numeric score, or a
  score outside 0–100
- Output: the record is *not* saved; a clear error message is shown
  telling the user what to fix

---

## 6. Design Notes

- **Why SQLite instead of a text file:** SQLite gives real persistence
  with almost no extra code, and it's the closest local-storage
  equivalent available to a Python desktop app (the exam's Local Storage
  requirement is a browser-only feature, so this is the nearest
  standard-library substitute).
- **Why Tkinter:** it's in the Python standard library, so no extra
  installs are needed to run the app, keeping setup simple for grading.
