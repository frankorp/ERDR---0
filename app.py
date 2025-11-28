from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
import json
import datetime
import random
import os
from functools import wraps

app = Flask(__name__)
app.secret_key = 'ERDR_PRO_SECRET_KEY_2024'

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

# 🔥 СИСТЕМА ЛОГИРОВАНИЯ
SYSTEM_LOGS = {
    "logs": [],
    "securityAlerts": []
}

# Типы логов
LOG_TYPES = {
    "LOGIN": "login",
    "LOGOUT": "logout", 
    "CREATE_CASE": "create",
    "DELETE_CASE": "delete",
    "VIEW_CASE": "view",
    "EXPORT_DATA": "export",
    "SYSTEM": "system"
}

# Декоратор для проверки авторизации
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

def generate_random_ip():
    return f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}"

def log_action(log_type, action, details=None, user=None, agency=None):
    if details is None:
        details = {}
    
    log_entry = {
        "id": str(datetime.datetime.now().timestamp()) + str(random.random()),
        "timestamp": datetime.datetime.now().isoformat(),
        "type": log_type,
        "action": action,
        "details": details,
        "user": user["name"] if user else "Система",
        "username": user["username"] if user else "system",
        "agency": agency or session.get('agency', 'system'),
        "ip": generate_random_ip(),
        "user_agent": request.headers.get('User-Agent', 'Unknown')
    }
    
    SYSTEM_LOGS["logs"].insert(0, log_entry)
    
    # Сохраняем только последние 1000 логов
    if len(SYSTEM_LOGS["logs"]) > 1000:
        SYSTEM_LOGS["logs"] = SYSTEM_LOGS["logs"][:1000]
    
    return log_entry

def get_agency_data(agency):
    agencies = {
        "gunp": {"name": "ГУНП", "fullName": "Головне управління Національної поліції", "color": "#1e40af", "icon": "👮‍♂️"},
        "sbu": {"name": "СБУ", "fullName": "Служба Безпеки України", "color": "#dc2626", "icon": "🕵️‍♂️"},
        "prosecutor": {"name": "Прокуратура", "fullName": "Генеральна прокуратура України", "color": "#7c2d12", "icon": "⚖️"},
        "admin": {"name": "Адмін-панель", "fullName": "Панель адміністратора системи", "color": "#7e22ce", "icon": "👨‍💼"}
    }
    return agencies.get(agency, {})

def get_status_text(status):
    statuses = {
        "new": "Нова",
        "in-progress": "В роботі", 
        "completed": "Завершена",
        "closed": "Закрита"
    }
    return statuses.get(status, status)

def initialize_test_data():
    # Очищаем базу данных перед инициализацией
    for agency in CASES_DATABASE:
        CASES_DATABASE[agency] = []
    
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
    session['selected_agency'] = agency
    agency_data = get_agency_data(agency)
    users = USERS.get(agency, [])
    return jsonify({
        "success": True,
        "agency": agency_data,
        "users": users
    })

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    agency = data.get('agency')
    
    if not username or not password:
        return jsonify({"success": False, "message": "Будь ласка, заповніть всі поля!"})
    
    user = None
    for u in USERS.get(agency, []):
        if u["username"] == username and u["password"] == password:
            user = u
            break
    
    if user:
        session['user'] = user
        session['agency'] = agency
        session['logged_in'] = True
        
        log_action(LOG_TYPES["LOGIN"], "Успішний вхід в систему", {
            "username": username,
            "status": "success",
            "agency": agency
        }, user)
        
        return jsonify({
            "success": True,
            "message": f"Вітаємо, {user['name']}!",
            "user": user
        })
    else:
        log_action(LOG_TYPES["LOGIN"], "Невдала спроба входу", {
            "username": username,
            "status": "failed",
            "agency": agency
        })
        
        return jsonify({"success": False, "message": "Невірний логін або пароль!"})

@app.route('/logout')
def logout():
    if 'user' in session:
        user = session['user']
        log_action(LOG_TYPES["LOGOUT"], "Вихід з системи", {}, user)
    
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
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
                         critical_cases=critical_cases,
                         get_status_text=get_status_text,
                         get_agency_data=get_agency_data)

@app.route('/add_case', methods=['POST'])
@login_required
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
    
    log_action(LOG_TYPES["CREATE_CASE"], "Створення нової справи", {
        "caseNumber": new_case["number"],
        "caseTitle": new_case["title"],
        "category": new_case["category"],
        "priority": new_case["priority"]
    }, user)
    
    return jsonify({"success": True, "message": f"Справа '{new_case['title']}' успішно створена!"})

@app.route('/view_case/<int:case_id>')
@login_required
def view_case(case_id):
    agency = session.get('agency')
    user = session.get('user')
    
    case_item = next((c for c in CASES_DATABASE[agency] if c["id"] == case_id), None)
    
    if case_item:
        log_action(LOG_TYPES["VIEW_CASE"], "Перегляд справи", {
            "caseNumber": case_item["number"],
            "caseTitle": case_item["title"]
        }, user)
        
        return jsonify({"success": True, "case": case_item})
    
    return jsonify({"success": False, "message": "Справу не знайдено!"})

@app.route('/delete_case', methods=['POST'])
@login_required
def delete_case():
    data = request.get_json()
    case_id = data.get('case_id')
    prosecutor_username = data.get('prosecutor_username')
    prosecutor_password = data.get('prosecutor_password')
    
    agency = session.get('agency')
    user = session.get('user')
    
    if agency != "prosecutor":
        return jsonify({"success": False, "message": "Помилка доступу! Тільки прокуратура може видаляти справи."})
    
    # Проверка прокурора
    prosecutor = None
    for u in USERS["prosecutor"]:
        if u["username"] == prosecutor_username and u["password"] == prosecutor_password:
            prosecutor = u
            break
    
    if not prosecutor:
        return jsonify({"success": False, "message": "Невірний логін або пароль прокурора!"})
    
    # Удаление дела
    case_item = next((c for c in CASES_DATABASE[agency] if c["id"] == case_id), None)
    if case_item:
        CASES_DATABASE[agency] = [c for c in CASES_DATABASE[agency] if c["id"] != case_id]
        
        log_action(LOG_TYPES["DELETE_CASE"], "Видалення справи", {
            "caseNumber": case_item["number"],
            "caseTitle": case_item["title"],
            "confirmedBy": prosecutor["name"]
        }, user)
        
        return jsonify({"success": True, "message": f"Справу '{case_item['title']}' успішно видалено!"})
    
    return jsonify({"success": False, "message": "Справу не знайдено!"})

@app.route('/admin/logs')
@login_required
def admin_logs():
    if session.get('agency') != 'admin':
        return redirect(url_for('dashboard'))
    
    logs = SYSTEM_LOGS["logs"]
    
    # Фильтрация
    log_type = request.args.get('type', '')
    username = request.args.get('user', '')
    agency_filter = request.args.get('agency', '')
    
    filtered_logs = logs
    if log_type:
        filtered_logs = [log for log in filtered_logs if log['type'] == log_type]
    if username:
        filtered_logs = [log for log in filtered_logs if log['username'] == username]
    if agency_filter:
        filtered_logs = [log for log in filtered_logs if log['agency'] == agency_filter]
    
    # Уникальные пользователи для фильтра
    unique_users = list(set(log['username'] for log in logs))
    
    return render_template('admin_logs.html', 
                         logs=filtered_logs,
                         unique_users=unique_users,
                         LOG_TYPES=LOG_TYPES)

@app.route('/admin/export_logs')
@login_required
def export_logs():
    if session.get('agency') != 'admin':
        return jsonify({"success": False, "message": "Доступ заборонено!"})
    
    # Здесь можно реализовать экспорт в CSV
    # Пока просто возвращаем JSON
    return jsonify({
        "success": True,
        "logs": SYSTEM_LOGS["logs"],
        "message": "Логи готові для експорту"
    })

if __name__ == '__main__':
    initialize_test_data()
    
    # Системный лог при запуске
    log_action(LOG_TYPES["SYSTEM"], "Система запущена", {
        "version": "2.4.1",
        "timestamp": datetime.datetime.now().isoformat()
    })
    
    print("🛡️ ЄРДР PRO System Initialized")
    print("24 unique passwords + logging system loaded")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
