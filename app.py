from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import datetime
import random

app = Flask(__name__)
app.secret_key = 'ERDR_PRO_SECRET_KEY_2024'

# 🔐 24 АБСОЛЮТНО РІЗНИХ ПАРОЛЯ
USERS = {
    "gunp": [
        {"username": "gunp_admin", "password": "BlueDragon2024", "name": "Коваленко І.П.", "position": "Головний адміністратор ГУНП"},
        {"username": "gunp_director", "password": "PoliceGuard987", "name": "Петренко О.В.", "position": "Начальник управління"},
        {"username": "gunp_deputy", "password": "SecureBase555", "name": "Шевченко М.І.", "position": "Заступник начальника"},
    ],
    "sbu": [
        {"username": "sbu_admin", "password": "RedShadow2024", "name": "Мельник А.В.", "position": "Головний адміністратор СБУ"},
        {"username": "sbu_counter", "password": "CounterSpy789", "name": "Ковальчук С.М.", "position": "Начальник контррозвідки"},
    ],
    "prosecutor": [
        {"username": "proc_admin", "password": "GoldScale2024", "name": "Віскар М.М.", "position": "Головний адміністратор Прокуратури"},
        {"username": "proc_general", "password": "JusticeLord777", "name": "Кулебяка А.А.", "position": "Генеральний прокурор"},
    ]
}

# База данных дел
CASES_DATABASE = {
    "gunp": [],
    "sbu": [],
    "prosecutor": []
}

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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    agency = request.form.get('agency')
    
    print(f"Login attempt: {username} / {password} / {agency}")  # Debug
    
    user = None
    for u in USERS.get(agency, []):
        if u["username"] == username and u["password"] == password:
            user = u
            break
    
    if user:
        session['user'] = user
        session['agency'] = agency
        return redirect('/dashboard')
    else:
        return "Невірний логін або пароль! <a href='/'>Назад</a>"

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
    if 'user' not in session:
        return redirect('/')
    
    user = session.get('user')
    agency = session.get('agency')
    
    new_case = {
        "id": int(datetime.datetime.now().timestamp()),
        "number": request.form.get('number'),
        "title": request.form.get('title'),
        "description": request.form.get('description', ''),
        "category": request.form.get('category', 'criminal'),
        "priority": request.form.get('priority', 'medium'),
        "status": "new",
        "createdDate": datetime.datetime.now().strftime('%d.%m.%Y'),
        "createdBy": user['name'],
        "responsible": user['name'],
        "agency": agency
    }
    
    CASES_DATABASE[agency].append(new_case)
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == '__main__':
    initialize_test_data()
    print("🛡️ ЄРДР PRO System Initialized")
    print("👉 Open: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
