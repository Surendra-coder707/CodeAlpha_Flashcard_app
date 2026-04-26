import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os
import requests
import html

class FlashcardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Flashcard Quiz App 🌐📚")
        self.root.geometry("900x650")
        self.root.configure(bg="#1e1e2f")

        self.file = "flashcards.json"
        self.cards = []
        self.index = 0
        self.show_answer = False
        self.mode = "local"   # local / api

        self.api_question = ""
        self.api_answer = ""

        self.load_data()
        self.setup_ui()
        self.update_card()

        # keyboard
        self.root.bind("<Right>", lambda e: self.next_card())
        self.root.bind("<Left>", lambda e: self.prev_card())

    # ---------------- DATA ----------------

    def load_data(self):
        if os.path.exists(self.file):
            with open(self.file, "r") as f:
                self.cards = json.load(f)
        else:
            self.cards = [
                {"question": "What is Python?", "answer": "Programming language"},
                {"question": "2 + 2 = ?", "answer": "4"}
            ]
            self.save_data()

    def save_data(self):
        with open(self.file, "w") as f:
            json.dump(self.cards, f, indent=2)

    # ---------------- UI ----------------

    def setup_ui(self):
        tk.Label(self.root, text="📚 Flashcard + Quiz App",
                 font=("Arial", 20, "bold"),
                 bg="#1e1e2f", fg="white").pack(pady=10)

        self.card = tk.Label(self.root, text="",
                             font=("Arial", 18),
                             bg="#2c2c3e",
                             fg="white",
                             wraplength=700,
                             height=8,
                             width=60,
                             relief="ridge",
                             bd=3)
        self.card.pack(pady=20)

        # Buttons
        btn_frame = tk.Frame(self.root, bg="#1e1e2f")
        btn_frame.pack()

        tk.Button(btn_frame, text="⬅ Previous", command=self.prev_card).grid(row=0, column=0, padx=10)

        self.toggle_btn = tk.Button(btn_frame, text="Show Answer",
                                   command=self.toggle_answer)
        self.toggle_btn.grid(row=0, column=1, padx=10)

        tk.Button(btn_frame, text="Next ➡", command=self.next_card).grid(row=0, column=2, padx=10)

        # Mode switch
        mode_frame = tk.Frame(self.root, bg="#1e1e2f")
        mode_frame.pack(pady=10)

        tk.Button(mode_frame, text="📚 Local Cards", command=self.use_local).grid(row=0, column=0, padx=10)
        tk.Button(mode_frame, text="🌐 Online Quiz", command=self.use_api).grid(row=0, column=1, padx=10)

        # Manage
        manage_frame = tk.Frame(self.root, bg="#1e1e2f")
        manage_frame.pack(pady=10)

        tk.Button(manage_frame, text="➕ Add", command=self.add_card).grid(row=0, column=0, padx=5)
        tk.Button(manage_frame, text="✏ Edit", command=self.edit_card).grid(row=0, column=1, padx=5)
        tk.Button(manage_frame, text="🗑 Delete", command=self.delete_card).grid(row=0, column=2, padx=5)

        self.status = tk.Label(self.root, text="", bg="#1e1e2f", fg="white")
        self.status.pack()

    # ---------------- API ----------------

    def get_api_question(self):
        try:
            url = "https://opentdb.com/api.php?amount=1&type=multiple"
            res = requests.get(url)
            data = res.json()["results"][0]

            self.api_question = html.unescape(data["question"])
            self.api_answer = html.unescape(data["correct_answer"])

        except:
            messagebox.showerror("Error", "Internet issue!")

    # ---------------- LOGIC ----------------

    def update_card(self):
        if self.mode == "api":
            if not self.api_question:
                self.get_api_question()

            if self.show_answer:
                self.card.config(text=f"Answer:\n{self.api_answer}", bg="#16a085")
            else:
                self.card.config(text=f"Question:\n{self.api_question}", bg="#2c2c3e")

            self.status.config(text="Mode: Online Quiz 🌐")

        else:
            if not self.cards:
                self.card.config(text="No cards available!")
                return

            card = self.cards[self.index]

            if self.show_answer:
                self.card.config(text=f"Answer:\n{card['answer']}", bg="#16a085")
            else:
                self.card.config(text=f"Question:\n{card['question']}", bg="#2c2c3e")

            self.status.config(text=f"Card {self.index+1}/{len(self.cards)} | Mode: Local 📚")

    def toggle_answer(self):
        self.show_answer = not self.show_answer
        self.update_card()

    def next_card(self):
        self.show_answer = False

        if self.mode == "api":
            self.get_api_question()
        else:
            if self.index < len(self.cards)-1:
                self.index += 1

        self.update_card()

    def prev_card(self):
        if self.mode == "local" and self.index > 0:
            self.index -= 1
            self.show_answer = False
            self.update_card()

    # ---------------- MODE ----------------

    def use_local(self):
        self.mode = "local"
        self.show_answer = False
        self.update_card()

    def use_api(self):
        self.mode = "api"
        self.api_question = ""
        self.show_answer = False
        self.update_card()

    # ---------------- CRUD ----------------

    def add_card(self):
        q = simpledialog.askstring("Question", "Enter Question:")
        a = simpledialog.askstring("Answer", "Enter Answer:")

        if q and a:
            self.cards.append({"question": q, "answer": a})
            self.save_data()
            self.update_card()

    def edit_card(self):
        if not self.cards:
            return

        card = self.cards[self.index]

        q = simpledialog.askstring("Edit Q", "Update Question:", initialvalue=card["question"])
        a = simpledialog.askstring("Edit A", "Update Answer:", initialvalue=card["answer"])

        if q and a:
            card["question"] = q
            card["answer"] = a
            self.save_data()
            self.update_card()

    def delete_card(self):
        if not self.cards:
            return

        if messagebox.askyesno("Confirm", "Delete this card?"):
            self.cards.pop(self.index)
            self.save_data()

            if self.index >= len(self.cards):
                self.index = max(0, len(self.cards)-1)

            self.update_card()

# ---------------- RUN ----------------

root = tk.Tk()
app = FlashcardApp(root)
root.mainloop()