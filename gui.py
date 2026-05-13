import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from datetime import datetime
from env_manager import VenvManager
from pkg_manager import PackageManager
import requests

class VenvManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер виртуальных окружений Python")
        self.root.geometry("800x650")
        
        self.server_url = "http://127.0.0.1:8000"
        self.vm = VenvManager()
        self.pm = PackageManager(self.vm)
        
        self.setup_ui()
        self.refresh_venv_list()
        self.refresh_templates_list()
    
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
        
        # Вкладка шаблонов
        template_frame = ttk.Frame(notebook)
        notebook.add(template_frame, text="Шаблоны")
        self.setup_template_tab(template_frame)
        
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
        self.venv_listbox.bind('<<ListboxSelect>>', self.on_venv_select)
        
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Обновить список", command=self.refresh_venv_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Удалить", command=self.delete_venv).pack(side=tk.LEFT, padx=2)
        
        # Информация о выбранном окружении
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
        
        # Установка из шаблона
        template_install_frame = ttk.LabelFrame(parent, text="Установить из шаблона", padding=10)
        template_install_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(template_install_frame, text="Шаблон:").grid(row=0, column=0, sticky=tk.W)
        self.template_combo = ttk.Combobox(template_install_frame, width=25, state="readonly")
        self.template_combo.grid(row=0, column=1, padx=5)
        ttk.Button(template_install_frame, text="Загрузить", command=self.load_template).grid(row=0, column=2, padx=5)
        
        # Просмотр пакетов
        view_frame = ttk.LabelFrame(parent, text="Установленные пакеты", padding=10)
        view_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        btn_frame = ttk.Frame(view_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Показать пакеты", command=self.show_packages).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Сохранить как шаблон", command=self.save_as_template).pack(side=tk.LEFT, padx=2)
        
        self.pkg_display = scrolledtext.ScrolledText(view_frame, height=10, wrap=tk.WORD)
        self.pkg_display.pack(fill=tk.BOTH, expand=True)
    
    def setup_template_tab(self, parent):
        # Создание шаблона вручную
        create_frame = ttk.LabelFrame(parent, text="Создать новый шаблон", padding=10)
        create_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(create_frame, text="Название шаблона:").grid(row=0, column=0, sticky=tk.W)
        self.template_name_entry = ttk.Entry(create_frame, width=30)
        self.template_name_entry.grid(row=0, column=1, padx=5)
        
        ttk.Label(create_frame, text="Пакеты\n(через запятую):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.template_packages_entry = ttk.Entry(create_frame, width=50)
        self.template_packages_entry.grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(create_frame, text="Создать шаблон", command=self.create_template).grid(row=1, column=2, padx=5)
        
        # Список шаблонов
        list_frame = ttk.LabelFrame(parent, text="Шаблоны на сервере", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.template_listbox = tk.Listbox(list_frame, height=10)
        self.template_listbox.pack(fill=tk.BOTH, expand=True)
        self.template_listbox.bind('<<ListboxSelect>>', self.on_template_select)
        
        btn_frame = ttk.Frame(list_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="Обновить", command=self.refresh_templates_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Удалить шаблон", command=self.delete_template).pack(side=tk.LEFT, padx=2)
        
        # Детали шаблона
        detail_frame = ttk.LabelFrame(parent, text="Детали шаблона", padding=10)
        detail_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.template_detail = scrolledtext.ScrolledText(detail_frame, height=8, wrap=tk.WORD)
        self.template_detail.pack(fill=tk.BOTH, expand=True)
    
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
        
        # Обновляем комбобоксы
        self.pkg_env_combo['values'] = venvs
        if venvs:
            self.pkg_env_combo.set(venvs[0])
        
        self.log(f"Обновлен список окружений. Найдено: {len(venvs)}")
    
    def refresh_templates_list(self):
        """Обновление списка шаблонов с сервера"""
        try:
            response = requests.get(f"{self.server_url}/templates", timeout=5)
            if response.status_code == 200:
                templates = response.json()
                self.template_listbox.delete(0, tk.END)
                template_names = list(templates.keys())
                for name in sorted(template_names):
                    self.template_listbox.insert(tk.END, name)
                
                # Обновляем комбобокс с шаблонами
                self.template_combo['values'] = sorted(template_names)
                if template_names:
                    self.template_combo.set(template_names[0])
                
                self.log(f"Загружено шаблонов с сервера: {len(template_names)}")
            else:
                self.log("Ошибка получения шаблонов с сервера")
        except requests.ConnectionError:
            self.log("Сервер недоступен")
        except Exception as e:
            self.log(f"Ошибка: {str(e)}")
    
    def on_venv_select(self, event):
        """Обработчик выбора окружения"""
        selection = self.venv_listbox.curselection()
        if selection:
            name = self.venv_listbox.get(selection[0])
            self.env_info_label.config(text=f"Выбрано: {name}")
    
    def on_template_select(self, event):
        """Обработчик выбора шаблона"""
        selection = self.template_listbox.curselection()
        if selection:
            name = self.template_listbox.get(selection[0])
            try:
                response = requests.get(f"{self.server_url}/templates", timeout=5)
                if response.status_code == 200:
                    templates = response.json()
                    if name in templates:
                        packages = templates[name]
                        self.template_detail.delete(1.0, tk.END)
                        self.template_detail.insert(1.0, f"Шаблон: {name}\n\nПакеты:\n")
                        for i, pkg in enumerate(packages, 1):
                            self.template_detail.insert(tk.END, f"{i}. {pkg}\n")
            except Exception as e:
                self.log(f"Ошибка загрузки деталей: {str(e)}")
    
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
        """Загрузка шаблона в окружение"""
        venv_name = self.pkg_env_combo.get()
        template = self.template_combo.get()
        
        if not venv_name:
            messagebox.showwarning("Предупреждение", "Выберите окружение")
            return
        if not template:
            messagebox.showwarning("Предупреждение", "Выберите шаблон")
            return
        
        def load_thread():
            self.log(f"Загрузка шаблона '{template}' в '{venv_name}'...")
            msg = self.pm.install_from_template(venv_name, template, self.server_url)
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
    
    def save_as_template(self):
        """Сохранить список пакетов как шаблон"""
        venv_name = self.pkg_env_combo.get()
        
        if not venv_name:
            messagebox.showwarning("Предупреждение", "Выберите окружение")
            return
        
        # Получаем список пакетов
        success, packages_text = self.pm.list_packages(venv_name)
        if not success:
            messagebox.showerror("Ошибка", "Не удалось получить список пакетов")
            return
        
        # Парсим список пакетов (пропускаем заголовки)
        packages = []
        for line in packages_text.split('\n')[2:]:  # Пропускаем заголовки
            if line.strip():
                # Берем только имя пакета (первое слово)
                pkg_name = line.split()[0]
                packages.append(pkg_name)
        
        # Диалог создания шаблона
        dialog = tk.Toplevel(self.root)
        dialog.title("Сохранить как шаблон")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text="Название шаблона:").pack(pady=5)
        name_entry = ttk.Entry(dialog, width=40)
        name_entry.pack(pady=5)
        name_entry.insert(0, venv_name + "_template")
        
        ttk.Label(dialog, text="Пакеты для шаблона:").pack(pady=5)
        packages_text = tk.Text(dialog, height=10, width=40)
        packages_text.pack(pady=5)
        packages_text.insert(1.0, '\n'.join(packages))
        
        def save_template():
            template_name = name_entry.get().strip()
            if not template_name:
                messagebox.showwarning("Предупреждение", "Введите название шаблона")
                return
            
            packages_list = [p.strip() for p in packages_text.get(1.0, tk.END).split('\n') if p.strip()]
            
            try:
                response = requests.post(
                    f"{self.server_url}/templates",
                    json={"name": template_name, "packages": packages_list},
                    timeout=5
                )
                
                if response.status_code == 200:
                    self.log(f"Шаблон '{template_name}' создан успешно")
                    self.refresh_templates_list()
                    dialog.destroy()
                    messagebox.showinfo("Успех", f"Шаблон '{template_name}' создан")
                else:
                    messagebox.showerror("Ошибка", f"Ошибка сервера: {response.text}")
            except requests.ConnectionError:
                messagebox.showerror("Ошибка", "Сервер недоступен")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))
        
        ttk.Button(dialog, text="Сохранить", command=save_template).pack(pady=10)
    
    def create_template(self):
        """Создание нового шаблона вручную"""
        name = self.template_name_entry.get().strip()
        packages_str = self.template_packages_entry.get().strip()
        
        if not name:
            messagebox.showwarning("Предупреждение", "Введите название шаблона")
            return
        if not packages_str:
            messagebox.showwarning("Предупреждение", "Введите список пакетов")
            return
        
        packages_list = [p.strip() for p in packages_str.split(',') if p.strip()]
        
        try:
            response = requests.post(
                f"{self.server_url}/templates",
                json={"name": name, "packages": packages_list},
                timeout=5
            )
            
            if response.status_code == 200:
                self.log(f"Шаблон '{name}' создан успешно")
                self.template_name_entry.delete(0, tk.END)
                self.template_packages_entry.delete(0, tk.END)
                self.refresh_templates_list()
                messagebox.showinfo("Успех", f"Шаблон '{name}' создан")
            else:
                messagebox.showerror("Ошибка", f"Ошибка сервера: {response.text}")
        except requests.ConnectionError:
            messagebox.showerror("Ошибка", "Сервер недоступен")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
    
    def delete_template(self):
        """Удаление шаблона"""
        selection = self.template_listbox.curselection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите шаблон для удаления")
            return
        
        name = self.template_listbox.get(selection[0])
        
        if messagebox.askyesno("Подтверждение", f"Удалить шаблон '{name}'?"):
            try:
                response = requests.delete(
                    f"{self.server_url}/templates/{name}",
                    timeout=5
                )
                
                if response.status_code == 200:
                    self.log(f"Шаблон '{name}' удален")
                    self.refresh_templates_list()
                    self.template_detail.delete(1.0, tk.END)
                else:
                    messagebox.showerror("Ошибка", f"Ошибка сервера: {response.text}")
            except requests.ConnectionError:
                messagebox.showerror("Ошибка", "Сервер недоступен")
            except Exception as e:
                messagebox.showerror("Ошибка", str(e))