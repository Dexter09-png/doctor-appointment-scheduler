import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from pymongo import MongoClient
from datetime import datetime
import uuid

# ------------------ DB Setup ------------------
def get_db_collection(uri="mongodb://localhost:27017/",
                      db_name="appointment_db", coll_name="appointments"):
    client = MongoClient(uri)
    db = client[db_name]
    return db[coll_name]

collection = get_db_collection()

# ------------------ Helpers ------------------
def validate_time(t):
    try:
        return datetime.strptime(t, "%H:%M").time()   # 24-hour HH:MM
    except ValueError:
        return None

def make_uid():
    return str(uuid.uuid4())[:8]   # short unique id

# ------------------ CRUD ------------------
def add_appointment():
    name = ent_name.get().strip()
    date_str = ent_date.get_date().strftime("%Y-%m-%d")
    time_str = ent_time.get().strip()
    purpose = ent_purpose.get().strip()

    if not (name and time_str and purpose):
        messagebox.showerror("Missing", "Please fill all fields.")
        return

    time_obj = validate_time(time_str)
    if not time_obj:
        messagebox.showerror("Time error", "Time must be in HH:MM (24-hour) format.")
        return

    when = datetime.combine(ent_date.get_date(), time_obj)
    uid = make_uid()

    doc = {
        "uid": uid,
        "patient name": name,
        "date": date_str,
        "time": time_str,
        "when": when,
        "purpose": purpose,
        "status": "Scheduled"
    }

    collection.insert_one(doc)
    messagebox.showinfo("Added", f"Appointment {uid} created.")
    clear_form()
    display_all()

def display_all():
    for row in tree.get_children():
        tree.delete(row)
    for doc in collection.find().sort("when", 1):
        tree.insert("", tk.END, iid=doc["uid"],
                    values=(doc["uid"], doc.get("patient name", ""), doc["date"], doc["time"], doc["purpose"], doc.get("status","")))

def edit_appointment():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Select", "Choose an appointment to edit.")
        return
    uid = sel[0]
    name = ent_name.get().strip()
    date_obj = ent_date.get_date()
    time_str = ent_time.get().strip()
    purpose = ent_purpose.get().strip()
    status = status_var.get()

    if not (name and time_str and purpose):
        messagebox.showerror("Missing", "Please fill all fields.")
        return

    time_obj = validate_time(time_str)
    if not time_obj:
        messagebox.showerror("Time error", "Time must be in HH:MM (24-hour) format.")
        return

    when = datetime.combine(date_obj, time_obj)
    date_str = date_obj.strftime("%Y-%m-%d")

    result = collection.update_one({"uid": uid},
                                   {"$set": {"patient name": name, "date": date_str, "time": time_str,
                                             "when": when, "purpose": purpose, "status": status}})
    if result.matched_count:
        messagebox.showinfo("Updated", f"Appointment {uid} updated.")
    else:
        messagebox.showerror("Not found", "Appointment not found in DB.")
    clear_form()
    display_all()

def remove_appointment():
    sel = tree.selection()
    if not sel:
        messagebox.showwarning("Select", "Choose an appointment to remove.")
        return
    uid = sel[0]
    confirm = messagebox.askyesno("Confirm", f"Delete appointment {uid}?")
    if not confirm:
        return
    result = collection.delete_one({"uid": uid})
    if result.deleted_count:
        messagebox.showinfo("Deleted", f"Appointment {uid} removed.")
    else:
        messagebox.showwarning("Missing", "Appointment not found.")
    clear_form()
    display_all()

def clear_form():
    ent_name.delete(0, tk.END)
    ent_date.set_date(datetime.today())
    ent_time.delete(0, tk.END)
    ent_purpose.delete(0, tk.END)
    status_var.set("Scheduled")
    tree.selection_remove(tree.selection())

def on_tree_select(event):
    sel = tree.selection()
    if not sel:
        return
    uid = sel[0]
    doc = collection.find_one({"uid": uid})
    if not doc:
        return
    ent_name.delete(0, tk.END); ent_name.insert(0, doc.get("name",""))
    ent_date.set_date(datetime.strptime(doc.get("date",""), "%Y-%m-%d"))
    ent_time.delete(0, tk.END); ent_time.insert(0, doc.get("time",""))
    ent_purpose.delete(0, tk.END); ent_purpose.insert(0, doc.get("purpose",""))
    status_var.set(doc.get("status","Scheduled"))

# ------------------ UI ------------------
root = tk.Tk()
root.title("🩺 Doctor Appointment Scheduler")
root.state('zoomed')  # maximize window

# Colors
BG_COLOR = "#F5F5DC"
BTN_BG = "#D35400"
BTN_FG = "white"

root.configure(bg=BG_COLOR)

banner = tk.Label(root, text="🩺 Doctor Appointment Scheduler", font=("Helvetica", 18, "bold"), bg=BG_COLOR)
banner.pack(pady=10)

main = tk.Frame(root, bg=BG_COLOR)
main.pack(fill=tk.BOTH, expand=True, padx=12)

form = tk.Frame(main, bg=BG_COLOR)
form.pack(side=tk.LEFT, fill=tk.Y, padx=(0,12))

lbl = lambda parent, txt: tk.Label(parent, text=txt, anchor="w", bg=BG_COLOR, font=("Helvetica", 11))

# Patient Name
lbl(form, "Patient Name:").grid(row=0, column=0, sticky="w", pady=(6,0))
ent_name = tk.Entry(form, width=28)
ent_name.grid(row=0, column=1, pady=(6,0), padx=6)

# Date
lbl(form, "Date:").grid(row=1, column=0, sticky="w", pady=(6,0))
ent_date = DateEntry(form, width=16, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
ent_date.grid(row=1, column=1, pady=(6,0), sticky="w", padx=6)

# Time
lbl(form, "Time (HH:MM 24h):").grid(row=2, column=0, sticky="w", pady=(6,0))
ent_time = tk.Entry(form, width=16)
ent_time.grid(row=2, column=1, pady=(6,0), sticky="w", padx=6)

# Reason for Visit
lbl(form, "Purpose:").grid(row=3, column=0, sticky="w", pady=(6,0))
ent_purpose = tk.Entry(form, width=40)
ent_purpose.grid(row=3, column=1, pady=(6,0), padx=6)

# Status
lbl(form, "Status:").grid(row=4, column=0, sticky="w", pady=(8,0))
status_var = tk.StringVar(value="Scheduled")
status_menu = ttk.Combobox(form, textvariable=status_var, values=["Scheduled", "Completed", "Cancelled"], state="readonly", width=14)
status_menu.grid(row=4, column=1, sticky="w", pady=(8,0), padx=6)

btn_frame = tk.Frame(form, bg=BG_COLOR)
btn_frame.grid(row=5, column=0, columnspan=2, pady=12)

def on_enter(e):
    e.widget['background'] = "#E67E22"

def on_leave(e):
    e.widget['background'] = BTN_BG

btn_add = tk.Button(btn_frame, text="Add", width=12, bg=BTN_BG, fg=BTN_FG, command=add_appointment, relief="flat")
btn_add.grid(row=0, column=0, padx=6)
btn_add.bind("<Enter>", on_enter)
btn_add.bind("<Leave>", on_leave)

btn_edit = tk.Button(btn_frame, text="Edit", width=12, bg=BTN_BG, fg=BTN_FG, command=edit_appointment, relief="flat")
btn_edit.grid(row=0, column=1, padx=6)
btn_edit.bind("<Enter>", on_enter)
btn_edit.bind("<Leave>", on_leave)

btn_remove = tk.Button(btn_frame, text="Remove", width=12, bg=BTN_BG, fg=BTN_FG, command=remove_appointment, relief="flat")
btn_remove.grid(row=0, column=2, padx=6)
btn_remove.bind("<Enter>", on_enter)
btn_remove.bind("<Leave>", on_leave)

btn_clear = tk.Button(btn_frame, text="Clear", width=12, bg=BTN_BG, fg=BTN_FG, command=clear_form, relief="flat")
btn_clear.grid(row=0, column=3, padx=6)
btn_clear.bind("<Enter>", on_enter)
btn_clear.bind("<Leave>", on_leave)

btn_refresh = tk.Button(btn_frame, text="Refresh View", width=12, bg=BTN_BG, fg=BTN_FG, command=display_all, relief="flat")
btn_refresh.grid(row=0, column=4, padx=6)
btn_refresh.bind("<Enter>", on_enter)
btn_refresh.bind("<Leave>", on_leave)

tree_frame = tk.Frame(main, bg=BG_COLOR)
tree_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

cols = ("UID", "Patient Name", "Date", "Time", "Purpose", "Status")
tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=18)
for c in cols:
    tree.heading(c, text=c)

tree.column("UID", width=100, anchor="center")
tree.column("Patient Name", width=160, anchor="w")
tree.column("Date", width=90, anchor="center")
tree.column("Time", width=80, anchor="center")
tree.column("Purpose", width=260, anchor="w")
tree.column("Status", width=100, anchor="center")

vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscroll=vsb.set)
tree.grid(row=0, column=0, sticky="nsew")
vsb.grid(row=0, column=1, sticky="ns")

tree_frame.grid_rowconfigure(0, weight=1)
tree_frame.grid_columnconfigure(0, weight=1)

tree.bind("<<TreeviewSelect>>", on_tree_select)

ent_date.set_date(datetime.today())
display_all()

root.mainloop()
