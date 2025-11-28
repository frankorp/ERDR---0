from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import datetime
import random
import json
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'ERDR_PRO_SECRET_KEY_2024'
app.template_folder = 'templates'

# 🔐 24 АБСОЛЮТНО РІЗНИХ ПАРОЛЯ
USERS = {
    "gunp": [
        {"username": "gunp_admin", "password": "BlueDragon2024", "name": "Коваленко І.П.", "position": "Головний адміністратор ГУНП"},
        {"username": "gunp_director", "password": "PoliceGuard987", "name": "Петренко О.В.", "position": "Начальник управління"},
        {"username": "gunp_deputy", "password": "SecureBase555", "name": "Шевченко М.І.", "position": "Заступник начальника"},
        {"username": "gunp_senior", "password": "Investigator777", "name": "Бондаренко С.П.", "position": "Старший слідчий"},
        {"username": "gunp_invest", "password": "CrimeHunter333", "name": "Сидоренко В.П.", "position": "Слідчий"},
        {"username": "gunp_oper", "password": "PatrolAgent111", "name": "Кравченко А.М.", "position": "Оперативник"},
        {"username": "gunp_analyst", "password": "DataAnalyzer999", "name": "Павленко І.В.", "position": "Аналітик"},
        {"username": "gunp_tech", "password": "TechSupport444", "name": "Ткачук Р.О.", "position": "Технічний спеціаліст"}
    ],
    "sbu": [
        {"username": "sbu_admin", "password": "RedShadow2024", "name": "Мельник А.В.", "position": "Головний адміністратор СБУ"},
        {"username": "sbu_counter", "password": "CounterSpy789", "name": "Ковальчук С.М.", "position": "Начальник контррозвідки"},
        {"username": "sbu_senior", "password": "SecretAgent456", "name": "Ткаченко І.П.", "position": "Старший оперуповноважений"},
        {"username": "sbu_oper", "password": "UnderCover123", "name": "Лисенко О.Р.", "position": "Оперуповноважений"},
        {"username": "sbu_cyber", "password": "CyberShield321", "name": "Шевчук М.С.", "position": "Кіберспеціаліст"},
        {"username": "sbu_analyst", "password": "IntelMaster654", "name": "Білий В.П.", "position": "Аналітик розвідки"},
        {"username": "sbu_security", "password": "SafeGuard987", "name": "Чорний О.І.", "position": "Спеціаліст безпеки"},
        {"username": "sbu_tech", "password": "TechWizard555", "name": "Зеленський П.М.", "position": "Технічний експерт"}
    ],
    "prosecutor": [
        {"username": "proc_admin", "password": "GoldScale2024", "name": "Віскар М.М.", "position": "Головний адміністратор Прокуратури"},
        {"username": "proc_general", "password": "JusticeLord777", "name": "Кулебяка А.А.", "position": "Генеральний прокурор"},
        {"username": "proc_deputy", "password": "LawMaster888", "name": "Маркієнко М.С.", "position": "Заступник прокурора"},
        {"username": "proc_senior", "password": "SeniorLaw555", "name": "Шмелев А.Є.", "position": "Старший прокурор"},
        {"username": "proc_dept", "password": "DeptChief333", "name": "Петров К.О.", "position": "Прокурор відділу"},
        {"username": "proc_assist", "password": "LegalAid111", "name": "Іванова Л.М.", "position": "Помічник прокурора"},
        {"username": "proc_criminal", "password": "CrimeLaw222", "name": "Семенюк В.І.", "position": "Прокурор-криміналіст"},
        {"username": "proc_super", "password": "Supervisor999", "name": "Козак Р.С.", "position": "Спеціаліст з нагляду"}
    ],
    "admin": [
        {"username": "system_admin", "password": "MasterControl2024", "name": "Системний адміністратор", "position": "Головний адміністратор"}
    ]
}

# База данных дел
CASES_DATABASE = {
    "gunp": [],
    "sbu": [],
    "prosecutor": []
}

# СИСТЕМА ЛОГИРОВАНИЯ
SYSTEM_LOGS = []

def initialize_test_data():
    CASES_DATABASE["gunp"].append({
        "id": 1,
        "number": "210/2024",
        "title": "Розкрадання коштів бюджету",
        "description": "Справа про розкрадання коштів місцевого бюджету",
        "category": "criminal",
        "priority": "high",
        "status": "in-progress",
        "createdDate": "15.01.2024",
        "createdBy": "Коваленко І.П.",
        "responsible": "Петренко О.В.",
        "agency": "gunp"
    })

    CASES_DATABASE["sbu"].append({
        "id": 2,
        "number": "СБУ-45/2024",
        "title": "Контррозвідувальна операція",
        "description": "Операція з виявлення іноземних агентів",
        "category": "operational",
        "priority": "critical",
        "status": "in-progress",
        "createdDate": "14.01.2024",
        "createdBy": "Мельник А.В.",
        "responsible": "Ковальчук С.М.",
        "agency": "sbu"
    })

    CASES_DATABASE["prosecutor"].append({
        "id": 3,
        "number": "П-789/2024",
        "title": "Нагляд за розслідуванням",
        "description": "Нагляд за дотриманням закону при розслідуванні",
        "category": "supervision",
        "priority": "medium",
        "status": "new",
        "createdDate": "16.01.2024",
        "createdBy": "Віскар М.М.",
        "responsible": "Кулебяка А.А.",
        "agency": "prosecutor"
    })

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/select_agency/<agency>')
def select_agency(agency):
    agencies = {
        "gunp": {"name": "ГУНП", "fullName": "Головне управління Національної поліції", "color": "#1e40af", "icon": "👮‍♂️"},
        "sbu": {"name": "СБУ", "fullName": "Служба Безпеки України", "color": "#dc2626", "icon": "🕵️‍♂️"},
        "prosecutor": {"name": "Прокуратура", "fullName": "Генеральна прокуратура України", "color": "#7c2d12", "icon": "⚖️"},
        "admin": {"name": "Адмін-панель", "fullName": "Панель адміністратора системи", "color": "#7e22ce", "icon": "👨‍💼"}
    }
    
    return jsonify({
        "success": True,
        "agency": agencies.get(agency),
        "users": USERS.get(agency, [])
    })

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    agency = data.get('agency')
    
    user = None
    for u in USERS.get(agency, []):
        if u["username"] == username and u["password"] == password:
            user = u
            break
    
    if user:
        session['user'] = user
        session['agency'] = agency
        session['logged_in'] = True
        
        return jsonify({
            "success": True,
            "message": f"Вітаємо, {user['name']}!",
            "user": user
        })
    else:
        return jsonify({"success": False, "message": "Невірний логін або пароль!"})

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    
    user = session.get('user')
    agency = session.get('agency')
    cases = CASES_DATABASE.get(agency, [])
    
    # Статистика
    total_cases = len(cases)
    active_cases = len([c for c in cases if c["status"] in ["new", "in-progress"]])
    critical_cases = len([c for c in cases if c["priority"] == "critical"])
    
    return render_template('dashboard.html', 
                         user=user,
                         agency=agency,
                         cases=cases,
                         total_cases=total_cases,
                         active_cases=active_cases,
                         critical_cases=critical_cases)

@app.route('/add_case', methods=['POST'])
def add_case():
    data = request.get_json()
    user = session.get('user')
    agency = session.get('agency')
    
    new_case = {
        "id": int(datetime.datetime.now().timestamp()),
        "number": data.get('number'),
        "title": data.get('title'),
        "description": data.get('description', ''),
        "category": data.get('category', 'criminal'),
        "priority": data.get('priority', 'medium'),
        "status": "new",
        "createdDate": datetime.datetime.now().strftime('%d.%m.%Y'),
        "createdBy": user['name'],
        "responsible": user['name'],
        "agency": agency
    }
    
    CASES_DATABASE[agency].append(new_case)
    
    return jsonify({"success": True, "message": f"Справа '{new_case['title']}' успішно створена!"})

@app.route('/get_cases')
def get_cases():
    agency = session.get('agency')
    cases = CASES_DATABASE.get(agency, [])
    return jsonify({"success": True, "cases": cases})

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    initialize_test_data()
    print("🛡️ ЄРДР PRO System Initialized")
    app.run(debug=True, host='0.0.0.0', port=5000)
