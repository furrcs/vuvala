import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from datetime import datetime
from env_manager import VenvManager
from pkg_manager import PackageManager

class VenvManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер виртуальных окружений Python")
        self.root.geometry("700x600")
        
        self.vm = VenvManager()
        self.pm = PackageManager(self.vm)
        
        self.setup_ui()
        self.refresh_venv_list()
    
    def setup_ui(self):
        # Заголовок
        header = ttk.Label(self.root, text="Python Venv Manager", font=('Arial', 14, 'bold'))
        header.pack(pady=10)
        
        # Notebook для вкладок
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Вкладка управления окружениями
        env_frame = ttk.Frame(notebook)
        notebook.add(env_frame, text="Окружения")
        self.setup_env_tab(env_frame)
        
        # Вкладка пакетов
        pkg_frame = ttk.Frame(notebook)
        notebook.add(pkg_frame, text="Пакеты")
        self.setup_pkg_tab(pkg_frame)
        
        # Вкладка логов
        log_frame = ttk.Frame(notebook)
        notebook.add(log_frame, text="Логи")
        self.setup_log_tab(log_frame)
    
    def setup_env_tab(self, parent):
        # Создание окружения
        create_frame = ttk.LabelFrame(parent, text="Создать окружение", padding=10)
        create_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(create_frame, text="Название:").pack(side=tk.LEFT)
        self.venv_name_entry = ttk.Entry(create_frame, width=30)
        self.venv_name_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(create_frame, text="Создать", command=self.create_venv).pack(side=tk.LEFT, padx=5)
        
        # Список окружений
        list_frame = ttk.LabelFrame(parent, text="Существующие окружения", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.venv_listbox = tk.Listbox(list_frame, height=10)
        self.venv_listbox.pack(fill=tk.BOTH, expand=True)
        
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Обновить список", command=self.refresh_venv_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_venv).pack(side=tk.LEFT, padx=2)
        
        # Информация
        self.env_info_label = ttk.Label(parent, text="Выберите окружение для просмотра информации", 
                                        foreground="gray")
        self.env_info_label.pack(pady=5)
    
    def setup_pkg_tab(self, parent):
        # Установка пакетов
        install_frame = ttk.LabelFrame(parent, text="Установить пакет", padding=10)
        install_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(install_frame, text="Окружение:").grid(row=0, column=0, sticky=tk.W)
        self.pkg_env_combo = ttk.Combobox(install_frame, width=25, state="readonly")
        self.pkg_env_combo.grid(row=0, column=1, padx=5)
        
        ttk.Label(install_frame, text="Пакет:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.pkg_entry = ttk.Entry(install_frame, width=30)
        self.pkg_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(install_frame, text="Установить", command=self.install_package).grid(row=1, column=2, padx=5)
        
        # Шаблоны
        template_frame = ttk.LabelFrame(parent, text="Загрузить из шаблона", padding=10)
        template_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(template_frame, text="Шаблон:").grid(row=0, column=0, sticky=tk.W)
        self.template_entry = ttk.Entry(template_frame, width=30)
        self.template_entry.grid(row=0, column=1, padx=5)
        ttk.Button(template_frame, text="Загрузить", command=self.load_template).grid(row=0, column=2, padx=5)
        
        # Просмотр пакетов
        view_frame = ttk.LabelFrame(parent, text="Просмотр пакетов", padding=10)
        view_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Button(view_frame, text="Показать установленные пакеты", 
                  command=self.show_packages).pack(pady=5)
        
        self.pkg_display = scrolledtext.ScrolledText(view_frame, height=10, wrap=tk.WORD)
        self.pkg_display.pack(fill=tk.BOTH, expand=True)
    
    def setup_log_tab(self, parent):
        self.log_text = scrolledtext.ScrolledText(parent, wrap=tk.WORD, font=('Courier', 9))
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        ttk.Button(parent, text="Очистить логи", command=self.clear_logs).pack(pady=5)
    
    def log(self, message):
        """Добавление сообщения в лог"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
    
    def clear_logs(self):
        self.log_text.delete(1.0, tk.END)
    
    def refresh_venv_list(self):
        """Обновление списка окружений"""
        self.venv_listbox.delete(0, tk.END)
        venvs = self.vm.list_venvs()
        for venv in venvs:
            self.venv_listbox.insert(tk.END, venv)
        
        # Обновляем комбобокс
        self.pkg_env_combo['values'] = venvs
        if venvs:
            self.pkg_env_combo.set(venvs[0])
        
        self.log(f"Обновлен список окружений. Найдено: {len(venvs)}")
    
    def get_selected_venv(self):
        """Получение выбранного окружения"""
        selection = self.venv_listbox.curselection()
        if selection:
            return self.venv_listbox.get(selection[0])
        return None
    
    def create_venv(self):
        """Создание нового окружения"""
        name = self.venv_name_entry.get().strip()
        if not name:
            messagebox.showwarning("Предупреждение", "Введите название окружения")
            return
        
        self.log(f"Создание окружения '{name}'...")
        success, msg = self.vm.create_venv(name)
        self.log(msg)
        
        if success:
            self.venv_name_entry.delete(0, tk.END)
            self.refresh_venv_list()
            messagebox.showinfo("Успех", msg)
        else:
            messagebox.showerror("Ошибка", msg)
    
    def delete_venv(self):
        """Удаление окружения"""
        name = self.get_selected_venv()
        if not name:
            messagebox.showwarning("Предупреждение", "Выберите окружение для удаления")
            return
        
        if messagebox.askyesno("Подтверждение", 
                               f"Вы уверены, что хотите удалить окружение '{name}'?\nЭто действие нельзя отменить!"):
            self.log(f"Удаление окружения '{name}'...")
            success, msg = self.vm.delete_venv(name)
            self.log(msg)
            self.refresh_venv_list()
    
    def install_package(self):
        """Установка пакета"""
        venv_name = self.pkg_env_combo.get()
        package = self.pkg_entry.get().strip()
        
        if not venv_name:
            messagebox.showwarning("Предупреждение", "Выберите окружение")
            return
        if not package:
            messagebox.showwarning("Предупреждение", "Введите название пакета")
            return
        
        def install_thread():
            self.log(f"Установка '{package}' в '{venv_name}'...")
            success, msg = self.pm.install_package(venv_name, package)
            self.root.after(0, lambda: self.log(msg))
            if not success:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", msg))
        
        threading.Thread(target=install_thread, daemon=True).start()
    
    def load_template(self):
        """Загрузка шаблона"""
        venv_name = self.pkg_env_combo.get()
        template = self.template_entry.get().strip()
        
        if not venv_name:
            messagebox.showwarning("Предупреждение", "Выберите окружение")
            return
        if not template:
            messagebox.showwarning("Предупреждение", "Введите имя шаблона")
            return
        
        def load_thread():
            self.log(f"Загрузка шаблона '{template}' в '{venv_name}'...")
            msg = self.pm.install_from_template(venv_name, template)
            self.root.after(0, lambda: self.log(msg))
        
        threading.Thread(target=load_thread, daemon=True).start()
    
    def show_packages(self):
        """Показать установленные пакеты"""
        venv_name = self.pkg_env_combo.get()
        
        if not venv_name:
            messagebox.showwarning("Предупреждение", "Выберите окружение")
            return
        
        success, msg = self.pm.list_packages(venv_name)
        self.pkg_display.delete(1.0, tk.END)
        
        if success:
            self.pkg_display.insert(1.0, f"Пакеты в '{venv_name}':\n{msg}")
            self.log(f"Показан список пакетов для '{venv_name}'")
        else:
            self.pkg_display.insert(1.0, f"Ошибка: {msg}")
            self.log(f"Ошибка получения пакетов: {msg}")