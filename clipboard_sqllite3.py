#Persistent Clipboard

import tkinter as tk
import sqlite3
import os

class ClipboardDB:
    def __init__(self):
        self.connection = sqlite3.connect("clipboard_boards.db")
        print(os.path.abspath(os.curdir))
        self.create_table()

    def create_table(self):
        cursor = self.connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS clipboard (board_id INTEGER, item TEXT)")

    def load_data(self, board_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT item FROM clipboard WHERE board_id = ?", (board_id,))
        return [row[0] for row in cursor.fetchall()]

    def save_data(self, board_id, items):
        cursor = self.connection.cursor()
        cursor.execute("DELETE FROM clipboard WHERE board_id = ?", (board_id,))
        data = [(board_id, item) for item in items]
        cursor.executemany("INSERT INTO clipboard VALUES (?, ?)", data)
        self.connection.commit()

    def close(self):
        self.connection.close()

class ClipboardApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Clipboard App")
        self.root.geometry("600x420")

        self.current_board = 1
        self.clipboard_data = []

        self.db = ClipboardDB()

        self.load_data()
        self.create_widgets()

        self.root.protocol("WM_DELETE_WINDOW", self.close_app)

    def load_data(self):
        self.clipboard_data = self.db.load_data(self.current_board)

    def close_app(self):
        self.db.save_data(self.current_board, self.clipboard_data)
        self.db.close()
        self.root.destroy()

    def create_widgets(self):
        self.labels_frame = tk.LabelFrame(self.root)
        self.labels_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        input_frame = tk.Frame(self.root)
        input_frame.pack(side=tk.BOTTOM, padx=10, pady=10)

        input_bar_frame = tk.LabelFrame(input_frame)
        input_bar_frame.pack(side=tk.TOP)

        self.text_entry = tk.Entry(input_bar_frame, width=30)
        self.text_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.text_entry.bind("<Return>", self.add_note)

        add_button = tk.Button(input_bar_frame, text="Add", command=self.add_note)
        add_button.pack(side=tk.LEFT)

        nav_frame = tk.LabelFrame(input_frame)
        nav_frame.pack(side=tk.TOP, pady=(0, 5))

        nav_buttons = [("Previous", -1), ("Next", 1)]
        for text, delta in nav_buttons:
            button = tk.Button(nav_frame, text=text, command=lambda d=delta: self.change_board(d))
            button.pack(side=tk.LEFT if text == "Previous" else tk.RIGHT)

        self.update_labels()
        self.update_page_label()

    def update_labels(self):
        for child in self.labels_frame.winfo_children():
            child.destroy()

        for i, text in enumerate(self.clipboard_data):
            self.create_label_with_buttons(text, i)
        
    def create_label_with_buttons(self, text, index):
        label_frame = tk.Frame(self.labels_frame, padx=10, pady=10, relief=tk.SOLID, bd=1)
        label_frame.grid(row=index % 5, column=index // 5, sticky="nsew")

        label = tk.Label(label_frame, text=text, anchor=tk.W, wraplength=200)
        label.pack(side=tk.LEFT, padx=5, pady=5)
        label.bind("<Button-1>", lambda event, text=text: self.copy_item(text))
        label.bind("<Button-3>", lambda event, text=text: self.copy_item(text))

        delete_button = tk.Button(label_frame, text="X", command=lambda: self.delete_item(index))
        delete_button.pack(side=tk.RIGHT, padx=(0, 5), pady=5)

    def update_page_label(self):
        if hasattr(self, "page_label"):
            self.page_label.destroy()
        self.page_label = tk.Label(self.root, text=f"Page: {self.current_board}")
        self.page_label.pack(side=tk.TOP, anchor=tk.CENTER, padx=10, pady=(10, 0))

    def change_board(self, delta):
        self.db.save_data(self.current_board, self.clipboard_data)
        self.current_board += delta
        if self.current_board < 1:
            self.current_board = 1
        self.load_data()
        self.update_labels()
        self.update_page_label()

    def add_note(self, event=None):
        text = self.text_entry.get().strip()
        if text:
            self.clipboard_data.append(text)
            self.update_labels()
            self.text_entry.delete(0, tk.END)

    def delete_item(self, index):
        if 0 <= index < len(self.clipboard_data):
            del self.clipboard_data[index]
            self.update_labels()

    def copy_item(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)

    def run(self):
        self.root.mainloop()

app = ClipboardApp()
app.run()
