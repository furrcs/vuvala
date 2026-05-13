import subprocess
import logging
import sys
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VenvManager:
    def __init__(self, base_path: str = "venvs"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(exist_ok=True)
        logger.info(f"Базовая директория: {self.base_path.absolute()}")
    
    def create_venv(self, name: str) -> tuple:
        venv_path = self.base_path / name
        
        if venv_path.exists():
            return False, f"Окружение '{name}' уже существует"
        
        try:
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_path)],
                check=True,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            logger.info(f"Создано окружение: {venv_path}")
            
            if self._verify_venv(venv_path):
                return True, f"Окружение '{name}' создано успешно"
            else:
                return False, "Окружение создано, но проверка не пройдена"
                
        except subprocess.TimeoutExpired:
            return False, "Таймаут создания окружения"
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            logger.error(f"Ошибка создания venv: {error_msg}")
            return False, f"Ошибка создания: {error_msg}"
        except Exception as e:
            logger.error(f"Неожиданная ошибка: {e}")
            return False, f"Ошибка: {str(e)}"
    
    def _verify_venv(self, venv_path: Path) -> bool:
        if sys.platform == "win32":
            python_path = venv_path / "Scripts" / "python.exe"
        else:
            python_path = venv_path / "bin" / "python"
        
        return python_path.exists()
    
    def delete_venv(self, name: str) -> tuple:
        venv_path = self.base_path / name
        if not venv_path.exists():
            return False, f"Окружение '{name}' не найдено"
        
        try:
            import shutil
            shutil.rmtree(venv_path)
            logger.info(f"Удалено окружение: {venv_path}")
            return True, f"Окружение '{name}' удалено"
        except Exception as e:
            logger.error(f"Ошибка удаления: {e}")
            return False, f"Ошибка удаления: {str(e)}"
    
    def list_venvs(self) -> list:
        venvs = []
        if not self.base_path.exists():
            return venvs
            
        for d in self.base_path.iterdir():
            if d.is_dir() and self._verify_venv(d):
                venvs.append(d.name)
        return sorted(venvs)
    
    def get_pip_path(self, name: str) -> str:
        if sys.platform == "win32":
            return str(self.base_path / name / "Scripts" / "pip.exe")
        return str(self.base_path / name / "bin" / "pip")
    
    def get_python_path(self, name: str) -> str:
        if sys.platform == "win32":
            return str(self.base_path / name / "Scripts" / "python.exe")
        return str(self.base_path / name / "bin" / "python")