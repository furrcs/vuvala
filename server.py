from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List
import json
import os

app = FastAPI(title="Venv Manager API")

TEMPLATES_FILE = "templates.json"

class EnvironmentConfig(BaseModel):
    name: str
    packages: List[str]

def load_templates() -> Dict:
    if os.path.exists(TEMPLATES_FILE):
        with open(TEMPLATES_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_templates(templates: Dict):
    with open(TEMPLATES_FILE, 'w') as f:
        json.dump(templates, f, indent=2)

@app.get("/")
async def root():
    return {"message": "Venv Manager API"}

@app.get("/templates")
async def get_templates():
    return load_templates()

@app.post("/templates")
async def create_template(config: EnvironmentConfig):
    templates = load_templates()
    if config.name in templates:
        raise HTTPException(status_code=400, detail="Шаблон уже существует")
    templates[config.name] = config.packages
    save_templates(templates)
    return {"message": "Шаблон создан", "name": config.name}

@app.delete("/templates/{name}")
async def delete_template(name: str):
    templates = load_templates()
    if name not in templates:
        raise HTTPException(status_code=404, detail="Шаблон не найден")
    del templates[name]
    save_templates(templates)
    return {"message": "Шаблон удален"}