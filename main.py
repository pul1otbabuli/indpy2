from fastapi import FastAPI, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import sqlite3
from typing import List
from pydantic import BaseModel
from lxml import etree

DATABASE_URL = "./court_cases.db"

app = FastAPI()
templates = Jinja2Templates(directory="templates")

def get_db():
    db = sqlite3.connect(DATABASE_URL)
    try:
        yield db
    finally:
        db.close()

class Case(BaseModel):
    case_id: int
    case_number: str
    opening_date: str
    description: str

class Party(BaseModel):
    party_id: int
    case_id: int
    name: str
    role: str
    contact_info: str

class Judge(BaseModel):
    judge_id: int
    name: str
    qualification: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Endpoint для получения всех дел
@app.get("/cases", response_model=List[Case])
async def get_all_cases(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("SELECT * FROM Cases")
    cases = [Case(**row) for row in cursor.fetchall()]
    return cases

# Endpoint для добавления нового дела
@app.post("/cases", response_class=HTMLResponse)
async def create_case(request: Request, case_number: str = Form(...), opening_date: str = Form(...), description: str = Form(...), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("INSERT INTO Cases (case_number, opening_date, description) VALUES (?, ?, ?)", (case_number, opening_date, description))
    db.commit()
    return HTMLResponse(content="Дело успешно добавлено", status_code=200)

@app.get("/cases/create", response_class=HTMLResponse)
async def create_case_form(request: Request):
    return templates.TemplateResponse("create_case_form.html", {"request": request})

# Endpoint для получения всех сторон
@app.get("/parties", response_model=List[Party])
async def get_all_parties(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("SELECT * FROM Parties")
    parties = [Party(**row) for row in cursor.fetchall()]
    return parties

# Endpoint для добавления новой стороны
@app.post("/parties", response_class=HTMLResponse)
async def create_party(request: Request, case_id: int = Form(...), name: str = Form(...), role: str = Form(...), contact_info: str = Form(...), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("INSERT INTO Parties (case_id, name, role, contact_info) VALUES (?, ?, ?, ?)", (case_id, name, role, contact_info))
    db.commit()
    return HTMLResponse(content="Сторона успешно добавлена", status_code=200)

@app.get("/parties/create", response_class=HTMLResponse)
async def create_party_form(request: Request):
    return templates.TemplateResponse("create_party_form.html", {"request": request})

# Endpoint для получения всех судей
@app.get("/judges", response_model=List[Judge])
async def get_all_judges(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("SELECT * FROM Judges")
    judges = [Judge(**row) for row in cursor.fetchall()]
    return judges

# Endpoint для добавления нового судьи
@app.post("/judges", response_class=HTMLResponse)
async def create_judge(request: Request, name: str = Form(...), qualification: str = Form(...), db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("INSERT INTO Judges (name, qualification) VALUES (?, ?)", (name, qualification))
    db.commit()
    return HTMLResponse(content="Судья успешно добавлен", status_code=200)

@app.get("/judges/create", response_class=HTMLResponse)
async def create_judge_form(request: Request):
    return templates.TemplateResponse("create_judge_form.html", {"request": request})

# Экспорт таблицы "Дела" в XML
@app.get("/export/cases")
async def export_cases(db: sqlite3.Connection = Depends(get_db)):
    cursor = db.execute("SELECT * FROM Cases")
    cases_data = cursor.fetchall()
    root = etree.Element("cases")
    for case in cases_data:
        case_element = etree.SubElement(root, "case")
        etree.SubElement(case_element, "case_id").text = str(case[0])
        etree.SubElement(case_element, "case_number").text = case[1]
        etree.SubElement(case_element, "opening_date").text = case[2]
        etree.SubElement(case_element, "description").text = case[3]

    xml_content = etree.tostring(root, pretty_print=True, encoding="UTF-8").decode()
    return HTMLResponse(content=f"<pre>{xml_content}</pre>", status_code=200)


# Импорт таблицы "Дела" из XML
@app.post("/import/cases", response_class=HTMLResponse)
async def import_cases(request: Request, db: sqlite3.Connection = Depends(get_db)):
    form_data = await request.form()
    xml_file = form_data["xml_file"].file.read()
    try:
        root = etree.fromstring(xml_file)
        cursor = db.cursor()
        cursor.execute("DELETE FROM Cases")  # Очищаем таблицу перед импортом
        for case_element in root.xpath("//case"):
            case_id = case_element.xpath("./case_id/text()")[0]
            case_number = case_element.xpath("./case_number/text()")[0]
            opening_date = case_element.xpath("./opening_date/text()")[0]
            description = case_element.xpath("./description/text()")[0]
            cursor.execute("INSERT INTO Cases (case_id, case_number, opening_date, description) VALUES (?, ?, ?, ?)",
                           (case_id, case_number, opening_date, description))
        db.commit()
        return HTMLResponse(content="Таблица 'Дела' успешно импортирована", status_code=200)
    except Exception as e:
        return HTMLResponse(content=f"Ошибка импорта XML: {e}", status_code=400)


@app.get("/import/cases/form", response_class=HTMLResponse)
async def import_cases_form(request: Request):
    return templates.TemplateResponse("import_cases_form.html", {"request": request})
