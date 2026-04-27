import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os
from datetime import datetime

class RandomTaskGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("Генератор случайных задач")
        self.root.geometry("600x600")

        self.history_file = "task_history.json"
        self.tasks_file = "tasks_pool.json"
        
        self.categories = ["Учёба", "Спорт", "Работа", "Другое"]
        
        # Загрузка или создание базового пула задач
        self.tasks_pool = self.load_data(self.tasks_file, [
            {"task": "Прочитать 10 страниц книги", "category": "Учёба"},
            {"task": "Посмотреть обучающее видео", "category": "Учёба"},
            {"task": "Сделать зарядку (15 минут)", "category": "Спорт"},
            {"task": "Пробежка или прогулка", "category": "Спорт"},
            {"task": "Разобрать рабочую почту", "category": "Работа"},
            {"task": "Написать план на завтра", "category": "Работа"}
        ])
        
        self.history = self.load_data(self.history_file, [])

        self.create_widgets()
        self.update_history_table()

    def create_widgets(self):
        # --- Фрейм добавления новой задачи ---
        add_frame = ttk.LabelFrame(self.root, text="Добавить новую задачу", padding=10)
        add_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(add_frame, text="Задача:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.new_task_entry = ttk.Entry(add_frame, width=35)
        self.new_task_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.new_task_category = ttk.Combobox(add_frame, values=self.categories, width=10, state="readonly")
        self.new_task_category.grid(row=0, column=3, padx=5, pady=5)
        self.new_task_category.set(self.categories[0])

        ttk.Button(add_frame, text="Добавить", command=self.add_task).grid(row=0, column=4, padx=5, pady=5)

        # --- Фрейм генерации и фильтрации ---
        gen_frame = ttk.LabelFrame(self.root, text="Генерация", padding=10)
        gen_frame.pack(fill=tk.X, padx=10, pady=5)

        filter_frame = ttk.Frame(gen_frame)
        filter_frame.pack(fill=tk.X, pady=5)

        ttk.Label(filter_frame, text="Фильтр по категории:").pack(side=tk.LEFT, padx=5)
        self.filter_var = tk.StringVar(value="Все")
        self.filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var, 
                                         values=["Все"] + self.categories, state="readonly", width=15)
        self.filter_combo.pack(side=tk.LEFT, padx=5)
        self.filter_combo.bind("<<ComboboxSelected>>", self.on_filter_change)

        ttk.Button(gen_frame, text="Сгенерировать задачу", command=self.generate_task).pack(pady=10)

        self.result_label = ttk.Label(gen_frame, text="Нажмите кнопку, чтобы получить задачу", 
                                      font=("Arial", 12, "bold"), wraplength=500, justify="center")
        self.result_label.pack(pady=10)

        # --- Фрейм истории ---
        history_frame = ttk.LabelFrame(self.root, text="История задач", padding=10)
        history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(history_frame, columns=("date", "category", "task"), show="headings")
        self.tree.heading("date", text="Дата и время")
        self.tree.heading("category", text="Категория")
        self.tree.heading("task", text="Задача")

        self.tree.column("date", width=140, anchor=tk.CENTER)
        self.tree.column("category", width=100, anchor=tk.CENTER)
        self.tree.column("task", width=300, anchor=tk.W)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def add_task(self):
        task_text = self.new_task_entry.get().strip()
        category = self.new_task_category.get()

        # Валидация: не пустая строка
        if not task_text:
            messagebox.showerror("Ошибка", "Текст задачи не может быть пустым!")
            return

        # Проверка на дубликаты (опционально)
        if any(t["task"].lower() == task_text.lower() for t in self.tasks_pool):
            messagebox.showwarning("Внимание", "Такая задача уже есть в списке!")
            return

        new_task = {"task": task_text, "category": category}
        self.tasks_pool.append(new_task)
        self.save_data(self.tasks_file, self.tasks_pool)
        
        self.new_task_entry.delete(0, tk.END)
        messagebox.showinfo("Успех", f"Задача '{task_text}' успешно добавлена в пул!")

    def generate_task(self):
        current_filter = self.filter_var.get()
        
        # Фильтруем пул задач для генерации
        if current_filter == "Все":
            available_tasks = self.tasks_pool
        else:
            available_tasks = [t for t in self.tasks_pool if t["category"] == current_filter]

        if not available_tasks:
            messagebox.showinfo("Пусто", f"Нет доступных задач в категории '{current_filter}'. Добавьте новые!")
            return

        # Выбираем случайную задачу
        selected = random.choice(available_tasks)
        self.result_label.config(text=selected["task"])

        # Добавляем в историю
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        history_record = {
            "date": timestamp,
            "category": selected["category"],
            "task": selected["task"]
        }
        
        self.history.insert(0, history_record)
        self.save_data(self.history_file, self.history)
        self.update_history_table()

    def on_filter_change(self, event=None):
        # Обновляем таблицу истории при смене фильтра
        self.update_history_table()

    def update_history_table(self):
        # Очищаем таблицу
        for item in self.tree.get_children():
            self.tree.delete(item)

        current_filter = self.filter_var.get()

        # Заполняем таблицу с учетом фильтра
        for item in self.history:
            if current_filter == "Все" or item["category"] == current_filter:
                self.tree.insert("", tk.END, values=(item["date"], item["category"], item["task"]))

    def load_data(self, filename, default_data):
        if not os.path.exists(filename):
            return default_data
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return default_data

    def save_data(self, filename, data):
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    root = tk.Tk()
    app = RandomTaskGenerator(root)
    root.mainloop()