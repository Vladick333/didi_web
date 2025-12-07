import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.graph_objects as go
import textwrap
import json
from auth import init_auth_database, login_page
from sidebar_auth import create_auth_sidebar
# ========== БАЗА ДАННЫХ ==========
def get_db_connection():
    """Создает новое соединение с базой данных для каждого запроса"""
    return sqlite3.connect('grad_recruitment.db', check_same_thread=False)


def init_database():
    """Инициализация базы данных с расширенной структурой"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Основная таблица студентов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            course INTEGER NOT NULL,
            specialization TEXT NOT NULL,
            programming_languages TEXT,
            work_experience TEXT,
            portfolio_link TEXT,
            contact_number TEXT,
            document_id TEXT UNIQUE,
            email TEXT,
            gpa REAL,
            university TEXT DEFAULT 'Международный Университет Информационных Технологий',
            graduation_year INTEGER,
            is_active INTEGER DEFAULT 1,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица вакансий
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacancies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            position TEXT NOT NULL,
            specialization TEXT,
            required_course INTEGER,
            salary_range TEXT,
            description TEXT,
            requirements TEXT,
            contact_email TEXT,
            application_deadline DATE,
            is_active INTEGER DEFAULT 1,
            posted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица откликов на вакансии
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            vacancy_id INTEGER,
            application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'pending',
            cover_letter TEXT,
            FOREIGN KEY (student_id) REFERENCES students (id),
            FOREIGN KEY (vacancy_id) REFERENCES vacancies (id)
        )
    ''')

    # Таблица уведомлений
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            notification_type TEXT DEFAULT 'info'
        )
    ''')

    # Таблица отчетов о трудоустройстве
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employment_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            company_name TEXT,
            position TEXT,
            employment_date DATE,
            salary TEXT,
            report_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students (id)
        )
    ''')

    # Добавляем тестовые данные если таблицы пустые
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        # Добавляем тестовых студентов
        test_students = [
            ('Алиев Аскар Бауыржанович', 4, 'Информационные Системы', 'Python, SQL, Java',
             'Разработка веб-приложений на Django, участие в хакатонах',
             'https://github.com/askarali', '+7 701 123 4567', '123456789012',
             'askar@email.com', 3.8, 'Международный Университет Информационных Технологий', 2024, 1),
            ('Смирнова Анна Ивановна', 5, 'Компьютерные Науки', 'C++, Python, JavaScript',
             'Стажировка в ТОО "КазТех", разработка мобильного приложения',
             'https://github.com/annasm', '+7 777 987 6543', '987654321098',
             'anna@email.com', 3.9, 'Казахстанско-Британский Технический Университет', 2024, 1),
            ('Ким Александр Сергеевич', 6, 'Программная Инженерия', 'Java, Spring Boot, SQL',
             '2 года опыта в fintech компании, разработка backend систем',
             'https://github.com/alexkim', '+7 705 555 1234', '456789012345',
             'alex@email.com', 3.5, 'Назарбаев Университет', 2024, 1),
            ('Омарова Айгуль Даулетовна', 3, 'Data Science', 'Python, R, SQL, TensorFlow',
             'Исследовательский проект по машинному обучению, публикация в конференции',
             'https://github.com/aigul', '+7 707 777 8888', '789012345678',
             'aigul@email.com', 3.7, 'Евразийский Национальный Университет', 2025, 1),
        ]

        cursor.executemany('''
            INSERT INTO students 
            (full_name, course, specialization, programming_languages, work_experience, 
             portfolio_link, contact_number, document_id, email, gpa, university, graduation_year, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', test_students)

    cursor.execute("SELECT COUNT(*) FROM vacancies")
    if cursor.fetchone()[0] == 0:
        # Добавляем тестовые вакансии
        test_vacancies = [
            ('Kaspi Bank', 'Junior Java Developer', 'Программная Инженерия', 4,
             'от 300 000 KZT', 'Разработка backend систем для банковских приложений',
             'Java, Spring Boot, SQL, Git', 'hr@kaspi.kz', '2024-12-31'),
            ('One Technologies', 'Python Developer', 'Информационные Системы', 4,
             '350 000 - 500 000 KZT', 'Разработка микросервисов на Python',
             'Python, FastAPI, PostgreSQL, Docker', 'career@one.kz', '2024-12-15'),
            ('Chocofamily', 'Frontend Developer', 'Компьютерные Науки', 3,
             'от 280 000 KZT', 'Разработка пользовательских интерфейсов',
             'JavaScript, React, TypeScript, CSS', 'jobs@chocofamily.kz', '2024-11-30'),
            ('Beeline Kazakhstan', 'Data Analyst', 'Data Science', 5,
             '400 000 - 600 000 KZT', 'Анализ данных телеком оператора',
             'SQL, Python, Power BI, статистика', 'talent@beeline.kz', '2024-12-20'),
        ]

        cursor.executemany('''
            INSERT INTO vacancies 
            (company_name, position, specialization, required_course, salary_range,
             description, requirements, contact_email, application_deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', test_vacancies)

    conn.commit()
    conn.close()


# ========== CRUD ОПЕРАЦИИ ==========
class DatabaseManager:
    def __init__(self):
        pass

    def execute_query(self, query, params=()):
        """Выполняет SQL запрос с созданием нового соединения"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor
        finally:
            conn.close()

    def execute_read_query(self, query, params=()):
        """Выполняет SQL запрос на чтение"""
        conn = get_db_connection()
        try:
            return pd.read_sql_query(query, conn, params=params)
        finally:
            conn.close()

    # Студенты
    def insert_student(self, data):
        query = '''
            INSERT INTO students 
            (full_name, course, specialization, programming_languages, work_experience, 
             portfolio_link, contact_number, document_id, email, gpa, graduation_year, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.execute_query(query, data)
        return True

    def get_all_students(self):
        query = "SELECT * FROM students ORDER BY registration_date DESC"
        return self.execute_read_query(query)

    def get_student_by_id(self, student_id):
        query = "SELECT * FROM students WHERE id = ?"
        result = self.execute_read_query(query, (student_id,))
        if not result.empty:
            return result.iloc[0]
        return None

    def update_student(self, student_id, data):
        query = '''
            UPDATE students SET
            full_name = ?, course = ?, specialization = ?, programming_languages = ?,
            work_experience = ?, portfolio_link = ?, contact_number = ?, document_id = ?,
            email = ?, gpa = ?, graduation_year = ?, is_active = ?,
            last_update = CURRENT_TIMESTAMP
            WHERE id = ?
        '''
        self.execute_query(query, (*data, student_id))
        return True

    def delete_student(self, student_id):
        query = "DELETE FROM students WHERE id = ?"
        self.execute_query(query, (student_id,))
        return True

    # Вакансии
    def insert_vacancy(self, data):
        query = '''
            INSERT INTO vacancies 
            (company_name, position, specialization, required_course, salary_range,
             description, requirements, contact_email, application_deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.execute_query(query, data)
        return True

    def get_all_vacancies(self):
        query = "SELECT * FROM vacancies WHERE is_active = 1 ORDER BY posted_date DESC"
        return self.execute_read_query(query)

    # Отклики на вакансии
    def apply_for_vacancy(self, student_id, vacancy_id, cover_letter=""):
        query = '''
            INSERT INTO applications (student_id, vacancy_id, cover_letter)
            VALUES (?, ?, ?)
        '''
        self.execute_query(query, (student_id, vacancy_id, cover_letter))
        return True

    def get_applications(self):
        query = '''
            SELECT a.*, s.full_name, v.position, v.company_name 
            FROM applications a
            LEFT JOIN students s ON a.student_id = s.id
            LEFT JOIN vacancies v ON a.vacancy_id = v.id
            ORDER BY a.application_date DESC
        '''
        return self.execute_read_query(query)

    def update_application_status(self, application_id, status):
        query = '''
            UPDATE applications SET status = ? WHERE id = ?
        '''
        self.execute_query(query, (status, application_id))
        return True

    # Уведомления
    def add_notification(self, user_id, title, message, notification_type='info'):
        query = '''
            INSERT INTO notifications (user_id, title, message, notification_type)
            VALUES (?, ?, ?, ?)
        '''
        self.execute_query(query, (user_id, title, message, notification_type))
        return True

    def get_notifications(self, user_id=None):
        if user_id:
            query = "SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC"
            return self.execute_read_query(query, (user_id,))
        else:
            query = "SELECT * FROM notifications ORDER BY created_at DESC LIMIT 50"
            return self.execute_read_query(query)

    def mark_notification_as_read(self, notification_id):
        query = '''
            UPDATE notifications SET is_read = 1 WHERE id = ?
        '''
        self.execute_query(query, (notification_id,))
        return True

    # Отчеты о трудоустройстве
    def add_employment_report(self, student_id, company_name, position, employment_date, salary):
        query = '''
            INSERT INTO employment_reports (student_id, company_name, position, employment_date, salary)
            VALUES (?, ?, ?, ?, ?)
        '''
        self.execute_query(query, (student_id, company_name, position, employment_date, salary))
        return True

    def get_employment_reports(self):
        query = '''
            SELECT er.*, s.full_name, s.specialization 
            FROM employment_reports er
            LEFT JOIN students s ON er.student_id = s.id
            ORDER BY er.employment_date DESC
        '''
        return self.execute_read_query(query)

    # Статистика
    def get_statistics(self):
        query = '''
            SELECT 
                (SELECT COUNT(*) FROM students) as total_students,
                (SELECT COUNT(*) FROM students WHERE is_active = 1) as active_students,
                (SELECT COUNT(*) FROM vacancies WHERE is_active = 1) as active_vacancies,
                (SELECT COUNT(*) FROM applications) as total_applications,
                (SELECT COUNT(*) FROM employment_reports) as employed_students,
                (SELECT COUNT(*) FROM notifications WHERE is_read = 0) as unread_notifications
        '''
        result = self.execute_read_query(query)
        if not result.empty:
            return result.iloc[0]
        return pd.Series([0, 0, 0, 0, 0, 0],
                         index=['total_students', 'active_students', 'active_vacancies',
                                'total_applications', 'employed_students', 'unread_notifications'])


# ========== ГЛОБАЛЬНЫЕ НАСТРОЙКИ ==========
COURSE_OPTIONS = [1, 2, 3, 4, 5, 6]
SPECIALIZATION_OPTIONS = [
    "Информационные Системы", "Компьютерные Науки", "Программная Инженерия",
    "Кибербезопасность", "Data Science", "Искусственный Интеллект",
    "Веб-разработка", "Мобильная разработка", "DevOps", "Экономика"
]
LANGUAGE_OPTIONS = [
    "Python", "Java", "C++", "JavaScript", "TypeScript", "SQL",
    "R", "Go", "Swift", "Kotlin", "C#", "PHP", "HTML/CSS", "React", "Vue.js"
]
UNIVERSITY_OPTIONS = [
    "Международный Университет Информационных Технологий",
    "Казахстанско-Британский Технический Университет",
    "Назарбаев Университет",
    "Евразийский Национальный Университет",
    "Казахский Национальный Университет"
]


def init_session_state():
    """Инициализация состояния сессии"""
    defaults = {
        'page': 'dashboard',
        'edit_mode': False,
        'current_student_id': None,
        'current_vacancy_id': None,
        'db_manager': DatabaseManager()
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Инициализируем основную базу
    init_database()

    # --- ИСПРАВЛЕНИЕ ---
    # Делаем импорт прямо тут, чтобы Python точно увидел функцию
    from auth import init_auth_database
    init_auth_database()
    # -------------------


# ========== НОВЫЙ СТИЛЬ - ФИОЛЕТОВЫЙ КИБЕРПАНК ==========
def apply_custom_styles():
    st.set_page_config(
        page_title="🎓 Graduate Recruitment System",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    st.markdown("""
    <style>
    /* ФИОЛЕТОВЫЙ КИБЕРПАНК ТЕМА */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Orbitron:wght@400;500;700;900&display=swap');

    :root {
        --neon-purple: #9d4edd;
        --neon-pink: #ff00ff;
        --neon-blue: #00e5ff;
        --dark-bg: #0a0a1a;
        --card-bg: #14142b;
        --text-light: #ffffff;
        --text-dim: #b8b8d1;
        --accent: #7b2cbf;
        --success: #00ff88;
        --warning: #ffaa00;
        --danger: #ff3860;
    }

    * {
        font-family: 'Inter', sans-serif;
    }

    h1, h2, h3, h4, .stButton > button, .neon-title {
        font-family: 'Orbitron', sans-serif !important;
        font-weight: 700;
    }

    /* Главный контейнер */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #0f0f23 100%);
        color: var(--text-light);
        background-attachment: fixed;
    }

    /* Неоновый заголовок */
    .main-header {
        background: rgba(20, 20, 43, 0.8);
        backdrop-filter: blur(10px);
        border: 1px solid var(--neon-purple);
        border-radius: 20px;
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 0 30px rgba(157, 78, 221, 0.3),
                    inset 0 0 20px rgba(157, 78, 221, 0.1);
        position: relative;
        overflow: hidden;
    }

    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, 
            transparent, 
            var(--neon-pink), 
            var(--neon-purple), 
            var(--neon-blue), 
            transparent);
    }

    .main-header h1 {
        background: linear-gradient(90deg, #9d4edd, #ff00ff, #00e5ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        margin: 0;
        text-shadow: 0 0 20px rgba(157, 78, 221, 0.5);
        animation: glow 2s ease-in-out infinite alternate;
    }

    @keyframes glow {
        from { text-shadow: 0 0 20px rgba(157, 78, 221, 0.5); }
        to { text-shadow: 0 0 30px rgba(255, 0, 255, 0.7), 0 0 40px rgba(0, 229, 255, 0.4); }
    }

    /* Карточки метрик */
    .metric-card {
        background: rgba(20, 20, 43, 0.8);
        border: 1px solid rgba(157, 78, 221, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(5px);
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    }

    .metric-card:hover {
        transform: translateY(-5px);
        border-color: var(--neon-purple);
        box-shadow: 0 10px 25px rgba(157, 78, 221, 0.4);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 900;
        background: linear-gradient(90deg, #9d4edd, #ff00ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0.5rem 0;
    }

    .metric-label {
        color: var(--text-dim);
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Кнопки - ОСНОВНЫЕ */
    .stButton > button {
        background: linear-gradient(135deg, #9d4edd, #7b2cbf) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 700 !important;
        font-size: 16px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 5px 15px rgba(157, 78, 221, 0.4) !important;
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
        transition: left 0.5s ease;
    }

    .stButton > button:hover {
        transform: translateY(-3px) !important;
        box-shadow: 0 8px 25px rgba(157, 78, 221, 0.6) !important;
        background: linear-gradient(135deg, #7b2cbf, #9d4edd) !important;
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    .stButton > button:active {
        transform: scale(0.98) !important;
    }

    /* Кнопки вторичные */
    .stButton > button[kind="secondary"] {
        background: rgba(20, 20, 43, 0.8) !important;
        border: 2px solid var(--neon-purple) !important;
        color: var(--neon-purple) !important;
    }

    .stButton > button[kind="secondary"]:hover {
        background: var(--neon-purple) !important;
        color: white !important;
    }

    /* Поля ввода (ФОРМЫ) - ЯРКИЕ И ВИДИМЫЕ */
    .stTextInput > div > div > input,
    .stSelectbox > div > button,
    .stMultiSelect > div > div > div,
    .stTextArea > div > textarea,
    .stNumberInput > div > div > input {
        background: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
        border: 2px solid rgba(157, 78, 221, 0.3) !important;
        border-radius: 10px !important;
        padding: 12px 16px !important;
        font-size: 16px !important;
        backdrop-filter: blur(5px);
    }

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > button:focus,
    .stMultiSelect > div > div > div:focus,
    .stTextArea > div > textarea:focus {
        border-color: var(--neon-purple) !important;
        box-shadow: 0 0 0 3px rgba(157, 78, 221, 0.2) !important;
        outline: none !important;
    }

    /* Цвет текста в селекторах */
    .stSelectbox > div > button > div > div > div {
        color: white !important;
    }

    /* Чекбоксы и радиокнопки */
    .stCheckbox > label, .stRadio > label {
        color: var(--text-light) !important;
        font-weight: 500;
    }

    /* Карточки контента */
    .content-card {
        background: rgba(20, 20, 43, 0.8);
        border: 1px solid rgba(157, 78, 221, 0.3);
        border-radius: 15px;
        padding: 2rem;
        margin-bottom: 1.5rem;
        backdrop-filter: blur(5px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
    }

    /* САЙДБАР - ИСПРАВЛЕННЫЙ С ФИКСИРОВАННЫМ РАЗМЕРОМ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, 
            rgba(10, 10, 26, 0.98) 0%, 
            rgba(20, 20, 43, 0.98) 50%,
            rgba(10, 10, 26, 0.95) 100%) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 3px solid var(--neon-purple) !important;
        box-shadow: 5px 0 25px rgba(157, 78, 221, 0.4) !important;
        position: fixed !important;
        height: 100vh !important;
        overflow-y: auto !important;
        z-index: 1000 !important;
        transition: transform 0.3s ease-in-out !important;

        /* СТРОГО фиксированные размеры */
        min-width: 300px !important;
        max-width: 300px !important;
        width: 300px !important;
    }

    /* Кнопка сворачивания - СТАБИЛЬНАЯ */
    button[kind="header"] {
        background: linear-gradient(135deg, #9d4edd, #ff00ff) !important;
        border: 2px solid #ffffff !important;
        border-radius: 50% !important;
        color: white !important;
        box-shadow: 0 0 20px rgba(157, 78, 221, 0.8), 
                    0 0 30px rgba(255, 0, 255, 0.5) !important;

        position: fixed !important;
        top: 50% !important;
        z-index: 1001 !important;

        width: 45px !important;
        height: 45px !important;
        min-width: 45px !important;
        min-height: 45px !important;

        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
        transition: all 0.3s ease !important;
        animation: pulseButton 2s infinite !important;
    }

    /* Сайдбар ОТКРЫТ - кнопка справа от него */
    section[data-testid="stSidebar"][aria-expanded="true"] ~ div button[kind="header"],
    section[data-testid="stSidebar"][aria-expanded="true"] + div button[kind="header"] {
        left: 285px !important;
        transform: translateY(-50%) !important;
    }

    /* Сайдбар ЗАКРЫТ - кнопка слева */
    section[data-testid="stSidebar"][aria-expanded="false"] ~ div button[kind="header"],
    section[data-testid="stSidebar"][aria-expanded="false"] + div button[kind="header"] {
        left: 10px !important;
        transform: translateY(-50%) !important;
    }

    /* Анимация кнопки */
    @keyframes pulseButton {
        0% { box-shadow: 0 0 20px rgba(157, 78, 221, 0.8), 0 0 30px rgba(255, 0, 255, 0.5); }
        50% { box-shadow: 0 0 30px rgba(157, 78, 221, 0.9), 0 0 40px rgba(255, 0, 255, 0.7); }
        100% { box-shadow: 0 0 20px rgba(157, 78, 221, 0.8), 0 0 30px rgba(255, 0, 255, 0.5); }
    }

    button[kind="header"]:hover {
        background: linear-gradient(135deg, #ff00ff, #9d4edd) !important;
        transform: translateY(-50%) scale(1.15) !important;
        box-shadow: 0 0 40px rgba(157, 78, 221, 1), 
                    0 0 50px rgba(255, 0, 255, 0.9) !important;
    }

    /* Иконка в кнопке */
    button[kind="header"] svg {
        fill: white !important;
        stroke: white !important;
        stroke-width: 2px !important;
        width: 20px !important;
        height: 20px !important;
    }

    /* Кнопки внутри сайдбара */
    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        margin-bottom: 10px !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(157, 78, 221, 0.4) !important;
        color: #e0e0e0 !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        border-radius: 12px !important;
        padding: 12px 16px !important;
        text-align: left !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(90deg, var(--neon-purple), var(--neon-pink)) !important;
        color: white !important;
        border-color: white !important;
        transform: translateX(5px) !important;
        box-shadow: 0 5px 20px rgba(157, 78, 221, 0.5) !important;
    }

    [data-testid="stSidebar"] .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #9d4edd, #7b2cbf) !important;
        color: white !important;
        border: 1px solid white !important;
        box-shadow: 0 0 15px rgba(157, 78, 221, 0.6) !important;
    }

    /* Убираем желтые предупреждения Streamlit */
    .stAlert[kind="warning"],
    .stAlert[kind="info"],
    .element-container:has(> .stAlert),
    div[data-testid="stDecoration"],
    div[data-testid="stToolbar"],
    div[data-testid="stStatusWidget"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        opacity: 0 !important;
        pointer-events: none !important;
    }

    /* Скрываем стандартные уведомления "Последняя активность" */
    div[data-testid="stAppViewContainer"] > div:first-child > div:first-child > div:first-child > div:first-child,
    .st-emotion-cache-1v0mbdj,
    .st-emotion-cache-16idsys {
        display: none !important;
    }

    /* Таблицы */
    .dataframe {
        background: rgba(20, 20, 43, 0.8) !important;
        border: 1px solid rgba(157, 78, 221, 0.3) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
    }

    .dataframe th {
        background: rgba(157, 78, 221, 0.2) !important;
        color: var(--neon-purple) !important;
        font-weight: 700 !important;
        border: none !important;
    }

    .dataframe td {
        color: var(--text-light) !important;
        border-color: rgba(157, 78, 221, 0.1) !important;
    }

    /* Информационные блоки */
    .stAlert {
        background: rgba(20, 20, 43, 0.9) !important;
        border: 1px solid !important;
        border-radius: 10px !important;
        backdrop-filter: blur(10px);
    }

    .stAlert[kind="success"] {
        border-color: var(--success) !important;
        color: var(--success) !important;
    }

    .stAlert[kind="error"] {
        border-color: var(--danger) !important;
        color: var(--danger) !important;
    }

    /* Прогресс-бары */
    .stProgress > div > div {
        background: linear-gradient(90deg, var(--neon-purple), var(--neon-pink)) !important;
        box-shadow: 0 0 10px var(--neon-purple);
    }

    /* Скрываем лишние элементы Streamlit */
    #MainMenu { 
        visibility: hidden !important;
        display: none !important; 
    }
    footer { 
        visibility: hidden !important;
        display: none !important; 
    }
    header { 
        visibility: hidden !important;
        display: none !important; 
    }

    /* Анимации */
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .slide-in {
        animation: slideIn 0.5s ease-out;
    }

    /* Статусные бейджи */
    .status-badge {
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }

    .status-pending { 
        background: rgba(255, 170, 0, 0.2); 
        color: var(--warning); 
        border: 1px solid var(--warning); 
    }
    .status-accepted { 
        background: rgba(0, 255, 136, 0.2); 
        color: var(--success); 
        border: 1px solid var(--success); 
    }
    .status-rejected { 
        background: rgba(255, 56, 96, 0.2); 
        color: var(--danger); 
        border: 1px solid var(--danger); 
    }
    .status-completed { 
        background: rgba(157, 78, 221, 0.2); 
        color: var(--neon-purple); 
        border: 1px solid var(--neon-purple); 
    }

    /* Заголовки в сайдбаре */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4 {
        color: #f0f0f0 !important;
        text-shadow: 0 2px 4px rgba(0,0,0,0.5);
    }

    /* Разделители в сайдбаре */
    [data-testid="stSidebar"] hr {
        border-color: rgba(157, 78, 221, 0.5) !important;
        margin: 20px 0 !important;
    }

    /* Основной контент с отступом под сайдбар */
    .main-content {
        margin-left: 300px;
        transition: margin-left 0.3s ease-in-out;
    }

    /* Когда сайдбар закрыт */
    section[data-testid="stSidebar"][aria-expanded="false"] + .main-content,
    section[data-testid="stSidebar"][aria-expanded="false"] ~ .main-content {
        margin-left: 0;
    }

    /* Кастомный скроллбар */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: rgba(20, 20, 43, 0.5);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #9d4edd, #7b2cbf);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #7b2cbf, #9d4edd);
    }
    </style>
    """, unsafe_allow_html=True)

    # JavaScript для улучшения работы
    js_code = """
    <script>
    // Убираем все предупреждения Streamlit
    document.addEventListener('DOMContentLoaded', function() {
        function hideStreamlitWarnings() {
            // Все возможные элементы предупреждений
            const warningSelectors = [
                '.stAlert',
                '.st-emotion-cache-1v0mbdj',
                '.st-emotion-cache-16idsys',
                '[data-testid="stDecoration"]',
                '[data-testid="stToolbar"]',
                '[data-testid="stStatusWidget"]',
                'div[class*="warning"]',
                'div[class*="info"]:not(.content-card)'
            ];

            warningSelectors.forEach(selector => {
                document.querySelectorAll(selector).forEach(el => {
                    if (el.textContent.includes('Последняя активность') || 
                        el.textContent.includes('Активные вакансии') ||
                        el.textContent.includes('Новые студенты')) {
                        el.style.display = 'none';
                        el.style.visibility = 'hidden';
                        el.style.height = '0';
                        el.style.opacity = '0';
                        el.style.pointerEvents = 'none';
                    }
                });
            });
        }

        // Сначала скрываем
        hideStreamlitWarnings();

        // Периодически проверяем (на случай динамической загрузки)
        setInterval(hideStreamlitWarnings, 1000);

        // Добавляем класс для основного контента
        const appContainer = document.querySelector('[data-testid="stAppViewContainer"]');
        if (appContainer) {
            const mainBlock = appContainer.querySelector('.main');
            if (mainBlock && mainBlock.querySelector('.block-container')) {
                const blockContainer = mainBlock.querySelector('.block-container');
                if (!blockContainer.classList.contains('main-content')) {
                    blockContainer.classList.add('main-content');
                }
            }
        }
    });
    </script>
    """
    st.components.v1.html(js_code, height=0)


# ========== КОМПОНЕНТЫ ИНТЕРФЕЙСА ==========
def create_header():
    """Создает неоновый заголовок"""
    st.markdown("""
    <div class="main-header slide-in">
        <h1>🎓 GRADUATE RECRUITMENT SYSTEM</h1>
        <p style="color: var(--text-dim); margin-top: 10px; font-size: 1.1rem;">
            Информационная система для трудоустройства выпускников университета
        </p>
    </div>
    """, unsafe_allow_html=True)


def metric_card(title, value, icon="📊", delta=None):
    """Создает карточку с метрикой"""
    st.markdown(f"""
    <div class="metric-card slide-in">
        <div style="font-size: 2.5rem; margin-bottom: 10px; color: var(--neon-purple);">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
        {f'<div style="color: var(--success); font-size: 0.9rem; margin-top: 5px;">{delta}</div>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)


# ========== НОВЫЕ СТРАНИЦЫ ==========
def notifications_page():
    """Страница уведомлений"""
    st.header("🔔 Уведомления")

    try:
        notifications = st.session_state.db_manager.get_notifications()

        if not notifications.empty:
            unread_count = len(notifications[notifications['is_read'] == 0])

            if unread_count > 0:
                st.markdown(f"""
                <div class="content-card">
                    <h3 style="color: var(--neon-purple);">
                        📬 Новых уведомлений: <span style="color: var(--danger);">{unread_count}</span>
                    </h3>
                </div>
                """, unsafe_allow_html=True)

            # Отображение уведомлений
            for _, notification in notifications.iterrows():
                with st.container():
                    bg_color = "rgba(157, 78, 221, 0.1)" if notification['is_read'] == 0 else "rgba(20, 20, 43, 0.8)"
                    border_color = "var(--neon-purple)" if notification['is_read'] == 0 else "rgba(157, 78, 221, 0.3)"

                    st.markdown(f"""
                    <div style="background: {bg_color}; border: 1px solid {border_color}; 
                            border-radius: 10px; padding: 15px; margin-bottom: 10px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <h4 style="margin: 0; color: var(--neon-purple);">{notification['title']}</h4>
                            <span style="color: var(--text-dim); font-size: 0.9rem;">
                                {notification['created_at'][:16]}
                            </span>
                        </div>
                        <p style="margin: 10px 0 0 0; color: var(--text-light);">{notification['message']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Кнопка "Прочитано"
                    if notification['is_read'] == 0:
                        col1, col2 = st.columns([1, 5])
                        with col1:
                            if st.button("✓ Прочитано", key=f"read_{notification['id']}"):
                                st.session_state.db_manager.mark_notification_as_read(notification['id'])
                                st.success("Уведомление отмечено как прочитанное!")
                                st.rerun()
                        st.markdown("---")
        else:
            st.info("📭 У вас пока нет уведомлений")
    except Exception as e:
        st.error(f"Ошибка при загрузке уведомлений: {e}")

    # Кнопка тестового уведомления
    if st.button("➕ Добавить тестовое уведомление", type="secondary"):
        st.session_state.db_manager.add_notification(
            1,
            "Тестовое уведомление",
            "Это тестовое уведомление для демонстрации работы системы",
            "info"
        )
        st.success("✅ Тестовое уведомление добавлено!")
        st.rerun()
    if st.button("🏠 В главное меню", use_container_width=True, type="secondary"):
        st.session_state.page = 'dashboard'
        st.rerun()


def employment_reports_page():
    """Страница отчетов о трудоустройстве"""
    st.header("📊 Отчеты о трудоустройстве")

    try:
        reports = st.session_state.db_manager.get_employment_reports()

        if not reports.empty:
            # Статистика
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Всего трудоустроено", len(reports))
            with col2:
                # ИСПРАВЛЕННЫЙ РАСЧЕТ СРЕДНЕЙ ЗАРПЛАТЫ
                try:
                    # Функция для извлечения числа из строки зарплаты
                    def extract_salary(salary_str):
                        if pd.isna(salary_str):
                            return 0

                        # Преобразуем в строку
                        salary_str = str(salary_str)

                        # Ищем числа в строке
                        import re
                        # Ищем все числа в строке (включая с запятыми)
                        numbers = re.findall(r'[\d,]+(?:\.\d+)?', salary_str)

                        if numbers:
                            # Берем первое найденное число
                            first_num = numbers[0].replace(',', '')
                            try:
                                return float(first_num)
                            except:
                                return 0
                        return 0

                    # Применяем функцию ко всем зарплатам
                    salaries = reports['salary'].apply(extract_salary)

                    # Фильтруем нулевые значения
                    valid_salaries = salaries[salaries > 0]

                    if len(valid_salaries) > 0:
                        avg_salary = valid_salaries.mean()
                        st.metric("Средняя зарплата", f"{avg_salary:,.0f} KZT")
                    else:
                        st.metric("Средняя зарплата", "Нет данных")
                except Exception as e:
                    st.metric("Средняя зарплата", "Ошибка")
                    st.caption(f"Ошибка расчета: {str(e)}")

            with col3:
                try:
                    latest_date = pd.to_datetime(reports['employment_date']).max()
                    st.metric("Последнее трудоустройство", latest_date.strftime('%d.%m.%Y'))
                except:
                    st.metric("Последнее трудоустройство", "Нет данных")

            # Таблица отчетов
            st.subheader("📋 История трудоустройства")

            # Показываем зарплаты как есть
            display_cols = ['full_name', 'company_name', 'position', 'employment_date', 'salary']
            st.dataframe(
                reports[display_cols].rename(columns={
                    'full_name': 'Студент',
                    'company_name': 'Компания',
                    'position': 'Должность',
                    'employment_date': 'Дата трудоустройства',
                    'salary': 'Зарплата'
                }),
                use_container_width=True,
                hide_index=True
            )

            # Дополнительная информация о зарплатах
            with st.expander("📊 Детальная статистика по зарплатам"):
                if 'salary' in reports.columns:
                    st.write("**Примеры записей зарплат:**")
                    for i, salary in enumerate(reports['salary'].head(5)):
                        st.write(f"{i + 1}. `{salary}`")

                    # Показываем статистику по зарплатам
                    try:
                        salaries_numeric = reports['salary'].apply(extract_salary)
                        valid_salaries = salaries_numeric[salaries_numeric > 0]

                        if len(valid_salaries) > 0:
                            st.write(f"**Корректных записей:** {len(valid_salaries)} из {len(reports)}")
                            col_s1, col_s2, col_s3 = st.columns(3)
                            with col_s1:
                                st.metric("Мин. зарплата", f"{valid_salaries.min():,.0f} KZT")
                            with col_s2:
                                st.metric("Медиана", f"{valid_salaries.median():,.0f} KZT")
                            with col_s3:
                                st.metric("Макс. зарплата", f"{valid_salaries.max():,.0f} KZT")
                    except:
                        st.warning("Не удалось проанализировать зарплаты")
        else:
            st.info("📝 Пока нет отчетов о трудоустройстве")
    except Exception as e:
        st.error(f"Ошибка при загрузке отчетов: {e}")

    # Форма добавления отчета - ТАКЖЕ ИСПРАВИТЬ ПОДСКАЗКУ
    with st.expander("➕ Добавить отчет о трудоустройстве"):
        st.info("💡 **Формат зарплаты:** '300 000 KZT' или '400 000-500 000 KZT' или 'от 350 000 KZT'")

        with st.form(key="employment_report_form"):
            col1, col2 = st.columns(2)

            with col1:
                students = st.session_state.db_manager.get_all_students()
                student_options = {row['id']: row['full_name'] for _, row in students.iterrows()}
                selected_student = st.selectbox("Выберите студента", options=list(student_options.keys()),
                                                format_func=lambda x: student_options[x])

                company_name = st.text_input("Название компании")

            with col2:
                position = st.text_input("Должность")
                employment_date = st.date_input("Дата трудоустройства")
                salary = st.text_input("Зарплата", placeholder="Например: 400 000 KZT",
                                       help="Укажите в формате: '400 000 KZT' или '350 000-500 000 KZT'")

            submitted = st.form_submit_button("📤 Добавить отчет")

            if submitted:
                if all([selected_student, company_name, position, salary]):
                    try:
                        st.session_state.db_manager.add_employment_report(
                            selected_student, company_name, position,
                            employment_date.strftime('%Y-%m-%d'), salary
                        )
                        st.success("✅ Отчет о трудоустройстве добавлен!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Ошибка: {str(e)}")
                else:
                    st.warning("⚠️ Пожалуйста, заполните все поля")

    # Кнопка "В главное меню"
    if st.button("🏠 В главное меню", use_container_width=True, type="secondary"):
        st.session_state.page = 'dashboard'
        st.rerun()


def applications_page():
    """Страница откликов на вакансии"""
    st.header("📨 Отклики на вакансии")

    try:
        applications = st.session_state.db_manager.get_applications()

        if not applications.empty:
            # Статистика по статусам
            status_counts = applications['status'].value_counts()

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Всего откликов", len(applications))
            with col2:
                pending = status_counts.get('pending', 0)
                st.metric("Ожидают", pending, delta=f"{pending} на рассмотрении")
            with col3:
                accepted = status_counts.get('accepted', 0)
                st.metric("Приняты", accepted, delta=f"{accepted} принято")
            with col4:
                rejected = status_counts.get('rejected', 0)
                st.metric("Отклонены", rejected, delta=f"{rejected} отклонено")

            # Фильтры
            st.subheader("🔍 Фильтр откликов")
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                status_filter = st.selectbox("Фильтр по статусу",
                                             ["Все", "pending", "accepted", "rejected"])
            with col_filter2:
                search_application = st.text_input("Поиск по студенту/вакансии")

            # Применение фильтров
            filtered_apps = applications.copy()
            if status_filter != "Все":
                filtered_apps = filtered_apps[filtered_apps['status'] == status_filter]
            if search_application:
                filtered_apps = filtered_apps[filtered_apps.apply(
                    lambda row: search_application.lower() in str(row['full_name']).lower() or
                                search_application.lower() in str(row['position']).lower(), axis=1)]

            # Отображение откликов
            for _, app in filtered_apps.iterrows():
                with st.container():
                    status_class = f"status-{app['status']}"
                    status_text = {
                        'pending': '⏳ Ожидает',
                        'accepted': '✅ Принято',
                        'rejected': '❌ Отклонено'
                    }.get(app['status'], app['status'])

                    st.markdown(f"""
                    <div class="content-card">
                        <div style="display: flex; justify-content: space-between; align-items: start;">
                            <div>
                                <h4 style="margin: 0; color: var(--neon-purple);">{app['position']}</h4>
                                <p style="margin: 5px 0; color: var(--text-dim);">{app['company_name']}</p>
                                <p style="margin: 0;"><strong>Студент:</strong> {app['full_name']}</p>
                                <p style="margin: 5px 0;"><strong>Дата отклика:</strong> {app['application_date'][:10]}</p>
                            </div>
                            <span class="status-badge {status_class}">{status_text}</span>
                        </div>
                        {f'<p style="margin-top: 10px;"><strong>Сопроводительное письмо:</strong><br>{app["cover_letter"][:200]}...</p>' if app['cover_letter'] else ''}
                    </div>
                    """, unsafe_allow_html=True)

                    # Кнопки управления статусом
                    col_status1, col_status2, col_status3, _ = st.columns([1, 1, 1, 3])
                    with col_status1:
                        if app['status'] != 'accepted':
                            if st.button("✅ Принять", key=f"accept_{app['id']}"):
                                st.session_state.db_manager.update_application_status(app['id'], 'accepted')
                                st.success("Статус изменен на 'Принято'")
                                st.rerun()
                    with col_status2:
                        if app['status'] != 'rejected':
                            if st.button("❌ Отклонить", key=f"reject_{app['id']}"):
                                st.session_state.db_manager.update_application_status(app['id'], 'rejected')
                                st.success("Статус изменен на 'Отклонено'")
                                st.rerun()
                    with col_status3:
                        if st.button("📋 Подробнее", key=f"details_{app['id']}"):
                            with st.expander("Детали отклика", expanded=True):
                                if app['cover_letter']:
                                    st.markdown(f"**Сопроводительное письмо:**\n{app['cover_letter']}")
                                st.markdown(f"**Дата отправки:** {app['application_date']}")
                    st.markdown("---")
        else:
            st.info("📭 Пока нет откликов на вакансии")
    except Exception as e:
        st.error(f"Ошибка при загрузке откликов: {e}")

    if st.button("🏠 В главное меню", use_container_width=True, type="secondary"):
        st.session_state.page = 'dashboard'
        st.rerun()


# ========== ОСНОВНЫЕ СТРАНИЦЫ ==========
def dashboard_page():
    """Главная панель управления"""
    create_header()

    try:
        stats = st.session_state.db_manager.get_statistics()

        # Основные метрики
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            metric_card("Всего студентов", stats['total_students'], "👨‍🎓")
        with col2:
            metric_card("Активных", stats['active_students'], "🔍")
        with col3:
            metric_card("Вакансий", stats['active_vacancies'], "💼")
        with col4:
            metric_card("Откликов", stats['total_applications'], "📨")
        with col5:
            metric_card("Трудоустроено", stats['employed_students'], "📊")
        with col6:
            metric_card("Уведомления", stats['unread_notifications'], "🔔")

        # Быстрые действия
        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("🚀 Быстрые действия")

        col_actions1, col_actions2, col_actions3, col_actions4, col_actions5 = st.columns(5)

        with col_actions1:
            if st.button("👨‍🎓 Подать заявку", use_container_width=True):
                st.session_state.page = 'student_form'
                st.rerun()

        with col_actions2:
            if st.button("💼 Вакансии", use_container_width=True):
                st.session_state.page = 'vacancies'
                st.rerun()

        with col_actions3:
            if st.button("📨 Отклики", use_container_width=True):
                st.session_state.page = 'applications'
                st.rerun()

        with col_actions4:
            if st.button("📊 Трудоустройство", use_container_width=True):
                st.session_state.page = 'employment_reports'
                st.rerun()

        with col_actions5:
            if st.button("🔔 Уведомления", use_container_width=True):
                st.session_state.page = 'notifications'
                st.rerun()

        # Статистика
        st.markdown("<br>", unsafe_allow_html=True)
        col_stats1, col_stats2 = st.columns(2)

        with col_stats1:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.subheader("🎯 Активность студентов")
            students_df = st.session_state.db_manager.get_all_students()
            if not students_df.empty:
                # Динамика регистрации студентов по месяцам
                try:
                    students_df['registration_date'] = pd.to_datetime(students_df['registration_date'])
                    monthly_registrations = students_df.set_index('registration_date').resample('M').size()

                    if len(monthly_registrations) > 0:
                        chart_data = pd.DataFrame({
                            'Месяц': monthly_registrations.index.strftime('%b %Y'),
                            'Регистрации': monthly_registrations.values
                        })

                        st.line_chart(chart_data.set_index('Месяц'))
                except:
                    pass

                # Дополнительная статистика
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    recent_count = len(
                        students_df[students_df['registration_date'] >= pd.Timestamp.now() - pd.DateOffset(months=1)])
                    st.metric("Новых в этом месяце", recent_count)
                with col_stat2:
                    avg_gpa = students_df['gpa'].mean() if 'gpa' in students_df.columns else 0
                    st.metric("Средний GPA", f"{avg_gpa:.2f}")
            else:
                st.info("Нет данных о студентах")
            st.markdown('</div>', unsafe_allow_html=True)

        with col_stats2:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.subheader("🚀 Статусы откликов")
            try:
                applications = st.session_state.db_manager.get_applications()
                if not applications.empty:
                    status_counts = applications['status'].value_counts()

                    fig = go.Figure(data=[go.Pie(
                        labels=['Ожидают', 'Приняты', 'Отклонены'],
                        values=[status_counts.get('pending', 0),
                                status_counts.get('accepted', 0),
                                status_counts.get('rejected', 0)],
                        hole=.3,
                        marker_colors=['#FFAA00', '#00FF88', '#FF3860']
                    )])

                    fig.update_layout(
                        showlegend=True,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color='white',
                        margin=dict(t=20, b=20, l=20, r=20)
                    )

                    st.plotly_chart(fig, use_container_width=True)

                    col_stat1, col_stat2, col_stat3 = st.columns(3)
                    with col_stat1:
                        st.metric("Ожидают", status_counts.get('pending', 0))
                    with col_stat2:
                        st.metric("Приняты", status_counts.get('accepted', 0))
                    with col_stat3:
                        st.metric("Отклонены", status_counts.get('rejected', 0))
                else:
                    st.info("Пока нет откликов")
            except Exception as e:
                st.info("Нет данных об откликах")
            st.markdown('</div>', unsafe_allow_html=True)

        # Последние активности - ИСПРАВЛЕННАЯ ВЕРСИЯ
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        st.subheader("🔄 Последние активности")

        col_activity1, col_activity2 = st.columns(2)

        with col_activity1:
            st.markdown("**🎓 Новые студенты**")
            try:
                if not students_df.empty:
                    recent_students = students_df.head(3)
                    for _, student in recent_students.iterrows():
                        st.markdown(f"""
                        <div style="background: rgba(157, 78, 221, 0.1); padding: 12px; border-radius: 10px; margin-bottom: 10px;">
                            <div style="display: flex; align-items: center; gap: 12px;">
                                <div style="font-size: 1.8rem; color: var(--neon-purple);">👨‍🎓</div>
                                <div>
                                    <div style="font-weight: 600; color: var(--neon-purple);">{student['full_name']}</div>
                                    <div style="font-size: 0.9rem; color: var(--text-dim); margin-top: 4px;">
                                        {student['specialization']} • Курс {student['course']}
                                    </div>
                                </div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("Нет данных о студентах")
            except Exception as e:
                st.info("Ошибка загрузки студентов")

        with col_activity2:
            st.markdown("**💼 Активные вакансии**")
            try:
                vacancies_df = st.session_state.db_manager.get_all_vacancies()
                if not vacancies_df.empty:
                    for idx, vacancy in vacancies_df.head(3).iterrows():
                        try:
                            # Безопасное вычисление дней
                            if pd.notna(vacancy['application_deadline']):
                                deadline_date = pd.to_datetime(vacancy['application_deadline'])
                                days_left = (deadline_date - pd.Timestamp.now()).days
                                days_left = max(0, days_left)
                                days_text = f"• {days_left} дней"
                                days_color = "#FF3860" if days_left < 7 else "#FFAA00" if days_left < 30 else "#00FF88"
                            else:
                                days_text = ""
                                days_color = "var(--text-dim)"

                            position = str(vacancy['position'])[:25] + (
                                "..." if len(str(vacancy['position'])) > 25 else "")
                            company = str(vacancy['company_name'])[:20] + (
                                "..." if len(str(vacancy['company_name'])) > 20 else "")

                            st.markdown(f"""
                            <div style="background: rgba(0, 229, 255, 0.1); padding: 12px; border-radius: 10px; margin-bottom: 10px;">
                                <div style="display: flex; align-items: center; gap: 12px;">
                                    <div style="font-size: 1.8rem; color: var(--neon-blue);">💼</div>
                                    <div>
                                        <div style="font-weight: 600; color: var(--neon-blue);">{position}</div>
                                        <div style="font-size: 0.9rem; color: var(--text-dim); margin-top: 4px;">
                                            {company} <span style="color: {days_color};">{days_text}</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                        except:
                            # Простая версия без дней
                            st.markdown(f"""
                            <div style="background: rgba(0, 229, 255, 0.1); padding: 12px; border-radius: 10px; margin-bottom: 10px;">
                                <div style="display: flex; align-items: center; gap: 12px;">
                                    <div style="font-size: 1.8rem; color: var(--neon-blue);">💼</div>
                                    <div>
                                        <div style="font-weight: 600; color: var(--neon-blue);">{vacancy['position'][:25]}</div>
                                        <div style="font-size: 0.9rem; color: var(--text-dim); margin-top: 4px;">
                                            {vacancy['company_name'][:20]}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.info("Нет активных вакансий")
            except Exception as e:
                st.info("Ошибка загрузки вакансий")

        st.markdown('</div>', unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {str(e)}")

    # Кнопка возврата в меню (если нужно)
    if st.session_state.page != 'dashboard':
        if st.button("🏠 В главное меню", use_container_width=True, type="secondary"):
            st.session_state.page = 'dashboard'
            st.rerun()


def student_management_page():
    """Управление студентами"""
    st.header("👨‍🎓 Управление студентами")

    # Поиск и фильтры
    with st.container():
        st.markdown('<div class="content-card">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            search_query = st.text_input("🔍 Поиск по имени", placeholder="Введите ФИО...")
        with col2:
            course_filter = st.selectbox("Фильтр по курсу", ["Все"] + COURSE_OPTIONS)
        with col3:
            spec_filter = st.selectbox("Фильтр по специальности", ["Все"] + SPECIALIZATION_OPTIONS)
        st.markdown('</div>', unsafe_allow_html=True)

    try:
        # Получение данных
        students_df = st.session_state.db_manager.get_all_students()

        # Применение фильтров
        if not students_df.empty:
            if search_query:
                students_df = students_df[students_df['full_name'].str.contains(search_query, case=False, na=False)]
            if course_filter != "Все":
                students_df = students_df[students_df['course'] == course_filter]
            if spec_filter != "Все":
                students_df = students_df[students_df['specialization'] == spec_filter]

        # Таблица студентов
        if not students_df.empty:
            display_cols = ['id', 'full_name', 'course', 'specialization', 'programming_languages', 'is_active']
            st.dataframe(
                students_df[display_cols].rename(columns={
                    'id': 'ID',
                    'full_name': 'ФИО',
                    'course': 'Курс',
                    'specialization': 'Специальность',
                    'programming_languages': 'Навыки',
                    'is_active': 'Активен'
                }),
                use_container_width=True,
                hide_index=True
            )

            # Детальный просмотр
            st.subheader("🔍 Детальный просмотр")
            selected_id = st.selectbox(
                "Выберите студента для просмотра",
                options=students_df['id'].tolist(),
                format_func=lambda x: f"ID {x}: {students_df[students_df['id'] == x]['full_name'].iloc[0]}"
            )

            if selected_id:
                student = st.session_state.db_manager.get_student_by_id(selected_id)
                if student is not None:
                    with st.expander(f"📋 Профиль студента {student['full_name']}", expanded=True):
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**🎓 ФИО:** {student['full_name']}")
                            st.markdown(f"**📚 Курс:** {student['course']}")
                            st.markdown(f"**🎯 Специальность:** {student['specialization']}")
                            st.markdown(f"**🏫 Университет:** {student['university']}")
                            st.markdown(f"**📅 Год выпуска:** {student['graduation_year']}")
                        with col2:
                            st.markdown(f"**📧 Email:** {student['email']}")
                            st.markdown(f"**📱 Телефон:** {student['contact_number']}")
                            st.markdown(f"**📊 GPA:** {student['gpa']}")
                            st.markdown(f"**🔧 Навыки:** {student['programming_languages']}")
                            st.markdown(
                                f"**🔍 Статус:** {'Активен в поиске ✅' if student['is_active'] else 'Не активен ❌'}")

                        st.markdown("**💼 Опыт работы:**")
                        st.info(
                            student['work_experience'] if pd.notna(student['work_experience']) else "Опыт не указан")

                        if student['portfolio_link'] and pd.notna(student['portfolio_link']):
                            st.markdown(f"**📂 Портфолио:** [{student['portfolio_link']}]({student['portfolio_link']})")

                        # Кнопки действий
                        col_edit, col_delete, col_report = st.columns([1, 1, 2])
                        if col_edit.button("✏️ Редактировать", key=f"edit_{selected_id}"):
                            st.session_state.edit_mode = True
                            st.session_state.current_student_id = selected_id
                            st.session_state.page = 'student_form'
                            st.rerun()

                        if col_delete.button("🗑️ Удалить", key=f"delete_{selected_id}", type="secondary"):
                            if st.checkbox("Подтвердите удаление"):
                                st.session_state.db_manager.delete_student(selected_id)
                                st.success("Студент удален!")
                                st.rerun()

                        if col_report.button("📝 Отчет о трудоустройстве", key=f"report_{selected_id}"):
                            st.session_state.page = 'employment_reports'
                            st.rerun()
        else:
            st.info("👤 Студенты не найдены")
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")

    if st.button("🏠 В главное меню", use_container_width=True, type="secondary"):
        st.session_state.page = 'dashboard'
        st.rerun()


def student_form_page():
    """Форма добавления/редактирования студента"""
    st.header("📝 Форма студента")

    is_edit = st.session_state.get('edit_mode', False)
    student_data = None

    if is_edit and st.session_state.current_student_id:
        try:
            # Получаем данные студента (это Pandas Series)
            student_data = st.session_state.db_manager.get_student_by_id(st.session_state.current_student_id)
        except Exception as e:
            st.error(f"Ошибка при загрузке данных студента: {e}")
            student_data = None

    with st.form(key="student_form"):
        col1, col2 = st.columns(2)

        # ВЕЗДЕ НИЖЕ ВМЕСТО "if student_data" ПИШЕМ "if student_data is not None"
        
        with col1:
            full_name = st.text_input("Полное ФИО *",
                                      value=student_data['full_name'] if student_data is not None else "",
                                      placeholder="Иванов Иван Иванович")
            email = st.text_input("Email *",
                                  value=student_data['email'] if student_data is not None else "",
                                  placeholder="example@email.com")
            contact_number = st.text_input("Контактный номер *",
                                           value=student_data['contact_number'] if student_data is not None else "",
                                           help="Формат: +7 XXX XXX XX XX",
                                           placeholder="+7 701 123 4567")
            document_id = st.text_input("ИИН *",
                                        value=student_data['document_id'] if student_data is not None else "",
                                        placeholder="12 цифр")

        with col2:
            # Для селектов (выпадающих списков) нужна аккуратная проверка
            default_course_idx = COURSE_OPTIONS.index(2) # по умолчанию 2 курс
            if student_data is not None and student_data['course'] in COURSE_OPTIONS:
                default_course_idx = COURSE_OPTIONS.index(student_data['course'])

            course = st.selectbox("Курс *", COURSE_OPTIONS, index=default_course_idx)

            default_spec_idx = 0
            if student_data is not None and student_data['specialization'] in SPECIALIZATION_OPTIONS:
                default_spec_idx = SPECIALIZATION_OPTIONS.index(student_data['specialization'])
            
            specialization = st.selectbox("Специальность *", SPECIALIZATION_OPTIONS, index=default_spec_idx)
            
            # Университет
            default_uni_idx = 0
            if student_data is not None and student_data['university'] in UNIVERSITY_OPTIONS:
                default_uni_idx = UNIVERSITY_OPTIONS.index(student_data['university'])
                
            university = st.selectbox("Университет", UNIVERSITY_OPTIONS, index=default_uni_idx)
            
            # GPA
            default_gpa = 3.0
            if student_data is not None and pd.notna(student_data['gpa']):
                default_gpa = float(student_data['gpa'])
                
            gpa = st.number_input("Средний балл (GPA)",
                                  min_value=0.0, max_value=4.0, step=0.1,
                                  value=default_gpa)

        # Мультиселект (языки)
        default_langs = []
        if student_data is not None and pd.notna(student_data['programming_languages']):
            # Разбиваем строку и чистим пробелы
            raw_langs = str(student_data['programming_languages']).split(',')
            # Фильтруем только те, что есть в списке опций
            default_langs = [l.strip() for l in raw_langs if l.strip() in LANGUAGE_OPTIONS]

        programming_languages = st.multiselect("Языки программирования и технологии",
                                               LANGUAGE_OPTIONS,
                                               default=default_langs)

        work_experience = st.text_area("Опыт работы",
                                       value=student_data['work_experience'] if student_data is not None else "",
                                       height=150,
                                       placeholder="Опишите ваш опыт работы, проекты, достижения...")

        portfolio_link = st.text_input("Ссылка на портфолио/GitHub",
                                       value=student_data['portfolio_link'] if student_data is not None else "",
                                       placeholder="https://github.com/username")

        col_year, col_active = st.columns(2)
        with col_year:
            default_year = 2024
            if student_data is not None and pd.notna(student_data['graduation_year']):
                default_year = int(student_data['graduation_year'])
                
            graduation_year = st.number_input("Год выпуска",
                                              min_value=2020, max_value=2030,
                                              value=default_year)
        with col_active:
            # Чекбокс
            is_active_val = True
            if student_data is not None:
                is_active_val = bool(student_data['is_active'])
            
            is_active = st.checkbox("Активно ищу работу/стажировку", value=is_active_val)

        submit_label = "💾 Сохранить изменения" if is_edit else "🚀 Отправить заявку"
        # Вот она - кнопка Submit. Она должна быть внутри with st.form!
        submitted = st.form_submit_button(submit_label, use_container_width=True)

        if submitted:
            if all([full_name, email, contact_number, document_id]):
                languages_str = ", ".join(programming_languages)
                student_data_tuple = (
                    full_name, course, specialization, languages_str,
                    work_experience, portfolio_link, contact_number,
                    document_id, email, gpa, graduation_year, int(is_active)
                )

                try:
                    if is_edit:
                        st.session_state.db_manager.update_student(st.session_state.current_student_id,
                                                                   student_data_tuple)
                        st.success("✅ Профиль успешно обновлен!")
                        # Добавляем уведомление
                        st.session_state.db_manager.add_notification(
                            st.session_state.current_student_id,
                            "Профиль обновлен",
                            f"Ваш профиль был обновлен. Дата: {datetime.now().strftime('%d.%m.%Y')}",
                            "success"
                        )
                    else:
                        st.session_state.db_manager.insert_student(student_data_tuple)
                        st.success("✅ Заявка успешно отправлена!")
                        # Добавляем уведомление админу
                        st.session_state.db_manager.add_notification(
                            1,  # Администратор
                            "Новая заявка студента",
                            f"Студент {full_name} подал заявку",
                            "info"
                        )
                        st.balloons()

                    # Сброс состояния после успеха
                    if is_edit:
                        st.session_state.edit_mode = False
                        st.session_state.current_student_id = None

                    st.session_state.page = 'students'
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Ошибка сохранения: {str(e)}")
            else:
                st.warning("⚠️ Пожалуйста, заполните все обязательные поля (отмечены *)")

    # Кнопки возврата (вне формы)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ К списку студентов", use_container_width=True, type="secondary"):
            st.session_state.page = 'students'
            st.session_state.edit_mode = False
            if 'current_student_id' in st.session_state:
                del st.session_state.current_student_id
            st.rerun()
    with col2:
        if st.button("🏠 В главное меню", use_container_width=True, type="secondary"):
            st.session_state.page = 'dashboard'
            st.session_state.edit_mode = False
            if 'current_student_id' in st.session_state:
                del st.session_state.current_student_id
            st.rerun()


def vacancies_page():
    """Страница вакансий"""
    st.header("💼 Вакансии для студентов")

    try:
        # Получение вакансий
        vacancies_df = st.session_state.db_manager.get_all_vacancies()

        if not vacancies_df.empty:
            # Поиск и фильтры
            with st.container():
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    search_vacancy = st.text_input("🔍 Поиск по вакансиям", placeholder="Название, компания...")
                with col2:
                    spec_filter = st.selectbox("Фильтр по специальности", ["Все"] + SPECIALIZATION_OPTIONS)
                st.markdown('</div>', unsafe_allow_html=True)

            # Применение фильтров
            if search_vacancy:
                vacancies_df = vacancies_df[vacancies_df.apply(
                    lambda row: search_vacancy.lower() in str(row['position']).lower() or
                                search_vacancy.lower() in str(row['company_name']).lower(), axis=1)]

            if spec_filter != "Все":
                vacancies_df = vacancies_df[vacancies_df['specialization'] == spec_filter]

            # Отображение вакансий в виде карточек
            for _, vacancy in vacancies_df.iterrows():
                with st.container():
                    deadline_date = pd.to_datetime(vacancy['application_deadline'])
                    days_left = (deadline_date - pd.Timestamp.now()).days
                    days_color = "var(--danger)" if days_left < 7 else "var(--warning)" if days_left < 30 else "var(--success)"

                    st.markdown(f"""
                    <div class="content-card">
                        <h3 style="margin: 0; color: var(--neon-purple);">{vacancy['position']}</h3>
                        <p style="margin: 0; font-weight: 500; color: var(--neon-blue);">{vacancy['company_name']}</p>
                        <div style="margin-top: 15px; display: flex; flex-wrap: wrap; gap: 10px;">
                            <span style="background: rgba(157, 78, 221, 0.2); color: var(--neon-purple); 
                                    padding: 6px 12px; border-radius: 20px; font-size: 0.9rem;">
                                🎯 {vacancy['specialization']}
                            </span>
                            <span style="background: rgba(0, 229, 255, 0.2); color: var(--neon-blue); 
                                    padding: 6px 12px; border-radius: 20px; font-size: 0.9rem;">
                                📚 Курс {vacancy['required_course']}+
                            </span>
                            <span style="background: rgba(255, 170, 0, 0.2); color: var(--warning); 
                                    padding: 6px 12px; border-radius: 20px; font-size: 0.9rem;">
                                💰 {vacancy['salary_range']}
                            </span>
                            <span style="background: rgba(255, 0, 255, 0.2); color: var(--neon-pink); 
                                    padding: 6px 12px; border-radius: 20px; font-size: 0.9rem;">
                                ⏰ Дней осталось: <span style="color: {days_color};">{days_left if days_left > 0 else 0}</span>
                            </span>
                        </div>
                        <p style="margin-top: 15px; color: var(--text-light); line-height: 1.6;">
                            {vacancy['description'][:200]}...
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Кнопки действий
                    col1, col2, col3 = st.columns([1, 1, 2])
                    with col1:
                        if st.button("📨 Откликнуться", key=f"apply_{vacancy['id']}"):
                            st.session_state.current_vacancy_id = vacancy['id']
                            st.session_state.page = 'apply_vacancy'
                            st.rerun()
                    with col2:
                        if st.button("📋 Подробнее", key=f"details_{vacancy['id']}"):
                            with st.expander("Подробная информация", expanded=True):
                                st.markdown(f"**📝 Описание:**\n{vacancy['description']}")
                                st.markdown(f"**🎯 Требования:**\n{vacancy['requirements']}")
                                st.markdown(f"**📧 Контакты:** {vacancy['contact_email']}")
                                st.markdown(f"**⏰ Дедлайн:** {vacancy['application_deadline']}")
                    st.markdown("---")
        else:
            st.info("💼 Активных вакансий пока нет")

    except Exception as e:
        st.error(f"Ошибка при загрузке вакансий: {e}")

    # Кнопка добавления вакансии
    if st.button("➕ Добавить вакансию", use_container_width=True):
        st.session_state.page = 'vacancy_form'
        st.rerun()

    if st.button("🏠 В главное меню", use_container_width=True, type="secondary"):
        st.session_state.page = 'dashboard'
        st.rerun()


def vacancy_form_page():
    """Форма добавления вакансии"""
    st.header("📋 Форма вакансии")

    with st.form(key="vacancy_form"):
        col1, col2 = st.columns(2)

        with col1:
            company_name = st.text_input("Название компании *", placeholder="Например: Kaspi Bank")
            position = st.text_input("Должность *", placeholder="Например: Junior Python Developer")
            specialization = st.selectbox("Специальность", SPECIALIZATION_OPTIONS)
            required_course = st.selectbox("Требуемый курс", COURSE_OPTIONS)

        with col2:
            salary_range = st.text_input("Зарплатная вилка", placeholder="Например: 300 000 - 500 000 KZT")
            contact_email = st.text_input("Email для откликов *", placeholder="hr@company.kz")
            application_deadline = st.date_input("Дедлайн подачи")

        description = st.text_area("Описание вакансии *", height=150,
                                   placeholder="Опишите обязанности, условия работы, преимущества...")
        requirements = st.text_area("Требования *", height=150,
                                    placeholder="Укажите необходимые навыки, опыт, образование...")

        submitted = st.form_submit_button("📤 Опубликовать вакансию", use_container_width=True)

        if submitted:
            if all([company_name, position, description, requirements, contact_email]):
                vacancy_data = (
                    company_name, position, specialization, required_course,
                    salary_range, description, requirements, contact_email,
                    application_deadline.strftime('%Y-%m-%d')
                )
                try:
                    st.session_state.db_manager.insert_vacancy(vacancy_data)
                    st.success("✅ Вакансия успешно опубликована!")
                    # Добавляем уведомление
                    st.session_state.db_manager.add_notification(
                        1,  # Администратор
                        "Новая вакансия",
                        f"Опубликована новая вакансия: {position} в компании {company_name}",
                        "info"
                    )
                    st.session_state.page = 'vacancies'
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Ошибка: {str(e)}")
            else:
                st.warning("⚠️ Пожалуйста, заполните все обязательные поля")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ К вакансиям", use_container_width=True, type="secondary"):
            st.session_state.page = 'vacancies'
            st.rerun()
    with col2:
        if st.button("🏠 В главное меню", use_container_width=True, type="secondary"):
            st.session_state.page = 'dashboard'
            st.rerun()


def analytics_page():
    """Аналитика и отчеты"""
    st.header("📊 Аналитика и отчеты")

    try:
        students_df = st.session_state.db_manager.get_all_students()
        vacancies_df = st.session_state.db_manager.get_all_vacancies()
        reports_df = st.session_state.db_manager.get_employment_reports()
        applications_df = st.session_state.db_manager.get_applications()

        if not students_df.empty:
            # Вкладки с разной аналитикой
            tab1, tab2, tab3, tab4 = st.tabs(["📈 Общая статистика", "🎯 Распределение", "📊 Успеваемость", "📋 Отчеты"])

            with tab1:
                col1, col2 = st.columns(2)

                with col1:
                    # Круговая диаграмма по специальностям
                    st.subheader("Распределение студентов по специальностям")
                    spec_dist = students_df['specialization'].value_counts()
                    for spec, count in spec_dist.items():
                        percentage = (count / spec_dist.sum()) * 100
                        st.progress(percentage / 100, text=f"{spec}: {count} студентов ({percentage:.1f}%)")

                with col2:
                    # Статистика по статусам откликов
                    st.subheader("Статусы откликов")
                    if not applications_df.empty:
                        status_dist = applications_df['status'].value_counts()
                        for status, count in status_dist.items():
                            status_ru = {'pending': '⏳ Ожидают', 'accepted': '✅ Приняты',
                                         'rejected': '❌ Отклонены'}.get(status, status)
                            st.metric(status_ru, count)
                    else:
                        st.info("Нет данных об откликах")

            with tab2:
                # Таблица распределения по курсам и специальностям
                st.subheader("Распределение студентов")
                if not students_df.empty:
                    pivot_table = pd.crosstab(students_df['course'], students_df['specialization'], margins=True)
                    st.dataframe(pivot_table, use_container_width=True)

                # Распределение зарплат
                st.subheader("Распределение зарплат")
                if not reports_df.empty and 'salary' in reports_df.columns:
                    salaries = reports_df['salary'].apply(
                        lambda x: float(str(x).split()[0].replace('KZT', '').replace(',', '').strip())
                        if 'KZT' in str(x) else 0
                    )
                    if salaries.sum() > 0:
                        col_s1, col_s2, col_s3 = st.columns(3)
                        with col_s1:
                            st.metric("Мин. зарплата", f"{salaries.min():,.0f} KZT")
                        with col_s2:
                            st.metric("Средняя зарплата", f"{salaries.mean():,.0f} KZT")
                        with col_s3:
                            st.metric("Макс. зарплата", f"{salaries.max():,.0f} KZT")

            with tab3:
                # Статистика успеваемости
                st.subheader("Статистика успеваемости студентов")
                if 'gpa' in students_df.columns:
                    gpa_stats = students_df['gpa'].describe()

                    col_g1, col_g2, col_g3, col_g4 = st.columns(4)
                    with col_g1:
                        st.metric("Средний GPA", f"{gpa_stats['mean']:.2f}")
                    with col_g2:
                        st.metric("Медиана GPA", f"{gpa_stats['50%']:.2f}")
                    with col_g3:
                        st.metric("Мин. GPA", f"{gpa_stats['min']:.2f}")
                    with col_g4:
                        st.metric("Макс. GPA", f"{gpa_stats['max']:.2f}")

                    # Распределение GPA
                    st.subheader("Распределение GPA")
                    gpa_bins = pd.cut(students_df['gpa'], bins=[0, 2.0, 3.0, 3.5, 4.0],
                                      labels=['<2.0', '2.0-3.0', '3.0-3.5', '3.5-4.0'])
                    gpa_dist = gpa_bins.value_counts().sort_index()
                    for gpa_range, count in gpa_dist.items():
                        percentage = (count / len(students_df)) * 100
                        st.progress(percentage / 100, text=f"{gpa_range}: {count} студентов ({percentage:.1f}%)")

            with tab4:
                # Генерация отчета
                st.subheader("📋 Генерация отчета")

                report_type = st.selectbox("Выберите тип отчета",
                                           ["Общий отчет", "Отчет по трудоустройству", "Отчет по успеваемости",
                                            "Отчет по вакансиям"])

                if st.button("📥 Сгенерировать отчет", use_container_width=True):
                    with st.spinner("Генерация отчета..."):
                        # Создаем простой текстовый отчет
                        report = f"""
                        ОТЧЕТ СИСТЕМЫ GRADUATE RECRUITMENT
                        =========================================
                        Дата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M')}
                        Тип отчета: {report_type}

                        """

                        if report_type == "Общий отчет":
                            report += f"""
                            ОБЩАЯ СТАТИСТИКА:
                            - Всего студентов: {len(students_df)}
                            - Активных студентов: {len(students_df[students_df['is_active'] == 1])}
                            - Всего ваканций: {len(vacancies_df)}
                            - Всего откликов: {len(applications_df) if not applications_df.empty else 0}
                            - Трудоустроено студентов: {len(reports_df)}

                            РАСПРЕДЕЛЕНИЕ ПО СПЕЦИАЛЬНОСТЯМ:
                            """
                            for spec, count in students_df['specialization'].value_counts().items():
                                report += f"- {spec}: {count} студентов\n"

                            report += f"\nСредний GPA: {students_df['gpa'].mean():.2f}"

                        elif report_type == "Отчет по трудоустройству":
                            if not reports_df.empty:
                                report += f"""
                                ОТЧЕТ ПО ТРУДОУСТРОЙСТВУ:
                                - Всего трудоустроено: {len(reports_df)}
                                - По компаниям:
                                """
                                company_counts = reports_df['company_name'].value_counts()
                                for company, count in company_counts.items():
                                    report += f"  - {company}: {count} студентов\n"

                                if 'salary' in reports_df.columns:
                                    salaries = reports_df['salary'].apply(
                                        lambda x: float(str(x).split()[0].replace('KZT', '').replace(',', '').strip())
                                        if 'KZT' in str(x) else 0
                                    )
                                    report += f"\nСредняя зарплата: {salaries.mean():,.0f} KZT"
                            else:
                                report += "Нет данных о трудоустройстве"

                        elif report_type == "Отчет по успеваемости":
                            report += f"""
                            ОТЧЕТ ПО УСПЕВАЕМОСТИ:
                            - Средний GPA: {students_df['gpa'].mean():.2f}
                            - Медиана GPA: {students_df['gpa'].median():.2f}
                            - Максимальный GPA: {students_df['gpa'].max():.2f}
                            - Минимальный GPA: {students_df['gpa'].min():.2f}

                            РАСПРЕДЕЛЕНИЕ ПО БАЛЛАМ:
                            """
                            gpa_bins = pd.cut(students_df['gpa'], bins=[0, 2.0, 3.0, 3.5, 4.0])
                            for interval, count in gpa_bins.value_counts().sort_index().items():
                                report += f"- {interval}: {count} студентов\n"

                        elif report_type == "Отчет по вакансиям":
                            report += f"""
                            ОТЧЕТ ПО ВАКАНСИЯМ:
                            - Всего активных вакансий: {len(vacancies_df)}

                            ПО КОМПАНИЯМ:
                            """
                            company_counts = vacancies_df['company_name'].value_counts()
                            for company, count in company_counts.items():
                                report += f"- {company}: {count} вакансий\n"

                            report += f"\nПО СПЕЦИАЛЬНОСТЯМ:"
                            spec_counts = vacancies_df['specialization'].value_counts()
                            for spec, count in spec_counts.items():
                                report += f"- {spec}: {count} вакансий\n"

                        st.success("✅ Отчет сгенерирован!")
                        st.text_area("Содержимое отчета", report, height=300)

                        # Кнопка скачивания
                        st.download_button(
                            label="📥 Скачать отчет",
                            data=report,
                            file_name=f"report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                            mime="text/plain"
                        )

                # Показать сырые данные
                with st.expander("📁 Просмотр всех данных"):
                    data_type = st.selectbox("Выберите данные",
                                             ["Студенты", "Вакансии", "Отклики", "Трудоустройство"])

                    if data_type == "Студенты":
                        st.dataframe(students_df, use_container_width=True)
                    elif data_type == "Вакансии":
                        st.dataframe(vacancies_df, use_container_width=True)
                    elif data_type == "Отклики" and not applications_df.empty:
                        st.dataframe(applications_df, use_container_width=True)
                    elif data_type == "Трудоустройство" and not reports_df.empty:
                        st.dataframe(reports_df, use_container_width=True)
        else:
            st.info("📊 Нет данных для анализа")

    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")

    if st.button("🏠 В главное меню", use_container_width=True, type="secondary"):
        st.session_state.page = 'dashboard'
        st.rerun()


def apply_vacancy_page():
    """Форма отклика на вакансию"""
    st.header("📨 Отклик на вакансию")

    if 'current_vacancy_id' in st.session_state:
        try:
            vacancies_df = st.session_state.db_manager.get_all_vacancies()
            vacancy = vacancies_df[vacancies_df['id'] == st.session_state.current_vacancy_id].iloc[0]

            st.markdown(f"""
            <div class="content-card">
                <h3 style="color: var(--neon-purple);">{vacancy['position']}</h3>
                <p style="color: var(--neon-blue); font-size: 1.1rem;">Компания: {vacancy['company_name']}</p>
            </div>
            """, unsafe_allow_html=True)

            # Получение списка студентов для отклика
            students_df = st.session_state.db_manager.get_all_students()

            if not students_df.empty:
                student_options = {row['id']: row['full_name'] for _, row in students_df.iterrows()}
                selected_student = st.selectbox("Выберите студента",
                                                options=list(student_options.keys()),
                                                format_func=lambda x: student_options[x])

                cover_letter = st.text_area("Сопроводительное письмо",
                                            height=150,
                                            placeholder="Расскажите, почему вы подходите для этой вакансии...",
                                            help="Опишите ваш опыт, навыки и почему вы хотите работать в этой компании")

                if st.button("📤 Отправить отклик", use_container_width=True):
                    try:
                        st.session_state.db_manager.apply_for_vacancy(selected_student,
                                                                      st.session_state.current_vacancy_id,
                                                                      cover_letter)

                        # Добавляем уведомление
                        st.session_state.db_manager.add_notification(
                            selected_student,
                            "Отклик отправлен",
                            f"Ваш отклик на вакансию '{vacancy['position']}' в компании {vacancy['company_name']} успешно отправлен!",
                            "info"
                        )

                        st.success("✅ Отклик успешно отправлен!")
                        st.balloons()

                        # Очищаем состояние
                        del st.session_state.current_vacancy_id
                        st.session_state.page = 'vacancies'
                        st.rerun()

                    except Exception as e:
                        st.error(f"❌ Ошибка при отправке отклика: {str(e)}")
            else:
                st.info("👤 Сначала добавьте студентов в систему")
        except Exception as e:
            st.error(f"Ошибка при загрузке данных: {str(e)}")
    else:
        st.warning("⚠️ Сначала выберите вакансию для отклика")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ К вакансиям", use_container_width=True, type="secondary"):
                if 'current_vacancy_id' in st.session_state:
                    del st.session_state.current_vacancy_id
                st.session_state.page = 'vacancies'
                st.rerun()
        with col2:
            if st.button("🏠 В главное меню", use_container_width=True, type="secondary"):
                if 'current_vacancy_id' in st.session_state:
                    del st.session_state.current_vacancy_id
                st.session_state.page = 'dashboard'
                st.rerun()
        if st.button("🔍 Перейти к вакансиям", use_container_width=True):
            st.session_state.page = 'vacancies'
            st.rerun()


# ========== САЙДБАР НАВИГАЦИИ ==========
def create_sidebar():
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid rgba(157, 78, 221, 0.5); margin-bottom: 25px;">
            <div style="font-size: 3rem; color: var(--neon-purple); text-shadow: 0 0 20px rgba(157, 78, 221, 0.7); margin-bottom: 10px;">
                ⚡
            </div>
            <h1 style="color: var(--neon-purple); margin: 0; font-size: 2rem; font-family: 'Orbitron', sans-serif;">
                GRS
            </h1>
            <p style="color: var(--text-dim); margin: 5px 0 0 0; font-size: 0.9rem; opacity: 0.8;">
                Graduate Recruitment System
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Основная навигация
        pages = {
            "🏠 Панель управления": "dashboard",
            "👨‍🎓 Студенты": "students",
            "💼 Вакансии": "vacancies",
            "📨 Отклики": "applications",
            "📊 Трудоустройство": "employment_reports",
            "🔔 Уведомления": "notifications",
            "📈 Аналитика": "analytics",
        }

        for page_name, page_key in pages.items():
            if st.button(page_name, use_container_width=True,
                         type="primary" if st.session_state.page == page_key else "secondary"):
                st.session_state.page = page_key
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Быстрые действия
        st.markdown("""
        <div style="padding: 15px; background: rgba(157, 78, 221, 0.1); border-radius: 12px; margin: 20px 0; border: 1px solid rgba(157, 78, 221, 0.3);">
            <h4 style="color: var(--neon-purple); margin: 0 0 15px 0; font-size: 1rem; text-align: center;">
                ⚡ Быстрые действия
            </h4>
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("➕ Студент", use_container_width=True, type="secondary"):
                st.session_state.page = 'student_form'
                st.session_state.edit_mode = False
                st.rerun()
        with col2:
            if st.button("➕ Вакансия", use_container_width=True, type="secondary"):
                st.session_state.page = 'vacancy_form'
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)

        # Статистика в сайдбаре
        try:
            stats = st.session_state.db_manager.get_statistics()
            st.markdown(f"""
            <div style="background: rgba(20, 20, 43, 0.8); border: 1px solid rgba(157, 78, 221, 0.3); 
                    border-radius: 15px; padding: 20px; margin-top: 10px; backdrop-filter: blur(10px);">
                <h4 style="color: var(--neon-purple); margin: 0 0 15px 0; text-align: center; font-size: 1.1rem;">
                    📊 Статистика
                </h4>
                <div style="display: grid; grid-template-columns: 1fr; gap: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 5px 0;">
                        <span style="color: var(--text-dim); font-size: 0.9rem;">👨‍🎓 Студентов:</span>
                        <span style="color: var(--neon-purple); font-weight: 700; font-size: 1.1rem;">{stats['total_students']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 5px 0;">
                        <span style="color: var(--text-dim); font-size: 0.9rem;">💼 Вакансий:</span>
                        <span style="color: var(--neon-blue); font-weight: 700; font-size: 1.1rem;">{stats['active_vacancies']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 5px 0;">
                        <span style="color: var(--text-dim); font-size: 0.9rem;">📨 Откликов:</span>
                        <span style="color: var(--neon-pink); font-weight: 700; font-size: 1.1rem;">{stats['total_applications']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; padding: 5px 0;">
                        <span style="color: var(--text-dim); font-size: 0.9rem;">🔔 Уведомления:</span>
                        <span style="color: var(--danger); font-weight: 700; font-size: 1.1rem;">{stats['unread_notifications']}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.markdown(f"""
            <div style="background: rgba(20, 20, 43, 0.8); border: 1px solid rgba(157, 78, 221, 0.3); 
                    border-radius: 15px; padding: 20px; margin-top: 10px; backdrop-filter: blur(10px);">
                <h4 style="color: var(--neon-purple); margin: 0 0 15px 0; text-align: center; font-size: 1.1rem;">
                    📊 Статистика
                </h4>
                <p style="color: var(--text-dim); text-align: center; font-size: 0.9rem;">
                    Загрузка статистики...
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Информация о системе
        st.markdown("""
        <div style="text-align: center; color: var(--text-dim); font-size: 0.75rem; padding: 15px 0; 
                margin-top: 20px; border-top: 1px solid rgba(157, 78, 221, 0.3); opacity: 0.7;">
            <div style="margin-bottom: 5px;">v3.0 | CyberPunk Edition</div>
            <div>© 2025 Graduate Recruitment System</div>
            <div style="margin-top: 8px; color: var(--neon-purple); font-weight: 500; font-size: 0.8rem;">
                Разработчик: Айкобенов Диас
            </div>
        </div>
        """, unsafe_allow_html=True)


def main():
    init_session_state()
    apply_custom_styles()

    # Проверка входа
    if 'user' not in st.session_state:
        login_page()
    else:
        # ВАЖНО: Вызываем функцию из файла sidebar_auth.py
        create_auth_sidebar()

        # Маршрутизация (ваш старый код)
        page_handlers = {
            'dashboard': dashboard_page,
            'students': student_management_page,
            'student_form': student_form_page,
            'vacancies': vacancies_page,
            'vacancy_form': vacancy_form_page,
            'apply_vacancy': apply_vacancy_page,
            'applications': applications_page,
            'employment_reports': employment_reports_page,
            'notifications': notifications_page,
            'analytics': analytics_page,
        }

        # Защита от прямого перехода по URL
        user_role = st.session_state.user['role']
        current_page = st.session_state.page

        # Если СТУДЕНТ пытается зайти куда не надо (тут всё верно)
        if user_role == 'student' and current_page in ['students', 'applications', 'employment_reports', 'analytics',
                                                       'vacancy_form']:
            st.warning("⛔ Нет доступа")
            st.session_state.page = 'dashboard'
            st.rerun()

        

        handler = page_handlers.get(st.session_state.page, dashboard_page)
        handler()


if __name__ == "__main__":
    main()







