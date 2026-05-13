import tkinter as tk
import threading
import subprocess
import sys
import time
import os
from gui import VenvManagerGUI

def start_server():
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        
        subprocess.run(
            [sys.executable, "-m", "uvicorn", "server:app", "--host", "127.0.0.1", "--port", "8000"],
            cwd=current_dir,
            capture_output=True
        )
    except Exception as e:
        print(f"Ошибка сервера: {e}")

def main():
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    print("Запуск сервера...")
    time.sleep(2)

    print("Запуск GUI...")
    root = tk.Tk()
    app = VenvManagerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()