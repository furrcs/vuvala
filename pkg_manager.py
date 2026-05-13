import subprocess
import requests
import logging
from env_manager import VenvManager

logger = logging.getLogger(__name__)

class PackageManager:
    def __init__(self, venv_manager: VenvManager):
        self.vm = venv_manager
    
    def install_package(self, venv_name: str, package: str) -> tuple:
        pip_path = self.vm.get_pip_path(venv_name)

        venv_path = self.vm.base_path / venv_name
        if not venv_path.exists():
            return False, f"Окружение '{venv_name}' не найдено"
        
        try:
            subprocess.run(
                [pip_path, "install", package],
                check=True,
                capture_output=True,
                text=True,
                timeout=120
            )
            logger.info(f"Установлен пакет {package} в {venv_name}")
            return True, f"Пакет '{package}' установлен успешно"
        except subprocess.TimeoutExpired:
            return False, "Таймаут установки пакета"
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            logger.error(f"Ошибка установки: {error_msg}")
            
            if "No matching distribution found" in error_msg:
                return False, f"Пакет '{package}' не найден в PyPI"
            elif "Could not find a version" in error_msg:
                return False, f"Нет подходящей версии пакета '{package}'"
            else:
                return False, f"Ошибка установки: {error_msg[:200]}"
    
    def install_from_template(self, venv_name: str, template_name: str, server_url: str = "http://127.0.0.1:8000") -> str:
        try:
            response = requests.get(f"{server_url}/templates", timeout=5)
            if response.status_code == 200:
                templates = response.json()
                if template_name in templates:
                    packages = templates[template_name]
                    results = []
                    for package in packages:
                        success, msg = self.install_package(venv_name, package)
                        results.append(f"{'✓' if success else '✗'} {package}: {msg}")
                    return "\n".join(results)
                return f"Шаблон '{template_name}' не найден на сервере"
            return "Ошибка получения данных с сервера"
        except requests.ConnectionError:
            return "Сервер недоступен. Проверьте подключение"
        except requests.Timeout:
            return "Таймаут подключения к серверу"
        except Exception as e:
            return f"Ошибка: {str(e)}"
    
    def list_packages(self, venv_name: str) -> tuple:
        pip_path = self.vm.get_pip_path(venv_name)
        
        try:
            result = subprocess.run(
                [pip_path, "list", "--format=columns"],
                check=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, f"Ошибка получения списка: {e.stderr}"
        except Exception as e:
            return False, f"Ошибка: {str(e)}"