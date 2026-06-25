"""
Fitness Tracker App
--------------------
Step 1: SQLite database setup (local storage)
Step 2: Add/log fitness data manually
Step 3: Dashboard/summary screen (daily + weekly)
Step 4: Simple, clean Tkinter UI with progress bars
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime, timedelta

DB_NAME = "fitness.db"


# ---------------------------------------------------------
# STEP 1: Database setup
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            duration_min INTEGER DEFAULT 0,
            steps INTEGER DEFAULT 0,
            calories INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()


def add_activity(date, activity_type, duration, steps, calories):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO activities (date, activity_type, duration_min, steps, calories)
        VALUES (?, ?, ?, ?, ?)
    """, (date, activity_type, duration, steps, calories))
    conn.commit()
    conn.close()


def get_all_activities():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, activity_type, duration_min, steps, calories FROM activities ORDER BY date DESC")
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_activity(activity_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM activities WHERE id=?", (activity_id,))
    conn.commit()
    conn.close()


def get_summary(start_date, end_date):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT SUM(steps), SUM(calories), SUM(duration_min), COUNT(*)
        FROM activities WHERE date BETWEEN ? AND ?
    """, (start_date, end_date))
    result = cursor.fetchone()
    conn.close()
    steps = result[0] or 0
    calories = result[1] or 0
    duration = result[2] or 0
    count = result[3] or 0
    return steps, calories, duration, count


# ---------------------------------------------------------
# STEP 2: Main Application (UI)
# ---------------------------------------------------------
class FitnessTrackerApp:
    DAILY_STEP_GOAL = 10000

    def __init__(self, root):
        self.root = root
        self.root.title("Fitness Tracker")
        self.root.geometry("650x550")
        self.root.configure(bg="#f4f6f8")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self.add_tab = ttk.Frame(self.notebook)
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.log_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.dashboard_tab, text="📊 Dashboard")
        self.notebook.add(self.add_tab, text="➕ Add Activity")
        self.notebook.add(self.log_tab, text="📋 Activity Log")

        self.build_add_tab()
        self.build_dashboard_tab()
        self.build_log_tab()

        self.refresh_dashboard()
        self.refresh_log()

    # -------------------------------------------------
    # STEP 3: Add Activity Tab
    # -------------------------------------------------
    def build_add_tab(self):
        frame = tk.Frame(self.add_tab, bg="#f4f6f8", padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Log New Activity", font=("Helvetica", 16, "bold"),
                 bg="#f4f6f8").grid(row=0, column=0, columnspan=2, pady=(0, 15))

        labels = ["Date (YYYY-MM-DD)", "Activity Type", "Duration (min)", "Steps", "Calories Burned"]
        self.entries = {}

        for i, label in enumerate(labels, start=1):
            tk.Label(frame, text=label, bg="#f4f6f8", font=("Helvetica", 11)).grid(
                row=i, column=0, sticky="w", pady=8)
            entry = tk.Entry(frame, width=25, font=("Helvetica", 11))
            entry.grid(row=i, column=1, pady=8)
            self.entries[label] = entry

        # default date = today
        self.entries["Date (YYYY-MM-DD)"].insert(0, datetime.now().strftime("%Y-%m-%d"))

        save_btn = tk.Button(frame, text="Save Activity", bg="#4caf50", fg="white",
                              font=("Helvetica", 11, "bold"), command=self.save_activity)
        save_btn.grid(row=len(labels) + 1, column=0, columnspan=2, pady=20, ipadx=10, ipady=5)

    def save_activity(self):
        try:
            date = self.entries["Date (YYYY-MM-DD)"].get().strip()
            activity_type = self.entries["Activity Type"].get().strip()
            duration = int(self.entries["Duration (min)"].get() or 0)
            steps = int(self.entries["Steps"].get() or 0)
            calories = int(self.entries["Calories Burned"].get() or 0)

            if not date or not activity_type:
                messagebox.showwarning("Missing Info", "Date and Activity Type are required.")
                return

            datetime.strptime(date, "%Y-%m-%d")  # validate format

            add_activity(date, activity_type, duration, steps, calories)
            messagebox.showinfo("Success", "Activity logged successfully!")

            for entry in self.entries.values():
                entry.delete(0, tk.END)
            self.entries["Date (YYYY-MM-DD)"].insert(0, datetime.now().strftime("%Y-%m-%d"))

            self.refresh_dashboard()
            self.refresh_log()

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers and date format (YYYY-MM-DD).")

    # -------------------------------------------------
    # STEP 4: Dashboard Tab (Summary + Progress Bars)
    # -------------------------------------------------
    def build_dashboard_tab(self):
        frame = tk.Frame(self.dashboard_tab, bg="#f4f6f8", padx=20, pady=20)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="Your Progress", font=("Helvetica", 16, "bold"),
                 bg="#f4f6f8").pack(pady=(0, 15))

        # Today's summary
        self.today_frame = tk.LabelFrame(frame, text="Today", font=("Helvetica", 12, "bold"),
                                          bg="#f4f6f8", padx=15, pady=15)
        self.today_frame.pack(fill="x", pady=10)

        self.today_steps_label = tk.Label(self.today_frame, text="", bg="#f4f6f8", font=("Helvetica", 11))
        self.today_steps_label.pack(anchor="w")
        self.today_progress = ttk.Progressbar(self.today_frame, length=400, maximum=self.DAILY_STEP_GOAL)
        self.today_progress.pack(pady=5, anchor="w")

        self.today_cal_label = tk.Label(self.today_frame, text="", bg="#f4f6f8", font=("Helvetica", 11))
        self.today_cal_label.pack(anchor="w")
        self.today_duration_label = tk.Label(self.today_frame, text="", bg="#f4f6f8", font=("Helvetica", 11))
        self.today_duration_label.pack(anchor="w")

        # Weekly summary
        self.week_frame = tk.LabelFrame(frame, text="This Week", font=("Helvetica", 12, "bold"),
                                         bg="#f4f6f8", padx=15, pady=15)
        self.week_frame.pack(fill="x", pady=10)

        self.week_steps_label = tk.Label(self.week_frame, text="", bg="#f4f6f8", font=("Helvetica", 11))
        self.week_steps_label.pack(anchor="w")
        self.week_cal_label = tk.Label(self.week_frame, text="", bg="#f4f6f8", font=("Helvetica", 11))
        self.week_cal_label.pack(anchor="w")
        self.week_workout_label = tk.Label(self.week_frame, text="", bg="#f4f6f8", font=("Helvetica", 11))
        self.week_workout_label.pack(anchor="w")

        refresh_btn = tk.Button(frame, text="🔄 Refresh", command=self.refresh_dashboard,
                                 bg="#2196f3", fg="white", font=("Helvetica", 10, "bold"))
        refresh_btn.pack(pady=10)

    def refresh_dashboard(self):
        today = datetime.now().strftime("%Y-%m-%d")
        steps, calories, duration, count = get_summary(today, today)

        self.today_steps_label.config(text=f"Steps: {steps} / {self.DAILY_STEP_GOAL}")
        self.today_progress["value"] = min(steps, self.DAILY_STEP_GOAL)
        self.today_cal_label.config(text=f"Calories Burned: {calories} kcal")
        self.today_duration_label.config(text=f"Active Duration: {duration} min")

        week_start = (datetime.now() - timedelta(days=6)).strftime("%Y-%m-%d")
        w_steps, w_calories, w_duration, w_count = get_summary(week_start, today)

        self.week_steps_label.config(text=f"Total Steps: {w_steps}")
        self.week_cal_label.config(text=f"Total Calories: {w_calories} kcal")
        self.week_workout_label.config(text=f"Workouts Logged: {w_count}")

    # -------------------------------------------------
    # Activity Log Tab
    # -------------------------------------------------
    def build_log_tab(self):
        frame = tk.Frame(self.log_tab, bg="#f4f6f8", padx=10, pady=10)
        frame.pack(fill="both", expand=True)

        columns = ("ID", "Date", "Type", "Duration", "Steps", "Calories")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=90, anchor="center")
        self.tree.pack(fill="both", expand=True)

        del_btn = tk.Button(frame, text="Delete Selected", bg="#f44336", fg="white",
                             font=("Helvetica", 10, "bold"), command=self.delete_selected)
        del_btn.pack(pady=10)

    def refresh_log(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        for activity in get_all_activities():
            self.tree.insert("", "end", values=activity)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an entry to delete.")
            return
        item = self.tree.item(selected[0])
        activity_id = item["values"][0]
        delete_activity(activity_id)
        self.refresh_log()
        self.refresh_dashboard()


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------
if __name__ == "__main__":
    init_db()
    root = tk.Tk()
    app = FitnessTrackerApp(root)
    root.mainloop()