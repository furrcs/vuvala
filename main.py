import tkinter as tk
import threading
import subprocess
import sys
import time
import os
from gui import VenvManagerGUI

def start_server():
    """Запуск FastAPI сервера"""
    try:
        # Получаем абсолютный путь к server.py
        current_dir = os.path.dirname(os.path.abspath(__file__))
        server_path = os.path.join(current_dir, "server.py")
        
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=current_dir,
            capture_output=True
        )
    except Exception as e:
        print(f"Ошибка сервера: {e}")

def main():
    # Запуск сервера в отдельном потоке
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Небольшая задержка для запуска сервера
    print("Запуск сервера...")
    time.sleep(2)
    
    # Запуск GUI
    print("Запуск GUI...")
    root = tk.Tk()
    app = VenvManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()