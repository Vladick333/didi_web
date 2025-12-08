import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import hashlib
import plotly.express as px
import plotly.graph_objects as go

@st.cache_resource(ttl=3600)  # Кэш на 1 час
def get_cached_db_connection():
    return sqlite3.connect('keu_career.db', check_same_thread=False)

def get_db_connection():
    return get_cached_db_connection()

# ========== КОНФИГУРАЦИЯ ==========
st.set_page_config(
    page_title="КЭУ Карьерный Центр",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ========== УЛУЧШЕННАЯ ПЕРСИКОВАЯ ТЕМА ==========
def apply_peach_theme():
    st.markdown("""
    <style>
    /* УЛУЧШЕННАЯ ПЕРСИКОВО-БЕЖЕВАЯ ТЕМА */
    :root {
        --peach-primary: #FFA07A;
        --peach-light: #FFE4B5;
        --peach-dark: #D2691E;
        --peach-gradient: linear-gradient(135deg, #FFA07A 0%, #FF8C69 50%, #FF7F50 100%);
        --beige-light: #F5F5DC;
        --beige-medium: #E6D5B8;
        --beige-dark: #D2B48C;
        --text-dark: #5D4037;
        --text-light: #8D6E63;
        --success: #4CAF50;
        --warning: #FF9800;
        --danger: #F44336;
        --card-bg: rgba(255, 255, 255, 0.95);
        --shadow-glow: 0 0 15px rgba(255, 160, 122, 0.3);
    }

    * {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* Главный контейнер */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, var(--beige-light) 0%, var(--peach-light) 100%) !important;
        color: var(--text-dark) !important;
        animation: backgroundShift 20s ease infinite alternate;
        background-size: 200% 200%;
    }

    @keyframes backgroundShift {
        0% { background-position: 0% 50%; }
        100% { background-position: 100% 50%; }
    }

    /* Заголовки */
    h1, h2, h3, h4, h5, h6 {
        color: var(--peach-dark) !important;
        font-weight: 600 !important;
        position: relative;
    }

    h1::after, h2::after {
        content: '';
        position: absolute;
        bottom: -5px;
        left: 0;
        width: 60px;
        height: 3px;
        background: var(--peach-gradient);
        border-radius: 2px;
    }

    /* Заголовок главный */
    .main-header {
        background: linear-gradient(135deg, var(--peach-primary) 0%, var(--peach-dark) 100%);
        color: white !important;
        padding: 2rem;
        margin-bottom: 2rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(210, 105, 30, 0.3);
        animation: pulse 3s infinite alternate;
        border: 2px solid rgba(255, 255, 255, 0.1);
    }

    @keyframes pulse {
        0% { box-shadow: 0 4px 20px rgba(210, 105, 30, 0.3); }
        100% { box-shadow: 0 4px 30px rgba(210, 105, 30, 0.5); }
    }

    .main-header h1 {
        color: white !important;
        font-size: 2.8rem;
        margin: 0;
        text-shadow: 1px 1px 3px rgba(0, 0, 0, 0.2);
        animation: glow 2s infinite alternate;
    }

    @keyframes glow {
        from { text-shadow: 0 0 10px rgba(255, 255, 255, 0.5); }
        to { text-shadow: 0 0 20px rgba(255, 255, 255, 0.8); }
    }

    /* Карточки */
    .content-card {
        background: var(--card-bg) !important;
        border: 1px solid var(--beige-dark) !important;
        border-radius: 12px !important;
        padding: 1.5rem !important;
        margin-bottom: 1.5rem !important;
        box-shadow: var(--shadow-glow) !important;
        backdrop-filter: blur(5px);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .content-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(255, 160, 122, 0.4) !important;
    }

    .metric-card {
        background: linear-gradient(135deg, var(--card-bg) 0%, rgba(255, 255, 255, 0.98) 100%);
        border: 2px solid var(--peach-primary) !important;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(255, 160, 122, 0.3);
        transition: all 0.3s ease;
    }

    .metric-card:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(255, 160, 122, 0.5);
    }

    /* Кнопки */
    .stButton > button {
        border-radius: 8px !important;
        padding: 10px 24px !important;
        font-weight: 600 !important;
        font-size: 14px !important;
        transition: all 0.3s ease !important;
        border: none !important;
        position: relative;
        overflow: hidden;
    }

    .stButton > button::after {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 5px;
        height: 5px;
        background: rgba(255, 255, 255, 0.5);
        opacity: 0;
        border-radius: 100%;
        transform: scale(1, 1) translate(-50%);
        transform-origin: 50% 50%;
    }

    .stButton > button:focus:not(:active)::after {
        animation: ripple 1s ease-out;
    }

    @keyframes ripple {
        0% { transform: scale(0, 0); opacity: 0.5; }
        100% { transform: scale(20, 20); opacity: 0; }
    }

    .student-button {
        background: linear-gradient(135deg, var(--peach-primary) 0%, #FF8C69 100%) !important;
        color: white !important;
        box-shadow: 0 3px 10px rgba(255, 160, 122, 0.3) !important;
    }

    .student-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 20px rgba(255, 140, 105, 0.5) !important;
        background: linear-gradient(135deg, #FF8C69 0%, var(--peach-primary) 100%) !important;
    }

    .admin-button {
        background: linear-gradient(135deg, #6A5ACD 0%, #483D8B 100%) !important;
        color: white !important;
        box-shadow: 0 3px 10px rgba(106, 90, 205, 0.3) !important;
    }

    .admin-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 20px rgba(72, 61, 139, 0.5) !important;
        background: linear-gradient(135deg, #483D8B 0%, #6A5ACD 100%) !important;
    }

    /* Кнопка назад */
    .back-button {
        background: white !important;
        border: 2px solid var(--peach-primary) !important;
        color: var(--peach-primary) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1) !important;
    }

    .back-button:hover {
        background: linear-gradient(135deg, var(--peach-light) 0%, white 100%) !important;
        border-color: var(--peach-dark) !important;
        color: var(--peach-dark) !important;
        transform: translateX(-5px) !important;
    }

    /* Сайдбар */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, var(--beige-light) 0%, #FAF0E6 100%) !important;
        border-right: 3px solid var(--peach-primary) !important;
    }

    [data-testid="stSidebar"] .stButton > button {
        width: 100% !important;
        margin-bottom: 10px !important;
        border-radius: 8px !important;
        padding: 12px !important;
        text-align: left !important;
        background: white !important;
        border: 1px solid var(--beige-dark) !important;
        color: var(--text-dark) !important;
        transition: all 0.3s ease !important;
    }

    [data-testid="stSidebar"] .stButton > button:hover {
        background: linear-gradient(135deg, var(--peach-primary) 0%, #FF8C69 100%) !important;
        color: white !important;
        border-color: var(--peach-primary) !important;
        transform: translateX(5px) !important;
        padding-left: 20px !important;
    }

    /* Таблицы */
    .dataframe {
        background: white !important;
        border: 1px solid var(--beige-dark) !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
    }

    .dataframe th {
        background: var(--peach-gradient) !important;
        color: white !important;
        font-weight: 600 !important;
        border: none !important;
        padding: 12px !important;
    }

    .dataframe td {
        color: var(--text-dark) !important;
        border-color: var(--beige-medium) !important;
        padding: 10px !important;
    }

    .dataframe tr:hover {
        background: rgba(255, 160, 122, 0.1) !important;
    }

    /* Логотип в сайдбаре */
    .logo-container {
        text-align: center;
        padding: 25px 0;
        border-bottom: 2px solid var(--peach-primary);
        margin-bottom: 25px;
        background: white;
        border-radius: 0 0 15px 15px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }

    /* Центрирование на странице входа */
    .login-center {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 70vh;
    }

    /* Улучшенные статусные бейджи */
    .status-badge {
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
        transition: all 0.3s ease;
    }

    .status-badge:hover {
        transform: scale(1.05);
    }

    .status-pending { 
        background: linear-gradient(135deg, rgba(255, 152, 0, 0.15) 0%, rgba(255, 152, 0, 0.3) 100%); 
        color: var(--warning); 
        border: 1px solid var(--warning); 
    }

    .status-accepted { 
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.15) 0%, rgba(76, 175, 80, 0.3) 100%); 
        color: var(--success); 
        border: 1px solid var(--success); 
    }

    .status-rejected { 
        background: linear-gradient(135deg, rgba(244, 67, 54, 0.15) 0%, rgba(244, 67, 54, 0.3) 100%); 
        color: var(--danger); 
        border: 1px solid var(--danger); 
    }

    /* Стили для расширенной таблицы */
    .full-table-container {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-top: 20px;
    }
    </style>
    """, unsafe_allow_html=True)


# ========== БАЗА ДАННЫХ ==========
def get_db_connection():
    return sqlite3.connect('keu_career.db', check_same_thread=False)


def init_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблица студентов
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            full_name TEXT NOT NULL,
            course INTEGER NOT NULL,
            specialization TEXT NOT NULL,
            programming_languages TEXT,
            work_experience TEXT,
            portfolio_link TEXT,
            contact_number TEXT,
            email TEXT,
            gpa REAL,
            university TEXT DEFAULT 'Карагандинский экономический университет Казпотребсоюза',
            graduation_year INTEGER,
            is_active INTEGER DEFAULT 1,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
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

    # Таблица откликов
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

    # Добавляем тестовых пользователей если таблица пуста
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Администратор
        admin_password = hashlib.sha256("admin123".encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, full_name, email)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', admin_password, 'admin', 'Администратор Системы', 'admin@keu.edu.kz'))

        # Тестовый студент
        student_password = hashlib.sha256("student123".encode()).hexdigest()
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, full_name, email)
            VALUES (?, ?, ?, ?, ?)
        ''', ('student', student_password, 'student', 'Иванов Иван Иванович', 'student@keu.edu.kz'))

        cursor.execute('''
            INSERT INTO students (user_id, full_name, course, specialization, programming_languages, 
            work_experience, contact_number, email, gpa, graduation_year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (2, 'Айкобенов Диас Кайырбекович', 4, 'Информационные системы', 'Excel, Word, PowerPoint',
              'Практика в банке "Каспи"', '+7 701 123 4567', 'student@keu.edu.kz', 3.8, 2024))

    # Добавляем тестовые вакансии
    cursor.execute("SELECT COUNT(*) FROM vacancies")
    if cursor.fetchone()[0] == 0:
        test_vacancies = [
            ('Kaspi Bank', 'Стажер-экономист', 'Экономика', 3,
             'от 150 000 KZT', 'Анализ финансовых показателей, подготовка отчетов',
             'Знание Excel, базовые знания экономики, ответственность', 'hr@kaspi.kz', '2024-12-31'),
            ('Halyk Bank', 'Ассистент финансового аналитика', 'Финансы', 4,
             '200 000 - 250 000 KZT', 'Помощь в анализе финансовых рынков',
             'Финансовое образование, аналитическое мышление', 'career@halykbank.kz', '2024-12-15'),
            ('Kazpost', 'Менеджер по продажам', 'Менеджмент', 3,
             '180 000 - 220 000 KZT', 'Работа с клиентами, развитие продаж',
             'Коммуникабельность, стрессоустойчивость', 'jobs@kazpost.kz', '2024-11-30'),
        ]

        cursor.executemany('''
            INSERT INTO vacancies 
            (company_name, position, specialization, required_course, salary_range,
             description, requirements, contact_email, application_deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', test_vacancies)

    conn.commit()
    conn.close()


# ========== АВТОРИЗАЦИЯ ==========
def login_page():
    # Создаем единый контейнер с заголовком внутри
    st.markdown('<div class="login-center">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.container():
            st.markdown('<div class="login-card">', unsafe_allow_html=True)

            # ЗАГОЛОВОК ВНУТРИ КАРТОЧКИ
            st.markdown("""
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: var(--peach-dark); margin: 0 0 10px 0;">🎓 КЭУ Карьерный Центр</h1>
                <p style="color: var(--text-light); margin: 5px 0;">Карагандинский экономический университет Казпотребсоюза</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Создаем вкладки для Входа и Регистрации
            tab1, tab2 = st.tabs(["🔐 **Вход**", "📝 **Регистрация**"])
            
            with tab1:
                # Форма входа
                username = st.text_input("**Логин**", key="login_username", 
                                       placeholder="Введите ваш логин")
                password = st.text_input("**Пароль**", type="password", key="login_password",
                                       placeholder="Введите ваш пароль")

                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.button("**Войти**", key="login_button", use_container_width=True, type="primary"):
                        if authenticate_user(username, password):
                            st.success("✅ Успешный вход!")
                            st.rerun()
                        else:
                            st.error("❌ Неверный логин или пароль")

                with col_btn2:
                    if st.button("**Демо-доступ**", key="demo_button", use_container_width=True):
                        st.info("""
                        **Тестовые данные:**
                        - Администратор: admin / admin123
                        - Студент: student / student123
                        """)
            
            with tab2:
                # Форма регистрации
                st.markdown("#### Создание нового аккаунта")
                
                full_name = st.text_input("**ФИО**", key="reg_full_name",
                                        placeholder="Иванов Иван Иванович")
                
                email = st.text_input("**Email**", key="reg_email",
                                    placeholder="example@keu.edu.kz")
                
                username_reg = st.text_input("**Логин**", key="reg_username",
                                           placeholder="Придумайте логин")
                
                col_pass1, col_pass2 = st.columns(2)
                with col_pass1:
                    password_reg = st.text_input("**Пароль**", type="password", key="reg_password",
                                               placeholder="Минимум 6 символов")
                
                with col_pass2:
                    password_confirm = st.text_input("**Подтвердите пароль**", type="password", key="reg_password_confirm",
                                                   placeholder="Повторите пароль")
                
                # Выбор роли
                role = st.selectbox("**Роль**", ["Студент", "Преподаватель"], key="reg_role")
                
                # Кнопка регистрации
                if st.button("📝 **Зарегистрироваться**", key="register_button", use_container_width=True, type="primary"):
                    # Валидация
                    if not all([full_name, email, username_reg, password_reg, password_confirm]):
                        st.error("❌ Заполните все поля")
                    elif password_reg != password_confirm:
                        st.error("❌ Пароли не совпадают")
                    elif len(password_reg) < 6:
                        st.error("❌ Пароль должен быть не менее 6 символов")
                    elif '@' not in email:
                        st.error("❌ Введите корректный email")
                    else:
                        # Регистрируем пользователя
                        if register_user(full_name, email, username_reg, password_reg, role):
                            st.success("✅ Регистрация успешна! Теперь войдите в систему.")
                            st.balloons()
                            # Автоматически переключаемся на вкладку входа
                            st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


def authenticate_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    # Позволяем входить по username ИЛИ email
    cursor.execute('''
        SELECT id, username, role, full_name 
        FROM users 
        WHERE (username = ? OR email = ?) AND password_hash = ?
    ''', (username, username, password_hash))

    user = cursor.fetchone()
    conn.close()

    if user:
        st.session_state.user = {
            'id': user[0],
            'username': user[1],
            'role': user[2],
            'full_name': user[3]
        }
        st.session_state.page = 'dashboard'
        return True
    return False


def logout():
    if 'user' in st.session_state:
        del st.session_state.user
    st.session_state.page = 'login'
    st.rerun()

def register_user(full_name, email, username, password, role):
    """Регистрация нового пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Проверяем, существует ли пользователь
        cursor.execute('SELECT COUNT(*) FROM users WHERE username = ? OR email = ?', 
                      (username, email))
        if cursor.fetchone()[0] > 0:
            st.error("❌ Пользователь с таким логином или email уже существует")
            return False
        
        # Хэшируем пароль
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Сохраняем роль в нужном формате
        role_db = 'student' if role == 'Студент' else 'teacher'
        
        # Добавляем пользователя
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, full_name, email)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, password_hash, role_db, full_name, email))
        
        # Если это студент, добавляем запись в таблицу students
        if role_db == 'student':
            user_id = cursor.lastrowid
            
            cursor.execute('''
                INSERT INTO students (user_id, full_name, email, course, specialization, gpa, graduation_year)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, full_name, email, 1, 'Экономика', 3.0, 2024))
        
        conn.commit()
        st.session_state.show_login_tab = True  # Флаг для переключения на вкладку входа
        return True
        
    except Exception as e:
        st.error(f"❌ Ошибка при регистрации: {str(e)}")
        return False
    finally:
        conn.close()

# ========== CRUD ОПЕРАЦИИ ==========
class DatabaseManager:
    def __init__(self):
        pass

    def execute_query(self, query, params=()):
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor
        finally:
            conn.close()

    def execute_read_query(self, query, params=()):
        conn = get_db_connection()
        try:
            return pd.read_sql_query(query, conn, params=params)
        finally:
            conn.close()

    # Студенты
    def insert_student(self, user_id, data):
        query = '''
            INSERT INTO students 
            (user_id, full_name, course, specialization, programming_languages, 
             work_experience, portfolio_link, contact_number, email, gpa, graduation_year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.execute_query(query, (user_id, *data))
        return True

    def get_all_students(self):
        query = "SELECT * FROM students ORDER BY registration_date DESC"
        return self.execute_read_query(query)

    def get_student_by_user_id(self, user_id):
        query = "SELECT * FROM students WHERE user_id = ?"
        result = self.execute_read_query(query, (user_id,))
        if not result.empty:
            return result.iloc[0]
        return None

    def update_student(self, user_id, data):
        query = '''
            UPDATE students SET
            full_name = ?, course = ?, specialization = ?, programming_languages = ?,
            work_experience = ?, portfolio_link = ?, contact_number = ?,
            email = ?, gpa = ?, graduation_year = ?, is_active = ?
            WHERE user_id = ?
        '''
        self.execute_query(query, (*data, user_id))
        return True

    # Вакансии
    def get_all_vacancies(self):
        query = "SELECT * FROM vacancies WHERE is_active = 1 ORDER BY posted_date DESC"
        return self.execute_read_query(query)

    def insert_vacancy(self, data):
        query = '''
            INSERT INTO vacancies 
            (company_name, position, specialization, required_course, salary_range,
             description, requirements, contact_email, application_deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.execute_query(query, data)
        return True

    # Отклики
    def apply_for_vacancy(self, student_id, vacancy_id, cover_letter=""):
        query = '''
            INSERT INTO applications (student_id, vacancy_id, cover_letter)
            VALUES (?, ?, ?)
        '''
        self.execute_query(query, (student_id, vacancy_id, cover_letter))
        return True

    def get_applications_by_student(self, student_id):
        query = '''
            SELECT a.*, v.position, v.company_name, v.salary_range
            FROM applications a
            JOIN vacancies v ON a.vacancy_id = v.id
            WHERE a.student_id = ?
            ORDER BY a.application_date DESC
        '''
        return self.execute_read_query(query, (student_id,))

    def get_all_applications(self):
        query = '''
            SELECT a.*, s.full_name, s.email as student_email, s.contact_number, 
                   v.position, v.company_name, v.salary_range
            FROM applications a
            LEFT JOIN students s ON a.student_id = s.id
            LEFT JOIN vacancies v ON a.vacancy_id = v.id
            ORDER BY a.application_date DESC
        '''
        return self.execute_read_query(query)

    def get_recent_applications(self, limit=10):
        query = '''
            SELECT a.*, s.full_name, v.position, v.company_name
            FROM applications a
            LEFT JOIN students s ON a.student_id = s.id
            LEFT JOIN vacancies v ON a.vacancy_id = v.id
            WHERE s.full_name IS NOT NULL AND v.position IS NOT NULL
            ORDER BY a.application_date DESC
            LIMIT ?
        '''
        return self.execute_read_query(query, (limit,))

    def update_application_status(self, application_id, status):
        query = "UPDATE applications SET status = ? WHERE id = ?"
        self.execute_query(query, (status, application_id))
        return True

    # Статистика
    def get_statistics(self):
        query = '''
            SELECT 
                (SELECT COUNT(*) FROM students) as total_students,
                (SELECT COUNT(*) FROM students WHERE is_active = 1) as active_students,
                (SELECT COUNT(*) FROM vacancies WHERE is_active = 1) as active_vacancies,
                (SELECT COUNT(*) FROM applications) as total_applications,
                (SELECT COUNT(*) FROM applications WHERE status = 'accepted') as accepted_applications,
                (SELECT COUNT(*) FROM applications WHERE status = 'pending') as pending_applications,
                (SELECT AVG(gpa) FROM students WHERE gpa IS NOT NULL) as avg_gpa
        '''
        result = self.execute_read_query(query)
        if not result.empty:
            return result.iloc[0]
        return pd.Series([0, 0, 0, 0, 0, 0, 0],
                         index=['total_students', 'active_students', 'active_vacancies',
                                'total_applications', 'accepted_applications', 'pending_applications', 'avg_gpa'])


# ========== ГЛОБАЛЬНЫЕ НАСТРОЙКИ ==========
COURSE_OPTIONS = [1, 2, 3, 4]
SPECIALIZATION_OPTIONS = [
    "Экономика", "Менеджмент", "Финансы", "Бухгалтерский учет",
    "Маркетинг", "Логистика", "ITA", "Цифровой дизайн", "Информационные системы"
]
SKILL_OPTIONS = [
    "Excel", "Word", "PowerPoint", "1С", "SQL", "Python", "SPSS",
    "Бухгалтерия", "Финансовый анализ", "Маркетинговые исследования",
    "S#", "JavaScript", "HTML/CSS", "Data Analysis", "Project Management"
]


def init_session_state():
    defaults = {
        'page': 'login',
        'edit_mode': False,
        'current_vacancy_id': None,
        'db_manager': DatabaseManager()
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    init_database()


# ========== КОМПОНЕНТЫ ИНТЕРФЕЙСА ==========
def create_header():
    st.markdown("""
    <div class="main-header">
        <h1>🎓 ТВОЯ КАРЬЕРА ОТ КЭУ</h1>
        <p>Карагандинский экономический университет Казпотребсоюза</p>
        <p>Платформа для трудоустройства студентов</p>
    </div>
    """, unsafe_allow_html=True)


def metric_card(title, value, icon="📊", change=None):
    change_html = ""
    if change:
        color = "var(--success)" if change > 0 else "var(--danger)" if change < 0 else "var(--text-light)"
        change_html = f'<div style="font-size: 0.9rem; color: {color}; margin-top: 5px;">{change:+}%</div>'

    st.markdown(f"""
    <div class="metric-card">
        <div style="font-size: 2.5rem; margin-bottom: 10px; color: var(--peach-dark);">{icon}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-label">{title}</div>
        {change_html}
    </div>
    """, unsafe_allow_html=True)


def back_button():
    """Универсальная кнопка назад"""
    if st.button("⬅️ Назад", key="back_button"):
        st.session_state.page = 'dashboard'
        st.rerun()


# ========== САЙДБАР ==========
def create_sidebar():
    with st.sidebar:
        # Логотип
        st.markdown("""
        <div class="logo-container">
            <div style="font-size: 3.5rem; color: var(--peach-dark);">🎓</div>
            <h2>КЭУ Казпотребсоюза</h2>
            <p>Карьерный центр</p>
        </div>
        """, unsafe_allow_html=True)

        # Профиль пользователя
        user = st.session_state.user
        st.markdown(f"""
        <div class="user-profile">
            <div style="font-size: 2rem; color: var(--peach-primary);">
                {'👨‍💼' if user['role'] == 'admin' else '👨‍🎓'}
            </div>
            <h4>{user['full_name']}</h4>
            <div class="user-role">
                {'Администратор' if user['role'] == 'admin' else 'Студент'}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Разделитель
        st.markdown("---")

        # Навигация для студентов
        if user['role'] == 'student':
            nav_items = [
                ("🏠 Главная", "dashboard"),
                ("👤 Мой профиль", "profile"),
                ("💼 Вакансии", "vacancies"),
                ("📨 Мои отклики", "my_applications"),
                ("📊 Статистика", "stats")
            ]
        # Навигация для админа
        else:
            nav_items = [
                ("🏠 Главная", "dashboard"),
                ("👨‍🎓 Все студенты", "students"),
                ("👨‍🎓 Детальная таблица", "students_detailed"),
                ("💼 Вакансии", "vacancies"),
                ("📨 Все отклики", "applications"),
                ("📊 Аналитика", "analytics"),
                ("➕ Новая вакансия", "add_vacancy")
            ]

        # Создаем кнопки навигации с уникальными ключами
        for i, (label, page_key) in enumerate(nav_items):
            button_type = "admin" if user['role'] == 'admin' else "student"
            key = f"nav_{page_key}_{i}_{user['role']}"

            if st.button(label, key=key, use_container_width=True):
                st.session_state.page = page_key
                st.rerun()

        st.markdown("---")

        # Статистика в сайдбаре
        try:
            stats = st.session_state.db_manager.get_statistics()
            st.markdown(f"""
            <div style="background: white; padding: 15px; border-radius: 10px; border: 2px solid var(--peach-light); 
                         box-shadow: 0 3px 10px rgba(0, 0, 0, 0.1);">
                <h4 style="color: var(--peach-dark); margin: 0 0 10px 0; text-align: center;">
                    📊 Быстрая статистика
                </h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div style="text-align: center;">
                        <div style="font-size: 1.2rem; font-weight: 700; color: var(--peach-dark);">{stats['total_students']}</div>
                        <div style="font-size: 0.8rem; color: var(--text-light);">Студентов</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.2rem; font-weight: 700; color: var(--peach-dark);">{stats['active_vacancies']}</div>
                        <div style="font-size: 0.8rem; color: var(--text-light);">Вакансий</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.2rem; font-weight: 700; color: var(--peach-dark);">{stats['total_applications']}</div>
                        <div style="font-size: 0.8rem; color: var(--text-light);">Откликов</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.2rem; font-weight: 700; color: var(--peach-dark);">{stats['accepted_applications']}</div>
                        <div style="font-size: 0.8rem; color: var(--text-light);">Принято</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Ошибка статистики: {e}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Кнопка выхода
        if st.button("🚪 Выйти", key="logout_button", use_container_width=True, type="secondary"):
            logout()


# ========== СТРАНИЦЫ СТУДЕНТА ==========
def student_dashboard():
    create_header()

    user = st.session_state.user
    db = st.session_state.db_manager

    try:
        # Получаем данные студента
        student = db.get_student_by_user_id(user['id'])
        stats = db.get_statistics()

        # Приветствие
        st.markdown(f"""
        <div class="content-card">
            <h2>👋 Добро пожаловать, {user['full_name'].split()[0]}!</h2>
            <p>Рады видеть вас в Карьерном центре КЭУ. Здесь вы можете найти подходящие вакансии и начать свою карьеру.</p>
        </div>
        """, unsafe_allow_html=True)

        # Быстрые действия
        st.subheader("⚡ Быстрые действия")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("👤 Заполнить профиль", key="student_profile_btn", use_container_width=True):
                st.session_state.page = 'profile'
                st.rerun()
        with col2:
            if st.button("💼 Найти вакансии", key="student_vacancies_btn", use_container_width=True):
                st.session_state.page = 'vacancies'
                st.rerun()
        with col3:
            if st.button("📨 Мои отклики", key="student_applications_btn", use_container_width=True):
                st.session_state.page = 'my_applications'
                st.rerun()

        # Статистика
        st.subheader("📊 Ваша статистика")
        col_stat1, col_stat2, col_stat3 = st.columns(3)
        with col_stat1:
            metric_card("Активных вакансий", stats['active_vacancies'], "💼")
        with col_stat2:
            if student is not None:
                metric_card("Ваш GPA", f"{student['gpa']:.2f}", "⭐")
            else:
                metric_card("Заполните профиль", "→", "📝")
        with col_stat3:
            metric_card("Всего студентов", stats['total_students'], "👨‍🎓")

        # Последние вакансии
        st.subheader("🔥 Последние вакансии")
        vacancies = db.get_all_vacancies()
        if not vacancies.empty:
            for i, vacancy in vacancies.head(3).iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="content-card">
                        <h4 style="color: var(--peach-dark); margin: 0;">{vacancy['position']}</h4>
                        <p style="color: var(--peach-primary); font-weight: 600; margin: 5px 0;">{vacancy['company_name']}</p>
                        <p style="margin: 5px 0;">
                            💰 <strong>Зарплата:</strong> {vacancy['salary_range']}<br>
                            🎯 <strong>Специальность:</strong> {vacancy['specialization']}
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("📨 Откликнуться", key=f"quick_apply_{vacancy['id']}"):
                            if student is not None:
                                st.session_state.current_vacancy_id = vacancy['id']
                                st.session_state.page = 'apply_vacancy'
                                st.rerun()
                            else:
                                st.warning("Сначала заполните свой профиль!")
                    with col_btn2:
                        if st.button("📋 Подробнее", key=f"details_{vacancy['id']}"):
                            with st.expander("Подробная информация"):
                                st.write(f"**Описание:** {vacancy['description']}")
                                st.write(f"**Требования:** {vacancy['requirements']}")
                                st.write(f"**Контакты:** {vacancy['contact_email']}")
                                st.write(f"**Дедлайн:** {vacancy['application_deadline']}")
                    st.markdown("---")
        else:
            st.info("Пока нет активных вакансий")

    except Exception as e:
        st.error(f"Ошибка: {str(e)}")


def student_profile():
    st.header("👤 Мой профиль")
    back_button()

    user = st.session_state.user
    db = st.session_state.db_manager

    # Получаем текущие данные студента
    student = db.get_student_by_user_id(user['id'])

    with st.form("student_profile_form", clear_on_submit=False):
        st.markdown('<div class="content-card">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            full_name = st.text_input("ФИО *",
                                      value=student['full_name'] if student is not None else user['full_name'],
                                      key="profile_full_name")
            course = st.selectbox("Курс *", COURSE_OPTIONS,
                                  index=3 if student is None else COURSE_OPTIONS.index(student['course']) if student[
                                                                                                                 'course'] in COURSE_OPTIONS else 3,
                                  key="profile_course")
            specialization = st.selectbox("Специальность *", SPECIALIZATION_OPTIONS,
                                          index=0 if student is None else SPECIALIZATION_OPTIONS.index(
                                              student['specialization']) if student[
                                                                                'specialization'] in SPECIALIZATION_OPTIONS else 0,
                                          key="profile_specialization")
            email = st.text_input("Email *",
                                  value=student['email'] if student is not None else "",
                                  key="profile_email")

        with col2:
            contact_number = st.text_input("Контактный номер *",
                                           value=student['contact_number'] if student is not None else "",
                                           key="profile_phone")
            programming_languages = st.multiselect("Навыки и технологии", SKILL_OPTIONS,
                                                   default=student['programming_languages'].split(
                                                       ', ') if student is not None and student[
                                                       'programming_languages'] else [],
                                                   key="profile_skills")
            gpa = st.number_input("Средний балл (GPA)", min_value=0.0, max_value=4.0, step=0.1,
                                  value=float(student['gpa']) if student is not None and student['gpa'] else 3.0,
                                  key="profile_gpa")
            graduation_year = st.number_input("Год выпуска", min_value=2024, max_value=2030,
                                              value=int(student['graduation_year']) if student is not None and student[
                                                  'graduation_year'] else 2024,
                                              key="profile_year")

        work_experience = st.text_area("Опыт работы и практики",
                                       value=student['work_experience'] if student is not None else "",
                                       height=120,
                                       placeholder="Опишите ваш опыт работы, практики, проекты...",
                                       key="profile_experience")

        portfolio_link = st.text_input("Ссылка на портфолио (опционально)",
                                       value=student['portfolio_link'] if student is not None else "",
                                       placeholder="https://...",
                                       key="profile_portfolio")

        is_active = st.checkbox("Активно ищу работу/стажировку",
                                value=bool(student['is_active']) if student is not None else True,
                                key="profile_active")

        st.markdown('</div>', unsafe_allow_html=True)

        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
        with col_btn1:
            submitted = st.form_submit_button("💾 Сохранить", use_container_width=True, key="profile_submit")
        with col_btn2:
            if st.form_submit_button("❌ Отмена", use_container_width=True, key="profile_cancel"):
                st.session_state.page = 'dashboard'
                st.rerun()

        if submitted:
            if all([full_name, email, contact_number]):
                skills_str = ", ".join(programming_languages)
                student_data = (
                    full_name, course, specialization, skills_str,
                    work_experience, portfolio_link, contact_number,
                    email, gpa, graduation_year, int(is_active)
                )

                try:
                    if student is not None:
                        # Обновляем существующую запись
                        db.update_student(user['id'], student_data)
                        st.success("✅ Профиль успешно обновлен!")
                    else:
                        # Создаем новую запись
                        db.insert_student(user['id'], student_data)
                        st.success("✅ Профиль успешно создан!")
                        st.balloons()

                    st.session_state.page = 'dashboard'
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Ошибка сохранения: {str(e)}")
            else:
                st.warning("⚠️ Пожалуйста, заполните все обязательные поля (отмечены *)")


def student_vacancies():
    st.header("💼 Доступные вакансии")
    back_button()

    db = st.session_state.db_manager

    try:
        vacancies = db.get_all_vacancies()

        if not vacancies.empty:
            # Фильтры
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                search_query = st.text_input("🔍 Поиск", placeholder="Должность, компания...", key="vacancy_search")
            with col_filter2:
                spec_filter = st.selectbox("Специальность", ["Все"] + SPECIALIZATION_OPTIONS, key="vacancy_spec_filter")

            # Применяем фильтры
            filtered_vacancies = vacancies.copy()
            if search_query:
                filtered_vacancies = filtered_vacancies[
                    filtered_vacancies['position'].str.contains(search_query, case=False, na=False) |
                    filtered_vacancies['company_name'].str.contains(search_query, case=False, na=False)
                    ]
            if spec_filter != "Все":
                filtered_vacancies = filtered_vacancies[filtered_vacancies['specialization'] == spec_filter]

            # Отображаем вакансии
            for i, vacancy in filtered_vacancies.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="content-card">
                        <h3 style="color: var(--peach-dark); margin: 0;">{vacancy['position']}</h3>
                        <p style="color: var(--peach-primary); font-size: 1.1rem; font-weight: 600; margin: 5px 0;">
                            {vacancy['company_name']}
                        </p>
                        <div style="display: flex; flex-wrap: wrap; gap: 10px; margin: 15px 0;">
                            <span style="background: var(--peach-light); color: var(--peach-dark); 
                                    padding: 6px 12px; border-radius: 20px; font-size: 0.9rem;">
                                🎯 {vacancy['specialization']}
                            </span>
                            <span style="background: rgba(255, 160, 122, 0.2); color: var(--peach-dark); 
                                    padding: 6px 12px; border-radius: 20px; font-size: 0.9rem;">
                                📚 Курс {vacancy['required_course']}+
                            </span>
                            <span style="background: rgba(255, 152, 0, 0.1); color: var(--warning); 
                                    padding: 6px 12px; border-radius: 20px; font-size: 0.9rem;">
                                💰 {vacancy['salary_range']}
                            </span>
                        </div>
                        <p style="color: var(--text-dark); line-height: 1.6;">
                            {vacancy['description'][:200]}...
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        if st.button("📨 Откликнуться", key=f"apply_vac_{vacancy['id']}", use_container_width=True):
                            # Проверяем, заполнен ли профиль
                            student = db.get_student_by_user_id(st.session_state.user['id'])
                            if student is not None:
                                st.session_state.current_vacancy_id = vacancy['id']
                                st.session_state.page = 'apply_vacancy'
                                st.rerun()
                            else:
                                st.warning("Сначала заполните свой профиль в разделе 'Мой профиль'")
                    with col_btn2:
                        if st.button("📋 Подробнее", key=f"more_vac_{vacancy['id']}", use_container_width=True):
                            with st.expander("Полная информация о вакансии", expanded=True):
                                st.write(f"**Описание:**")
                                st.write(vacancy['description'])
                                st.write(f"**Требования:**")
                                st.write(vacancy['requirements'])
                                st.write(f"**Контакты:** {vacancy['contact_email']}")
                                st.write(f"**Дедлайн подачи:** {vacancy['application_deadline']}")
                    st.markdown("---")
        else:
            st.info("💼 Активных вакансий пока нет")

    except Exception as e:
        st.error(f"Ошибка: {str(e)}")


def student_apply_vacancy():
    st.header("📨 Отклик на вакансию")
    back_button()

    if 'current_vacancy_id' not in st.session_state:
        st.warning("Сначала выберите вакансию для отклика")
        if st.button("⬅️ К вакансиям", key="back_to_vacancies"):
            st.session_state.page = 'vacancies'
            st.rerun()
        return

    db = st.session_state.db_manager
    user = st.session_state.user

    try:
        # Получаем информацию о вакансии
        vacancies = db.get_all_vacancies()
        vacancy = vacancies[vacancies['id'] == st.session_state.current_vacancy_id].iloc[0]

        # Получаем данные студента
        student = db.get_student_by_user_id(user['id'])

        if student is None:
            st.error("Сначала заполните свой профиль!")
            if st.button("👤 Заполнить профиль", key="fill_profile_first"):
                st.session_state.page = 'profile'
                st.rerun()
            return

        st.markdown(f"""
        <div class="content-card">
            <h3>{vacancy['position']}</h3>
            <p style="font-size: 1.1rem; color: var(--peach-primary);">
                Компания: <strong>{vacancy['company_name']}</strong>
            </p>
            <p>Зарплата: <strong>{vacancy['salary_range']}</strong></p>
            <p>Требуемый курс: <strong>{vacancy['required_course']}+</strong></p>
        </div>
        """, unsafe_allow_html=True)

        st.subheader("Ваши данные")
        st.info(f"""
        **ФИО:** {student['full_name']}
        **Специальность:** {student['specialization']}
        **Курс:** {student['course']}
        **GPA:** {student['gpa']}
        **Email:** {student['email']}
        **Телефон:** {student['contact_number']}
        """)

        st.subheader("Сопроводительное письмо")
        cover_letter = st.text_area(
            "Расскажите, почему вы подходите для этой должности",
            height=150,
            placeholder="Опишите ваш опыт, навыки и почему вы хотите работать в этой компании...",
            key="cover_letter_text"
        )

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            if st.button("📤 Отправить отклик", key="send_application", use_container_width=True):
                try:
                    db.apply_for_vacancy(student['id'], vacancy['id'], cover_letter)
                    st.success("✅ Ваш отклик успешно отправлен!")
                    st.balloons()

                    # Очищаем состояние и возвращаемся
                    del st.session_state.current_vacancy_id
                    st.session_state.page = 'my_applications'
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Ошибка при отправке: {str(e)}")

        with col_btn2:
            if st.button("❌ Отмена", key="cancel_application", use_container_width=True):
                del st.session_state.current_vacancy_id
                st.session_state.page = 'vacancies'
                st.rerun()

    except Exception as e:
        st.error(f"Ошибка: {str(e)}")


def student_my_applications():
    st.header("📨 Мои отклики")
    back_button()

    user = st.session_state.user
    db = st.session_state.db_manager

    try:
        # Получаем данные студента
        student = db.get_student_by_user_id(user['id'])

        if student is None:
            st.info("У вас еще нет профиля. Сначала заполните его.")
            if st.button("👤 Заполнить профиль", key="create_profile_for_apps"):
                st.session_state.page = 'profile'
                st.rerun()
            return

        # Получаем отклики студента
        applications = db.get_applications_by_student(student['id'])

        if not applications.empty:
            # Статистика
            status_counts = applications['status'].value_counts()

            col_stat1, col_stat2, col_stat3 = st.columns(3)
            with col_stat1:
                st.metric("Всего откликов", len(applications))
            with col_stat2:
                pending = status_counts.get('pending', 0)
                st.metric("На рассмотрении", pending)
            with col_stat3:
                accepted = status_counts.get('accepted', 0)
                st.metric("Принято", accepted)

            # Список откликов
            for i, app in applications.iterrows():
                status_class = f"status-{app['status']}"
                status_text = {
                    'pending': '⏳ На рассмотрении',
                    'accepted': '✅ Принято',
                    'rejected': '❌ Отклонено'
                }.get(app['status'], app['status'])

                st.markdown(f"""
                <div class="content-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4 style="margin: 0; color: var(--peach-dark);">{app['position']}</h4>
                            <p style="margin: 5px 0; color: var(--peach-primary);">{app['company_name']}</p>
                            <p style="margin: 0;"><strong>Дата отклика:</strong> {app['application_date'][:10]}</p>
                            <p style="margin: 0;"><strong>Зарплата:</strong> {app['salary_range']}</p>
                        </div>
                        <span class="status-badge {status_class}">{status_text}</span>
                    </div>
                    {f'<p style="margin-top: 10px;"><strong>Сопроводительное письмо:</strong><br>{app["cover_letter"]}</p>' if app['cover_letter'] else ''}
                </div>
                """, unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("📭 У вас пока нет откликов на вакансии")
            if st.button("💼 Найти вакансии", key="find_vacancies_from_apps"):
                st.session_state.page = 'vacancies'
                st.rerun()

    except Exception as e:
        st.error(f"Ошибка: {str(e)}")


def student_stats():
    st.header("📊 Статистика")
    back_button()

    db = st.session_state.db_manager
    user = st.session_state.user

    try:
        student = db.get_student_by_user_id(user['id'])
        stats = db.get_statistics()

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.subheader("📈 Общая статистика")

            st.metric("Всего студентов", stats['total_students'])
            st.metric("Активных вакансий", stats['active_vacancies'])
            st.metric("Всего откликов", stats['total_applications'])

            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="content-card">', unsafe_allow_html=True)
            st.subheader("👤 Ваша статистика")

            if student is not None:
                # Получаем отклики студента
                applications = db.get_applications_by_student(student['id'])

                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.metric("Ваш GPA", f"{student['gpa']:.2f}")
                with col_stat2:
                    st.metric("Ваш курс", student['course'])

                if not applications.empty:
                    status_counts = applications['status'].value_counts()
                    st.write("**Ваши отклики:**")
                    st.write(f"- Всего: {len(applications)}")
                    st.write(f"- На рассмотрении: {status_counts.get('pending', 0)}")
                    st.write(f"- Принято: {status_counts.get('accepted', 0)}")
                else:
                    st.info("У вас пока нет откликов")
            else:
                st.info("Заполните свой профиль")
                if st.button("👤 Заполнить профиль", key="fill_profile_stats"):
                    st.session_state.page = 'profile'
                    st.rerun()

            st.markdown('</div>', unsafe_allow_html=True)

        # Статистика по вакансиям
        st.subheader("💼 Статистика по вакансиям")

        vacancies = db.get_all_vacancies()
        if not vacancies.empty:
            # Самые популярные специальности в вакансиях
            spec_counts = vacancies['specialization'].value_counts()
            st.write("**Вакансии по специальностям:**")
            for spec, count in spec_counts.items():
                percentage = (count / len(vacancies)) * 100
                st.progress(percentage / 100, text=f"{spec}: {count} вакансий ({percentage:.1f}%)")

    except Exception as e:
        st.error(f"Ошибка: {str(e)}")


# ========== СТРАНИЦЫ АДМИНА ==========
def admin_dashboard():
    create_header()

    db = st.session_state.db_manager

    try:
        stats = db.get_statistics()

        st.markdown(f"""
        <div class="content-card">
            <h2>👨‍💼 Панель администратора</h2>
            <p>Добро пожаловать в систему управления карьерным центром КЭУ</p>
        </div>
        """, unsafe_allow_html=True)

        # Основные метрики
        st.subheader("📊 Ключевые показатели")

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card("Всего студентов", stats['total_students'], "👨‍🎓")
        with col2:
            metric_card("Активных", stats['active_students'], "🔍")
        with col3:
            metric_card("Вакансий", stats['active_vacancies'], "💼")
        with col4:
            metric_card("Откликов", stats['total_applications'], "📨")

        # Быстрые действия
        st.subheader("⚡ Быстрые действия")

        col_actions1, col_actions2, col_actions3, col_actions4 = st.columns(4)
        with col_actions1:
            if st.button("➕ Новая вакансия", key="admin_new_vacancy", use_container_width=True):
                st.session_state.page = 'add_vacancy'
                st.rerun()
        with col_actions2:
            if st.button("👨‍🎓 Все студенты", key="admin_all_students", use_container_width=True):
                st.session_state.page = 'students'
                st.rerun()
        with col_actions3:
            if st.button("📨 Все отклики", key="admin_all_apps", use_container_width=True):
                st.session_state.page = 'applications'
                st.rerun()
        with col_actions4:
            if st.button("📊 Аналитика", key="admin_analytics", use_container_width=True):
                st.session_state.page = 'analytics'
                st.rerun()

        # Последние отклики - ИСПРАВЛЕНО
        # Последние отклики - ИСПРАВЛЕНО
        st.subheader("🔄 Последние отклики")

        applications = db.get_recent_applications(10)
        if not applications.empty and not applications.isna().all().all():
            for i, app in applications.iterrows():
                # Проверяем наличие данных
                student_name = app['full_name'] if pd.notna(app['full_name']) else "Не указано"
                position = app['position'] if pd.notna(app['position']) else "Не указано"
                company = app['company_name'] if pd.notna(app['company_name']) else "Не указано"
                status = app['status'] if pd.notna(app['status']) else 'pending'

                status_class = f"status-{status}"
                status_text = {
                    'pending': '⏳ Ожидает',
                    'accepted': '✅ Принято',
                    'rejected': '❌ Отклонено'
                }.get(status, 'pending')

                date_str = str(app['application_date'])[:10] if pd.notna(app['application_date']) else "Не указана"

                st.markdown(f"""
                <div class="content-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4 style="margin: 0; color: var(--peach-dark);">{position}</h4>
                            <p style="margin: 5px 0; color: var(--peach-primary);">{company}</p>
                            <p style="margin: 0;"><strong>Студент:</strong> {student_name}</p>
                            <p style="margin: 5px 0;"><strong>Дата:</strong> {date_str}</p>
                        </div>
                        <span class="status-badge {status_class}">{status_text}</span>
                    </div>
                    {f'<p style="margin-top: 10px;"><strong>Сопроводительное письмо:</strong><br>{app["cover_letter"]}</p>' if pd.notna(app["cover_letter"]) and app["cover_letter"] else ''}
                </div>
                """, unsafe_allow_html=True)
                st.markdown("---")
        else:
            st.info("Пока нет откликов")

    except Exception as e:
        st.error(f"Ошибка: {str(e)}")


def admin_students():
    st.header("👨‍🎓 Управление студентами")
    back_button()

    db = st.session_state.db_manager

    try:
        students = db.get_all_students()

        if not students.empty:
            # Поиск и фильтры
            col_filter1, col_filter2, col_filter3 = st.columns(3)
            with col_filter1:
                search_name = st.text_input("Поиск по ФИО", key="admin_search_name")
            with col_filter2:
                search_course = st.selectbox("Курс", ["Все"] + COURSE_OPTIONS, key="admin_search_course")
            with col_filter3:
                search_spec = st.selectbox("Специальность", ["Все"] + SPECIALIZATION_OPTIONS, key="admin_search_spec")

            # Применяем фильтры
            filtered_students = students.copy()
            if search_name:
                filtered_students = filtered_students[
                    filtered_students['full_name'].str.contains(search_name, case=False, na=False)]
            if search_course != "Все":
                filtered_students = filtered_students[filtered_students['course'] == search_course]
            if search_spec != "Все":
                filtered_students = filtered_students[filtered_students['specialization'] == search_spec]

            # Таблица студентов
            display_df = filtered_students[
                ['full_name', 'course', 'specialization', 'gpa', 'is_active', 'email', 'contact_number']].copy()
            display_df['is_active'] = display_df['is_active'].apply(lambda x: '✅' if x == 1 else '❌')

            st.dataframe(
                display_df.rename(columns={
                    'full_name': 'ФИО',
                    'course': 'Курс',
                    'specialization': 'Специальность',
                    'gpa': 'GPA',
                    'is_active': 'Активен',
                    'email': 'Email',
                    'contact_number': 'Телефон'
                }),
                use_container_width=True,
                hide_index=True
            )

            # Статистика
            st.subheader("📊 Статистика студентов")

            col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
            with col_stat1:
                st.metric("Всего студентов", len(students))
            with col_stat2:
                active_count = len(students[students['is_active'] == 1])
                st.metric("Активно ищут", active_count)
            with col_stat3:
                avg_gpa = students['gpa'].mean() if 'gpa' in students.columns and not students[
                    'gpa'].isna().all() else 0
                st.metric("Средний GPA", f"{avg_gpa:.2f}")
            with col_stat4:
                most_popular = students['specialization'].mode()[0] if not students[
                    'specialization'].mode().empty else "Нет данных"
                st.metric("Популярная спец.", most_popular)

        else:
            st.info("Пока нет зарегистрированных студентов")

    except Exception as e:
        st.error(f"Ошибка: {str(e)}")


def admin_students_detailed():
    st.header("👨‍🎓 Детальная таблица студентов")
    back_button()

    db = st.session_state.db_manager

    try:
        students = db.get_all_students()

        if not students.empty:
            st.markdown('<div class="full-table-container">', unsafe_allow_html=True)

            # Поиск и фильтры
            col1, col2, col3 = st.columns(3)
            with col1:
                search_name = st.text_input("🔍 Поиск по ФИО", key="detailed_search_name")
            with col2:
                search_course = st.selectbox("🎓 Курс", ["Все"] + COURSE_OPTIONS, key="detailed_search_course")
            with col3:
                search_spec = st.selectbox("🎯 Специальность", ["Все"] + SPECIALIZATION_OPTIONS,
                                           key="detailed_search_spec")

            # Применяем фильтры
            filtered_students = students.copy()
            if search_name:
                filtered_students = filtered_students[
                    filtered_students['full_name'].str.contains(search_name, case=False, na=False)]
            if search_course != "Все":
                filtered_students = filtered_students[filtered_students['course'] == search_course]
            if search_spec != "Все":
                filtered_students = filtered_students[filtered_students['specialization'] == search_spec]

            # Детальная таблица
            display_df = filtered_students[[
                'full_name', 'course', 'specialization', 'gpa', 'email',
                'contact_number', 'programming_languages', 'graduation_year',
                'work_experience', 'is_active'
            ]].copy()

            display_df['is_active'] = display_df['is_active'].apply(lambda x: '✅ Да' if x == 1 else '❌ Нет')

            st.dataframe(
                display_df.rename(columns={
                    'full_name': 'ФИО',
                    'course': 'Курс',
                    'specialization': 'Специальность',
                    'gpa': 'GPA',
                    'email': 'Email',
                    'contact_number': 'Телефон',
                    'programming_languages': 'Навыки',
                    'graduation_year': 'Год выпуска',
                    'work_experience': 'Опыт работы',
                    'is_active': 'В поиске работы'
                }),
                use_container_width=True,
                height=400
            )

            st.markdown('</div>', unsafe_allow_html=True)

            # Экспорт данных
            st.subheader("📤 Экспорт данных")
            col_exp1, col_exp2 = st.columns(2)

            with col_exp1:
                if st.button("📥 Экспорт в CSV", key="export_csv"):
                    csv = display_df.to_csv(index=False)
                    st.download_button(
                        label="Скачать CSV",
                        data=csv,
                        file_name=f"students_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                        mime="text/csv"
                    )

            with col_exp2:
                if st.button("📊 Создать отчет", key="create_report"):
                    report = f"""
                    ОТЧЕТ ПО СТУДЕНТАМ КЭУ
                    Дата: {datetime.now().strftime('%d.%m.%Y %H:%M')}

                    Всего студентов: {len(students)}
                    Активно ищут работу: {len(students[students['is_active'] == 1])}
                    Средний GPA: {students['gpa'].mean():.2f}

                    Распределение по курсам:
                    """

                    for course in COURSE_OPTIONS:
                        count = len(students[students['course'] == course])
                        report += f"- Курс {course}: {count} студентов\n"

                    st.text_area("Отчет", report, height=200)

        else:
            st.info("Пока нет зарегистрированных студентов")

    except Exception as e:
        st.error(f"Ошибка: {str(e)}")


def admin_vacancies():
    st.header("💼 Управление вакансиями")
    back_button()

    db = st.session_state.db_manager

    try:
        vacancies = db.get_all_vacancies()

        if not vacancies.empty:
            # Кнопка добавления
            if st.button("➕ Добавить вакансию", key="admin_add_vacancy_btn"):
                st.session_state.page = 'add_vacancy'
                st.rerun()

            # Таблица вакансий
            display_df = vacancies[['company_name', 'position', 'specialization', 'salary_range',
                                    'application_deadline', 'contact_email']].copy()

            st.dataframe(
                display_df.rename(columns={
                    'company_name': 'Компания',
                    'position': 'Должность',
                    'specialization': 'Специальность',
                    'salary_range': 'Зарплата',
                    'application_deadline': 'Дедлайн',
                    'contact_email': 'Email компании'
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Пока нет активных вакансий")
            if st.button("➕ Добавить первую вакансию", key="admin_add_first_vacancy"):
                st.session_state.page = 'add_vacancy'
                st.rerun()

    except Exception as e:
        st.error(f"Ошибка: {str(e)}")


def admin_add_vacancy():
    st.header("➕ Новая вакансия")
    back_button()

    with st.form("add_vacancy_form", clear_on_submit=True):
        st.markdown('<div class="content-card">', unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            company_name = st.text_input("Название компании *", key="vac_company")
            position = st.text_input("Должность *", key="vac_position")
            specialization = st.selectbox("Специальность", SPECIALIZATION_OPTIONS, key="vac_specialization")
            required_course = st.selectbox("Требуемый курс", COURSE_OPTIONS, key="vac_course")

        with col2:
            salary_range = st.text_input("Зарплатная вилка", placeholder="150 000 - 200 000 KZT", key="vac_salary")
            contact_email = st.text_input("Email для откликов *", placeholder="hr@company.kz", key="vac_email")
            application_deadline = st.date_input("Дедлайн подачи", key="vac_deadline")

        description = st.text_area("Описание вакансии *", height=120, key="vac_description")
        requirements = st.text_area("Требования *", height=120, key="vac_requirements")

        st.markdown('</div>', unsafe_allow_html=True)

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("📤 Опубликовать", use_container_width=True, key="vac_submit")
        with col_btn2:
            if st.form_submit_button("❌ Отмена", use_container_width=True, key="vac_cancel"):
                st.session_state.page = 'vacancies'
                st.rerun()

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
                    st.session_state.page = 'vacancies'
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Ошибка: {str(e)}")
            else:
                st.warning("⚠️ Заполните все обязательные поля")


def admin_applications():
    st.header("📨 Управление откликами")
    back_button()

    db = st.session_state.db_manager

    try:
        applications = db.get_all_applications()

        if not applications.empty:
            # Фильтры
            col_filter1, col_filter2 = st.columns(2)
            with col_filter1:
                status_filter = st.selectbox("Статус", ["Все", "pending", "accepted", "rejected"],
                                             key="admin_status_filter")
            with col_filter2:
                search_app = st.text_input("Поиск", placeholder="Студент, вакансия...", key="admin_app_search")

            # Применяем фильтры
            filtered_apps = applications.copy()
            if status_filter != "Все":
                filtered_apps = filtered_apps[filtered_apps['status'] == status_filter]
            if search_app:
                filtered_apps = filtered_apps[
                    filtered_apps['full_name'].str.contains(search_app, case=False, na=False) |
                    filtered_apps['position'].str.contains(search_app, case=False, na=False)
                    ]

            # Отображение откликов
            for i, app in filtered_apps.iterrows():
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
                            <h4 style="margin: 0; color: var(--peach-dark);">{app['position']}</h4>
                            <p style="margin: 5px 0; color: var(--peach-primary);">{app['company_name']}</p>
                            <p style="margin: 0;"><strong>Студент:</strong> {app['full_name']}</p>
                            <p style="margin: 0;"><strong>Email:</strong> {app['student_email']}</p>
                            <p style="margin: 0;"><strong>Телефон:</strong> {app['contact_number']}</p>
                            <p style="margin: 5px 0;"><strong>Дата:</strong> {app['application_date'][:10]}</p>
                            <p style="margin: 0;"><strong>Зарплата:</strong> {app['salary_range']}</p>
                        </div>
                        <span class="status-badge {status_class}">{status_text}</span>
                    </div>
                    {f'<p style="margin-top: 10px;"><strong>Сопроводительное письмо:</strong><br>{app["cover_letter"]}</p>' if app['cover_letter'] else ''}
                </div>
                """, unsafe_allow_html=True)

                # Кнопки управления статусом
                col_status1, col_status2, col_status3 = st.columns(3)
                with col_status1:
                    if app['status'] != 'accepted':
                        if st.button("✅ Принять", key=f"accept_{app['id']}"):
                            db.update_application_status(app['id'], 'accepted')
                            st.success("Статус изменен на 'Принято'")
                            st.rerun()
                with col_status2:
                    if app['status'] != 'rejected':
                        if st.button("❌ Отклонить", key=f"reject_{app['id']}"):
                            db.update_application_status(app['id'], 'rejected')
                            st.success("Статус изменен на 'Отклонено'")
                            st.rerun()
                with col_status3:
                    if st.button("📋 Подробнее", key=f"app_details_{app['id']}"):
                        with st.expander("Детали отклика"):
                            st.write(f"**ID отклика:** {app['id']}")
                            if app['cover_letter']:
                                st.write(f"**Сопроводительное письмо:**\n{app['cover_letter']}")
                            st.write(f"**Дата отправки:** {app['application_date']}")
                st.markdown("---")
        else:
            st.info("📭 Пока нет откликов на вакансии")

    except Exception as e:
        st.error(f"Ошибка: {str(e)}")


def admin_analytics():
    st.header("📊 Расширенная аналитика")
    back_button()

    db = st.session_state.db_manager

    try:
        students = db.get_all_students()
        vacancies = db.get_all_vacancies()
        applications = db.get_all_applications()

        # Основные метрики
        st.subheader("📈 Ключевые показатели")

        stats = db.get_statistics()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card("Всего студентов", stats['total_students'], "👨‍🎓")
        with col2:
            metric_card("Вакансий", stats['active_vacancies'], "💼")
        with col3:
            metric_card("Откликов", stats['total_applications'], "📨")
        with col4:
            metric_card("Конверсия",
                        f"{(stats['accepted_applications'] / stats['total_applications'] * 100):.1f}%" if stats[
                                                                                                              'total_applications'] > 0 else "0%",
                        "📊")

        # Визуализация
        st.subheader("📊 Визуализация данных")

        # Распределение студентов по курсам
        if not students.empty:
            col_chart1, col_chart2 = st.columns(2)

            with col_chart1:
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.write("**Распределение студентов по курсам**")

                course_counts = students['course'].value_counts().sort_index()
                fig1 = px.pie(
                    values=course_counts.values,
                    names=course_counts.index,
                    title="Курсы",
                    color_discrete_sequence=px.colors.sequential.RdBu
                )
                fig1.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig1, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_chart2:
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.write("**Распределение по специальностям**")

                spec_counts = students['specialization'].value_counts()
                fig2 = px.bar(
                    x=spec_counts.values,
                    y=spec_counts.index,
                    orientation='h',
                    title="Специальности",
                    color=spec_counts.values,
                    color_continuous_scale='Peach'
                )
                fig2.update_layout(xaxis_title="Количество", yaxis_title="Специальность")
                st.plotly_chart(fig2, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # Анализ откликов
        if not applications.empty:
            st.subheader("📨 Анализ откликов")

            col_app1, col_app2 = st.columns(2)

            with col_app1:
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.write("**Статусы откликов**")

                status_counts = applications['status'].value_counts()
                fig3 = px.pie(
                    values=status_counts.values,
                    names=status_counts.index.map({
                        'pending': 'На рассмотрении',
                        'accepted': 'Принято',
                        'rejected': 'Отклонено'
                    }),
                    title="Статусы откликов",
                    color_discrete_sequence=['#FF9800', '#4CAF50', '#F44336']
                )
                st.plotly_chart(fig3, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col_app2:
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.write("**Динамика откликов**")

                applications['application_date'] = pd.to_datetime(applications['application_date'])
                daily_counts = applications.groupby(applications['application_date'].dt.date).size()

                fig4 = px.line(
                    x=daily_counts.index,
                    y=daily_counts.values,
                    title="Количество откликов по дням",
                    markers=True
                )
                fig4.update_layout(xaxis_title="Дата", yaxis_title="Количество откликов")
                st.plotly_chart(fig4, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # Успеваемость
        if not students.empty and 'gpa' in students.columns:
            st.subheader("⭐ Анализ успеваемости")

            gpa_stats = students['gpa'].describe()

            col_gpa1, col_gpa2 = st.columns(2)

            with col_gpa1:
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.write("**Статистика GPA**")

                stats_data = {
                    'Метрика': ['Среднее', 'Медиана', 'Минимум', 'Максимум', 'Стандартное отклонение'],
                    'Значение': [
                        f"{gpa_stats['mean']:.2f}",
                        f"{gpa_stats['50%']:.2f}",
                        f"{gpa_stats['min']:.2f}",
                        f"{gpa_stats['max']:.2f}",
                        f"{gpa_stats['std']:.2f}"
                    ]
                }

                st.table(pd.DataFrame(stats_data))
                st.markdown('</div>', unsafe_allow_html=True)

            with col_gpa2:
                st.markdown('<div class="content-card">', unsafe_allow_html=True)
                st.write("**Распределение GPA**")

                fig5 = px.histogram(
                    students,
                    x='gpa',
                    nbins=20,
                    title="Распределение среднего балла",
                    color_discrete_sequence=['#FFA07A']
                )
                fig5.update_layout(xaxis_title="GPA", yaxis_title="Количество студентов")
                st.plotly_chart(fig5, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

        # Генерация комплексного отчета
        st.subheader("📋 Генерация комплексного отчета")

        if st.button("📊 Сгенерировать полный отчет", key="generate_full_report"):
            report = f"""
            КОМПЛЕКСНЫЙ ОТЧЕТ КАРЬЕРНОГО ЦЕНТРА КЭУ
            =========================================
            Дата генерации: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}

            СТУДЕНТЫ:
            - Всего студентов: {len(students)}
            - Активно ищут работу: {len(students[students['is_active'] == 1])}
            - Средний GPA: {students['gpa'].mean():.2f if not students.empty and 'gpa' in students.columns else 'Нет данных'}

            ВАКАНСИИ:
            - Активных вакансий: {len(vacancies)}
            - Популярная специальность: {vacancies['specialization'].mode()[0] if not vacancies.empty else 'Нет данных'}

            ОТКЛИКИ:
            - Всего откликов: {len(applications) if not applications.empty else 0}
            - Принято: {len(applications[applications['status'] == 'accepted']) if not applications.empty else 0}
            - На рассмотрении: {len(applications[applications['status'] == 'pending']) if not applications.empty else 0}
            - Отклонено: {len(applications[applications['status'] == 'rejected']) if not applications.empty else 0}
            - Конверсия: {(len(applications[applications['status'] == 'accepted']) / len(applications) * 100) if not applications.empty and len(applications) > 0 else 0:.1f}%

            РАСПРЕДЕЛЕНИЕ ПО КУРСАМ:
            """

            if not students.empty:
                for course in COURSE_OPTIONS:
                    count = len(students[students['course'] == course])
                    percentage = (count / len(students)) * 100 if len(students) > 0 else 0
                    report += f"- Курс {course}: {count} студентов ({percentage:.1f}%)\n"

            report += "\nРАСПРЕДЕЛЕНИЕ ПО СПЕЦИАЛЬНОСТЯМ:\n"
            if not students.empty:
                for spec in SPECIALIZATION_OPTIONS:
                    count = len(students[students['specialization'] == spec])
                    if count > 0:
                        percentage = (count / len(students)) * 100
                        report += f"- {spec}: {count} студентов ({percentage:.1f}%)\n"

            # Добавляем статистику GPA
            if not students.empty and 'gpa' in students.columns:
                report += f"\nУСПЕВАЕМОСТЬ:\n"
                report += f"- Средний GPA: {students['gpa'].mean():.2f}\n"
                report += f"- Максимальный GPA: {students['gpa'].max():.2f}\n"
                report += f"- Минимальный GPA: {students['gpa'].min():.2f}\n"
                report += f"- Стандартное отклонение: {students['gpa'].std():.2f}\n"

            # Рекомендации
            report += f"\nРЕКОМЕНДАЦИИ:\n"
            if not vacancies.empty:
                most_demanded = vacancies['specialization'].mode()[0]
                report += f"- Наиболее востребованная специальность: {most_demanded}\n"

            if not applications.empty:
                conversion_rate = (len(applications[applications['status'] == 'accepted']) / len(applications)) * 100
                if conversion_rate < 30:
                    report += "- Рекомендуется улучшить качество подготовки студентов к собеседованиям\n"
                report += f"- Уровень конверсии откликов: {conversion_rate:.1f}%\n"

            st.success("✅ Комплексный отчет сгенерирован!")

            # Отображаем и предлагаем скачать отчет
            st.text_area("Содержимое отчета", report, height=400)

            st.download_button(
                label="📥 Скачать полный отчет",
                data=report,
                file_name=f"keu_comprehensive_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                key="download_full_report"
            )

    except Exception as e:
        st.error(f"Ошибка при генерации аналитики: {str(e)}")


# ========== ОСНОВНАЯ ФУНКЦИЯ ==========
def main():
    init_session_state()
    apply_peach_theme()

    # Если пользователь не авторизован - показываем страницу входа
    if 'user' not in st.session_state:
        login_page()
    else:
        # Создаем сайдбар
        create_sidebar()

        user_role = st.session_state.user['role']

        # Определяем обработчики страниц в зависимости от роли
        if user_role == 'student':
            page_handlers = {
                'dashboard': student_dashboard,
                'profile': student_profile,
                'vacancies': student_vacancies,
                'apply_vacancy': student_apply_vacancy,
                'my_applications': student_my_applications,
                'stats': student_stats,
            }
        else:  # admin
            page_handlers = {
                'dashboard': admin_dashboard,
                'students': admin_students,
                'students_detailed': admin_students_detailed,
                'vacancies': admin_vacancies,
                'add_vacancy': admin_add_vacancy,
                'applications': admin_applications,
                'analytics': admin_analytics,
            }

        # Получаем текущую страницу (по умолчанию dashboard)
        current_page = st.session_state.get('page', 'dashboard')

        # Вызываем обработчик страницы
        handler = page_handlers.get(current_page, student_dashboard if user_role == 'student' else admin_dashboard)
        handler()


if __name__ == "__main__":
    main()


