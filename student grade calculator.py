"""
Student Grade Calculator
-------------------------
A desktop app (Tkinter GUI, SQLite storage) that lets a lecturer or
student enter a student's name and assessment scores, then calculates
the total, average, letter grade, and pass/fail status. Records persist
between sessions in a local SQLite database (grades.db).

Run with:  python3 grade_calculator.py
Requires only the Python standard library (tkinter, sqlite3).
"""

import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox

DB_FILE = "grades.db"


# ---------------------------------------------------------------------
# Model
# ---------------------------------------------------------------------
class StudentRecord:
    """Represents one student's name and assessment scores."""

    def __init__(self, name, scores, record_id=None):
        self.id = record_id
        self.name = name
        self.scores = scores  # list of floats

    @property
    def total(self):
        total = 0
        for score in self.scores:
            total += score
        return total

    @property
    def average(self):
        if not self.scores:
            return 0
        return self.total / len(self.scores)

    @property
    def grade(self):
        avg = self.average
        if avg >= 70:
            return "A"
        elif avg >= 60:
            return "B"
        elif avg >= 50:
            return "C"
        elif avg >= 45:
            return "D"
        elif avg >= 40:
            return "E"
        else:
            return "F"

    @property
    def is_pass(self):
        return self.grade != "F"

    def scores_display(self):
        return ", ".join(f"{s:.1f}" for s in self.scores)


# ---------------------------------------------------------------------
# Persistence
# ---------------------------------------------------------------------
class GradeDatabase:
    """Wraps the SQLite connection used to persist student records."""

    def __init__(self, db_file=DB_FILE):
        self.conn = sqlite3.connect(db_file)
        self.init_db()

    def init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                scores TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def add_record(self, record):
        scores_str = ",".join(str(s) for s in record.scores)
        cur = self.conn.execute(
            "INSERT INTO records (name, scores) VALUES (?, ?)",
            (record.name, scores_str),
        )
        self.conn.commit()
        record.id = cur.lastrowid
        return record

    def get_all_records(self):
        rows = self.conn.execute("SELECT id, name, scores FROM records").fetchall()
        records = []
        for row_id, name, scores_str in rows:
            scores = [float(s) for s in scores_str.split(",")]
            records.append(StudentRecord(name, scores, record_id=row_id))
        return records

    def delete_record(self, record_id):
        self.conn.execute("DELETE FROM records WHERE id = ?", (record_id,))
        self.conn.commit()


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def validate_scores(raw_values):
    """Turn a list of raw string inputs into validated floats, or raise ValueError."""
    if len(raw_values) < 3:
        raise ValueError("Enter at least three assessment scores.")

    scores = []
    for raw in raw_values:
        raw = raw.strip()
        if raw == "":
            raise ValueError("Please fill in every score field.")
        try:
            value = float(raw)
        except ValueError:
            raise ValueError(f"'{raw}' is not a valid number.")
        if value < 0 or value > 100:
            raise ValueError("Scores must be between 0 and 100.")
        scores.append(value)
    return scores


# ---------------------------------------------------------------------
# GUI
# ---------------------------------------------------------------------
class GradeCalculatorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Grade Ledger — Student Grade Calculator")
        self.geometry("720x560")
        self.configure(bg="#f4f0e4")

        self.db = GradeDatabase()
        self.score_entries = []

        self.build_form()
        self.build_table()
        self.refresh_table()

    # ---- Form ----
    def build_form(self):
        form_frame = tk.LabelFrame(
            self, text="New Entry", bg="#fffdf8", padx=12, pady=12, font=("Arial", 10, "bold")
        )
        form_frame.pack(fill="x", padx=14, pady=(14, 8))

        tk.Label(form_frame, text="Student name:", bg="#fffdf8").grid(row=0, column=0, sticky="w")
        self.name_entry = tk.Entry(form_frame, width=30)
        self.name_entry.grid(row=0, column=1, columnspan=3, sticky="w", pady=(0, 8))

        self.scores_frame = tk.Frame(form_frame, bg="#fffdf8")
        self.scores_frame.grid(row=1, column=0, columnspan=4, sticky="w")

        for _ in range(3):
            self.add_score_field()

        btn_frame = tk.Frame(form_frame, bg="#fffdf8")
        btn_frame.grid(row=2, column=0, columnspan=4, sticky="w", pady=(10, 0))

        tk.Button(btn_frame, text="+ Add another score", command=self.add_score_field).pack(
            side="left", padx=(0, 8)
        )
        tk.Button(
            btn_frame, text="Calculate & Save", command=self.on_calculate, bg="#2b3b31", fg="white"
        ).pack(side="left", padx=(0, 8))
        tk.Button(btn_frame, text="Clear form", command=self.clear_form).pack(side="left")

        self.result_label = tk.Label(
            form_frame, text="", bg="#fffdf8", font=("Arial", 10), justify="left"
        )
        self.result_label.grid(row=3, column=0, columnspan=4, sticky="w", pady=(10, 0))

    def add_score_field(self):
        index = len(self.score_entries) + 1
        row = tk.Frame(self.scores_frame, bg="#fffdf8")
        row.pack(side="left", padx=(0, 10))
        tk.Label(row, text=f"Score {index}:", bg="#fffdf8").pack(anchor="w")
        entry = tk.Entry(row, width=8)
        entry.pack()
        self.score_entries.append(entry)

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        for entry in self.score_entries:
            entry.delete(0, tk.END)
        self.result_label.config(text="")

    # ---- Table ----
    def build_table(self):
        table_frame = tk.LabelFrame(
            self, text="All Records", bg="#fffdf8", padx=12, pady=12, font=("Arial", 10, "bold")
        )
        table_frame.pack(fill="both", expand=True, padx=14, pady=8)

        columns = ("name", "scores", "total", "average", "grade", "status")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        headings = {
            "name": "Name", "scores": "Scores", "total": "Total",
            "average": "Average", "grade": "Grade", "status": "Status",
        }
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True)

        tk.Button(table_frame, text="Delete selected", command=self.on_delete, fg="#9c3b34").pack(
            anchor="e", pady=(8, 0)
        )
        self.count_label = tk.Label(table_frame, text="", bg="#fffdf8")
        self.count_label.pack(anchor="w", pady=(4, 0))

    # ---- Actions ----
    def on_calculate(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showerror("Missing name", "Please enter the student's name.")
            return

        raw_scores = [entry.get() for entry in self.score_entries]
        try:
            scores = validate_scores(raw_scores)
        except ValueError as e:
            messagebox.showerror("Invalid input", str(e))
            return

        record = StudentRecord(name, scores)
        self.db.add_record(record)

        status = "PASS" if record.is_pass else "FAIL"
        self.result_label.config(
            text=(
                f"{record.name} — Total: {record.total:.1f}  "
                f"Average: {record.average:.1f}  Grade: {record.grade}  ({status})"
            )
        )

        self.clear_form()
        self.refresh_table()

    def on_delete(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("No selection", "Select a record in the table first.")
            return
        item = self.tree.item(selected[0])
        record_id = item["tags"][0]
        self.db.delete_record(record_id)
        self.refresh_table()

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        records = self.db.get_all_records()
        for record in records:
            status = "Pass" if record.is_pass else "Fail"
            self.tree.insert(
                "",
                tk.END,
                values=(
                    record.name,
                    record.scores_display(),
                    f"{record.total:.1f}",
                    f"{record.average:.1f}",
                    record.grade,
                    status,
                ),
                tags=(record.id,),
            )

        self.count_label.config(text=f"{len(records)} record(s) stored in {DB_FILE}")


if __name__ == "__main__":
    app = GradeCalculatorApp()
    app.mainloop()
