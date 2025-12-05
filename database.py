import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import json

# ========== БАЗА ДАННЫХ SQLite ==========
DATABASE_NAME = 'recruit_system.db'


def get_db_connection():
    """Создает соединение с базой данных SQLite."""
    try:
        conn = sqlite3.connect(DATABASE_NAME, check_same_thread=False)
        return conn
    except sqlite3.Error as e:
        st.error(f"Ошибка подключения к БД: {e}")
        return None


def init_database():
    """Инициализация базы данных с вашей структурой"""
    conn = get_db_connection()
    if conn is None:
        return

    cursor = conn.cursor()

    # Основная таблица студентов (ваша структура)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            course INTEGER NOT NULL,
            specialization TEXT,
            programming_languages TEXT,
            work_experience TEXT,
            portfolio_link TEXT,
            contact_number TEXT,
            document_id TEXT,
            is_active BOOLEAN,
            email TEXT,
            gpa REAL,
            university TEXT DEFAULT 'Международный Университет Информационных Технологий',
            graduation_year INTEGER,
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

    # Проверяем, есть ли данные в таблице students
    cursor.execute("SELECT COUNT(*) FROM students")
    if cursor.fetchone()[0] == 0:
        # Добавляем тестовых студентов
        test_students = [
            ('Алиев Аскар Бауыржанович', 4, 'Информационные Системы', 'Python, SQL, Java',
             'Разработка веб-приложений на Django, участие в хакатонах',
             'https://github.com/askarali', '+7 701 123 4567', '123456789012',
             1, 'askar@email.com', 3.8, 'Международный Университет Информационных Технологий', 2024),
            ('Смирнова Анна Ивановна', 5, 'Компьютерные Науки', 'C++, Python, JavaScript',
             'Стажировка в ТОО "КазТех", разработка мобильного приложения',
             'https://github.com/annasm', '+7 777 987 6543', '987654321098',
             1, 'anna@email.com', 3.9, 'Казахстанско-Британский Технический Университет', 2024),
        ]

        cursor.executemany('''
            INSERT INTO students 
            (full_name, course, specialization, programming_languages, work_experience, 
             portfolio_link, contact_number, document_id, is_active, email, gpa, university, graduation_year)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', test_students)

    # Проверяем, есть ли данные в таблице vacancies
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
        ]

        cursor.executemany('''
            INSERT INTO vacancies 
            (company_name, position, specialization, required_course, salary_range,
             description, requirements, contact_email, application_deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', test_vacancies)

    conn.commit()
    conn.close()


# ========== CRUD ОПЕРАЦИИ ДЛЯ SQLite ==========
class DatabaseManager:
    def __init__(self):
        pass

    def execute_query(self, query, params=()):
        """Выполняет SQL запрос с созданием нового соединения"""
        conn = get_db_connection()
        if conn is None:
            return None
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor
        except sqlite3.Error as e:
            st.error(f"Ошибка выполнения запроса: {e}")
            return None
        finally:
            if conn:
                conn.close()

    def execute_read_query(self, query, params=()):
        """Выполняет SQL запрос на чтение"""
        conn = get_db_connection()
        if conn is None:
            return pd.DataFrame()
        try:
            return pd.read_sql_query(query, conn, params=params)
        except Exception as e:
            st.error(f"Ошибка выполнения запроса на чтение: {e}")
            return pd.DataFrame()
        finally:
            if conn:
                conn.close()

    # Студенты
    def insert_student(self, data):
        query = '''
            INSERT INTO students 
            (full_name, course, specialization, programming_languages, work_experience, 
             portfolio_link, contact_number, document_id, email, gpa, graduation_year, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        result = self.execute_query(query, data)
        return result is not None

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
        result = self.execute_query(query, (*data, student_id))
        return result is not None

    def delete_student(self, student_id):
        query = "DELETE FROM students WHERE id = ?"
        result = self.execute_query(query, (student_id,))
        return result is not None

    # Вакансии
    def insert_vacancy(self, data):
        query = '''
            INSERT INTO vacancies 
            (company_name, position, specialization, required_course, salary_range,
             description, requirements, contact_email, application_deadline)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        result = self.execute_query(query, data)
        return result is not None

    def get_all_vacancies(self):
        query = "SELECT * FROM vacancies WHERE is_active = 1 ORDER BY posted_date DESC"
        return self.execute_read_query(query)

    # Отклики на вакансии
    def apply_for_vacancy(self, student_id, vacancy_id, cover_letter=""):
        query = '''
            INSERT INTO applications (student_id, vacancy_id, cover_letter)
            VALUES (?, ?, ?)
        '''
        result = self.execute_query(query, (student_id, vacancy_id, cover_letter))
        return result is not None

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
        result = self.execute_query(query, (status, application_id))
        return result is not None

    # Уведомления
    def add_notification(self, user_id, title, message, notification_type='info'):
        query = '''
            INSERT INTO notifications (user_id, title, message, notification_type)
            VALUES (?, ?, ?, ?)
        '''
        result = self.execute_query(query, (user_id, title, message, notification_type))
        return result is not None

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
        result = self.execute_query(query, (notification_id,))
        return result is not None

    # Отчеты о трудоустройстве
    def add_employment_report(self, student_id, company_name, position, employment_date, salary):
        query = '''
            INSERT INTO employment_reports (student_id, company_name, position, employment_date, salary)
            VALUES (?, ?, ?, ?, ?)
        '''
        result = self.execute_query(query, (student_id, company_name, position, employment_date, salary))
        return result is not None

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


# ========== ИНИЦИАЛИЗАЦИЯ ==========
def init_session_state():
    """Инициализация состояния сессии"""
    defaults = {
        'page': 'dashboard',
        'edit_mode': False,
        'current_student_id': None,
        'current_vacancy_id': None,
        'db_manager': DatabaseManager(),
        'sidebar_collapsed': False  # Добавляем состояние для сайдбара
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Инициализируем базу данных при первом запуске
    init_database()


# ========== СТИЛИ ==========
# В функции apply_custom_styles() ИЗМЕНИТЕ CSS:

def apply_custom_styles():
    st.set_page_config(
        page_title="🎓 Graduate Recruitment System",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"  # Можно изменить на "collapsed"
    )

    st.markdown("""
    <style>
    /* ОГРАНИЧИВАЕМ ШИРИНУ ОСНОВНОГО КОНТЕНТА */
    .main .block-container {
        max-width: 1200px !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
        padding-top: 2rem !important;
    }

    /* === УБИРАЕМ ПРИНУДИТЕЛЬНОЕ ОТОБРАЖЕНИЕ === */
    /* УДАЛИТЬ ЭТОТ БЛОК ВООБЩЕ ИЛИ ЗАКОММЕНТИРОВАТЬ */
    /* 
    section[data-testid="stSidebar"] {
        transform: translateX(0) !important;
        visibility: visible !important;
        width: 280px !important;
    }
    */

    /* Вместо этого задаем нормальную ширину */
    section[data-testid="stSidebar"] {
        min-width: 280px;
        max-width: 280px;
    }

    /* Кнопка сворачивания в сайдбаре */
    .sidebar-toggle-btn {
        background: rgba(157, 78, 221, 0.1) !important;
        border: 1px solid rgba(157, 78, 221, 0.3) !important;
        border-radius: 6px !important;
        padding: 8px !important;
        font-size: 14px !important;
        margin-bottom: 10px !important;
    }

    /* Уменьшаем ширину таблиц */
    .stDataFrame {
        max-width: 1000px !important;
    }

    /* Остальные стили... */
    </style>
    """, unsafe_allow_html=True)

# ========== ОСНОВНЫЕ СТРАНИЦЫ ==========
def dashboard_page():
    """Главная панель управления"""
    # Заголовок Dashboard
    st.markdown("""
    <div style="background: rgba(20, 20, 43, 0.8);
                backdrop-filter: blur(10px);
                border: 1px solid var(--neon-purple);
                border-radius: 20px;
                padding: 2rem;
                margin-bottom: 2rem;
                text-align: center;
                box-shadow: 0 0 30px rgba(157, 78, 221, 0.3),
                            inset 0 0 20px rgba(157, 78, 221, 0.1);
                position: relative;
                overflow: hidden;">
        <div style="position: absolute; top: 0; left: 0; right: 0; height: 2px;
                    background: linear-gradient(90deg, 
                        transparent, 
                        var(--neon-pink), 
                        var(--neon-purple), 
                        var(--neon-blue), 
                        transparent);"></div>
        <h1 style="background: linear-gradient(90deg, #9d4edd, #ff00ff, #00e5ff);
                   -webkit-background-clip: text;
                   -webkit-text-fill-color: transparent;
                   background-clip: text;
                   font-size: 3rem;
                   margin: 0;
                   text-shadow: 0 0 20px rgba(157, 78, 221, 0.5);">
            🎓 GRADUATE RECRUITMENT SYSTEM
        </h1>
        <p style="color: var(--text-dim); margin-top: 10px; font-size: 1.1rem;">
            Информационная система для трудоустройства выпускников университета
        </p>
    </div>
    """, unsafe_allow_html=True)

    try:
        stats = st.session_state.db_manager.get_statistics()

        # Основные метрики
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.metric("Всего студентов", stats['total_students'])
        with col2:
            st.metric("Активных", stats['active_students'])
        with col3:
            st.metric("Вакансий", stats['active_vacancies'])
        with col4:
            st.metric("Откликов", stats['total_applications'])
        with col5:
            st.metric("Трудоустроено", stats['employed_students'])
        with col6:
            st.metric("Уведомления", stats['unread_notifications'])

    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")


def student_management_page():
    """Управление студентами"""
    st.header("👨‍🎓 Управление студентами")

    # Поиск
    search_query = st.text_input("🔍 Поиск по имени", placeholder="Введите ФИО...")

    try:
        # Получение данных
        students_df = st.session_state.db_manager.get_all_students()

        if not students_df.empty:
            if search_query:
                students_df = students_df[students_df['full_name'].str.contains(search_query, case=False, na=False)]

            # Таблица студентов
            st.dataframe(
                students_df[
                    ['id', 'full_name', 'course', 'specialization', 'programming_languages', 'is_active']].rename(
                    columns={
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
        else:
            st.info("👤 Студенты не найдены")
    except Exception as e:
        st.error(f"Ошибка при загрузке данных: {e}")


def main():
    init_session_state()
    apply_custom_styles()

    # ========== САЙДБАР С КНОПКОЙ СВОРАЧИВАНИЯ ==========
    with st.sidebar:
        # Кнопка сворачивания/разворачивания сайдбара
        col_toggle, col_logo = st.columns([1, 4])
        with col_toggle:
            if st.button("☰", key="sidebar_toggle", help="Свернуть/развернуть меню"):
                # Меняем состояние через JS или релоад
                st.rerun()



        with col_logo:
            if not st.session_state.sidebar_collapsed:
                st.markdown("""
                <div style="text-align: center;">
                    <div style="font-size: 2rem; color: #9d4edd; margin-bottom: 5px;">⚡</div>
                    <div style="font-size: 1.2rem; font-weight: bold; color: white;">GRS</div>
                    <div style="font-size: 0.7rem; color: #888;">Graduate Recruitment System</div>
                </div>
                """, unsafe_allow_html=True)

        st.markdown("---")

        # Если сайдбар развернут - показываем полное меню
        if not st.session_state.sidebar_collapsed:
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
                # Определяем активную кнопку
                button_type = "primary" if st.session_state.page == page_key else "secondary"

                if st.button(page_name,
                             use_container_width=True,
                             type=button_type,
                             key=f"nav_{page_key}"):
                    st.session_state.page = page_key
                    st.rerun()

            # Разделитель
            st.markdown("---")

            # Быстрые действия
            st.markdown("""
            <div style="padding: 15px; background: rgba(157, 78, 221, 0.1); 
                        border-radius: 12px; margin: 20px 0; 
                        border: 1px solid rgba(157, 78, 221, 0.3);">
                <h4 style="color: #9d4edd; margin: 0 0 15px 0; 
                        font-size: 1rem; text-align: center;">
                    ⚡ Быстрые действия
                </h4>
            </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("➕ Студент",
                             use_container_width=True,
                             type="secondary",
                             key="add_student_btn"):
                    st.session_state.page = 'student_form'
                    st.session_state.edit_mode = False
                    st.rerun()

            with col2:
                if st.button("➕ Вакансия",
                             use_container_width=True,
                             type="secondary",
                             key="add_vacancy_btn"):
                    st.session_state.page = 'vacancy_form'
                    st.rerun()

            # Разделитель
            st.markdown("---")

            # Статистика в сайдбаре
            try:
                stats = st.session_state.db_manager.get_statistics()
                st.markdown(f"""
                <div style="background: rgba(20, 20, 43, 0.8); 
                            border: 1px solid rgba(157, 78, 221, 0.3); 
                            border-radius: 15px; padding: 20px; margin-top: 10px;">
                    <h4 style="color: #9d4edd; margin: 0 0 15px 0; 
                            text-align: center; font-size: 1.1rem;">
                        📊 Статистика
                    </h4>
                    <div style="display: grid; grid-template-columns: 1fr; gap: 8px;">
                        <div style="display: flex; justify-content: space-between; 
                                    align-items: center; padding: 5px 0;">
                            <span style="color: #888; font-size: 0.9rem;">
                                👨‍🎓 Студентов:
                            </span>
                            <span style="color: #9d4edd; font-weight: 700; 
                                        font-size: 1.1rem;">
                                {stats['total_students']}
                            </span>
                        </div>
                        <div style="display: flex; justify-content: space-between; 
                                    align-items: center; padding: 5px 0;">
                            <span style="color: #888; font-size: 0.9rem;">
                                💼 Вакансий:
                            </span>
                            <span style="color: #00e5ff; font-weight: 700; 
                                        font-size: 1.1rem;">
                                {stats['active_vacancies']}
                            </span>
                        </div>
                        <div style="display: flex; justify-content: space-between; 
                                    align-items: center; padding: 5px 0;">
                            <span style="color: #888; font-size: 0.9rem;">
                                📨 Откликов:
                            </span>
                            <span style="color: #ff00ff; font-weight: 700; 
                                        font-size: 1.1rem;">
                                {stats['total_applications']}
                            </span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            except:
                pass

            # Информация о системе
            st.markdown("""
            <div style="text-align: center; color: #888; font-size: 0.75rem; 
                        padding: 15px 0; margin-top: 20px; 
                        border-top: 1px solid rgba(157, 78, 221, 0.3); opacity: 0.7;">
                <div style="margin-bottom: 5px;">v3.0 | CyberPunk Edition</div>
                <div>© 2025 Graduate Recruitment System</div>
            </div>
            """, unsafe_allow_html=True)

        else:
            # Если сайдбар свернут - показываем только иконки
            st.markdown("<br>", unsafe_allow_html=True)

            # Минималистичное меню
            menu_icons = {
                "dashboard": "🏠",
                "students": "👨‍🎓",
                "vacancies": "💼",
                "applications": "📨",
                "employment_reports": "📊",
                "notifications": "🔔",
                "analytics": "📈",
            }

            for page_key, icon in menu_icons.items():
                if st.button(
                        icon,
                        help=get_page_name(page_key),
                        key=f"nav_icon_{page_key}",
                        use_container_width=True
                ):
                    st.session_state.page = page_key
                    st.rerun()

            st.markdown("<br><br>", unsafe_allow_html=True)

            # Быстрые действия в свернутом виде
            col1, col2 = st.columns(2)
            with col1:
                if st.button("👤", help="Добавить студента", use_container_width=True):
                    st.session_state.page = 'student_form'
                    st.session_state.edit_mode = False
                    st.rerun()

            with col2:
                if st.button("💼", help="Добавить вакансию", use_container_width=True):
                    st.session_state.page = 'vacancy_form'
                    st.rerun()

    # ========== ОСНОВНОЙ КОНТЕНТ ==========

    # Если сайдбар свернут, добавляем маленькую кнопку для разворачивания вверху основного контента
    if st.session_state.sidebar_collapsed:
        col_top_left, _ = st.columns([1, 20])
        with col_top_left:
            if st.button("☰", key="expand_sidebar_top"):
                st.session_state.sidebar_collapsed = False
                st.rerun()

    # Маршрутизация страниц
    page_handlers = {
        'dashboard': dashboard_page,
        'students': student_management_page,
        'vacancies': lambda: st.header("💼 Вакансии (страница в разработке)"),
        'applications': lambda: st.header("📨 Отклики (страница в разработке)"),
        'employment_reports': lambda: st.header("📊 Трудоустройство (страница в разработке)"),
        'notifications': lambda: st.header("🔔 Уведомления (страница в разработке)"),
        'analytics': lambda: st.header("📈 Аналитика (страница в разработке)"),
        'student_form': lambda: st.header("📝 Форма студента (страница в разработке)"),
        'vacancy_form': lambda: st.header("📋 Форма вакансии (страница в разработке)"),
    }

    # Вызов обработчика текущей страницы
    handler = page_handlers.get(st.session_state.page, dashboard_page)
    handler()


def get_page_name(page_key):
    """Получить название страницы по ключу"""
    page_names = {
        'dashboard': 'Панель управления',
        'students': 'Студенты',
        'vacancies': 'Вакансии',
        'applications': 'Отклики',
        'employment_reports': 'Трудоустройство',
        'notifications': 'Уведомления',
        'analytics': 'Аналитика',
    }
    return page_names.get(page_key, page_key)


if __name__ == "__main__":
    main()