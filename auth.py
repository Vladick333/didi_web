import streamlit as st
import pandas as pd
import sqlite3
import hashlib


# ========== ФУНКЦИИ АВТОРИЗАЦИИ ==========
def get_db_connection():
    """Создает новое соединение с базой данных"""
    return sqlite3.connect('grad_recruitment.db', check_same_thread=False)


def hash_password(password):
    """Хеширование пароля"""
    return hashlib.sha256(password.encode()).hexdigest()


def init_auth_database():
    """Инициализация таблиц для авторизации"""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Таблица пользователей
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'employer', 'student')),
            email TEXT,
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active INTEGER DEFAULT 1
        )
    ''')

    # Добавляем тестовых пользователей если таблица пустая
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Администратор
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, email, full_name)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', hash_password('admin123'), 'admin', 'admin@system.kz', 'Администратор Системы'))

        # Тестовый студент
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, email, full_name)
            VALUES (?, ?, ?, ?, ?)
        ''', ('student', hash_password('student123'), 'student', 'student@email.com', 'Тестовый Студент'))

        # Тестовый работодатель
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, email, full_name)
            VALUES (?, ?, ?, ?, ?)
        ''', ('employer', hash_password('employer123'), 'employer', 'employer@company.kz', 'Тестовый Работодатель'))

    conn.commit()
    conn.close()
    return True


def authenticate_user(username, password):
    """Аутентификация пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, username, password_hash, role, full_name, email 
        FROM users 
        WHERE username = ? AND is_active = 1
    ''', (username,))

    user = cursor.fetchone()
    conn.close()

    if user and user[2] == hash_password(password):
        return {
            'id': user[0],
            'username': user[1],
            'role': user[3],
            'full_name': user[4],
            'email': user[5]
        }
    return None


def register_user(username, password, role, email, full_name):
    """Регистрация нового пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, role, email, full_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (username, hash_password(password), role, email, full_name))

        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        conn.close()
        return False


def get_current_user():
    """Получение информации о текущем пользователе"""
    if 'user' in st.session_state:
        return st.session_state.user
    return None


def logout():
    """Выход из системы"""
    if 'user' in st.session_state:
        del st.session_state.user
    st.session_state.page = 'login'
    st.rerun()


# Роли для отображения
ROLES = {
    'student': '🎓 Студент',
    'employer': '💼 Работодатель',
    'admin': '👑 Администратор'
}


# ========== КОМПОНЕНТЫ ИНТЕРФЕЙСА ==========
def login_page():
    """Страница входа в систему"""
    # Инициализация базы данных при первом запуске
    init_auth_database()

    st.markdown("""
    <style>
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        min-height: 80vh;
    }
    .login-card {
        background: rgba(20, 20, 43, 0.9);
        border: 1px solid var(--neon-purple);
        border-radius: 20px;
        padding: 2rem;
        width: 100%;
        max-width: 500px;
        backdrop-filter: blur(10px);
        box-shadow: 0 0 30px rgba(157, 78, 221, 0.3);
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="login-container">
        <div class="login-card">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: var(--neon-purple); margin-bottom: 10px; font-family: 'Orbitron', sans-serif;">🎓 GRS</h1>
                <p style="color: var(--text-dim);">Graduate Recruitment System</p>
            </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔐 Вход", "📝 Регистрация"])

    with tab1:
        with st.form(key="login_form"):
            username = st.text_input("👤 Логин", placeholder="Введите ваш логин")
            password = st.text_input("🔒 Пароль", type="password", placeholder="Введите пароль")
            submit_login = st.form_submit_button("Войти в систему", use_container_width=True)

            if submit_login:
                if username and password:
                    user = authenticate_user(username, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.page = 'dashboard'
                        st.success(f"✅ Добро пожаловать, {user['full_name']}!")
                        st.rerun()
                    else:
                        st.error("❌ Неверный логин или пароль")
                else:
                    st.warning("⚠️ Заполните все поля")

    with tab2:
        with st.form(key="register_form"):
            st.markdown("#### 📝 Регистрация нового пользователя")

            col1, col2 = st.columns(2)
            with col1:
                reg_username = st.text_input("Логин*", help="Уникальное имя пользователя")
                reg_password = st.text_input("Пароль*", type="password")
                confirm_password = st.text_input("Подтвердите пароль*", type="password")
            with col2:
                reg_full_name = st.text_input("ФИО*")
                reg_email = st.text_input("Email*")
                reg_role = st.selectbox("Роль*", options=list(ROLES.keys()),
                                        format_func=lambda x: ROLES[x])

            submit_register = st.form_submit_button("Зарегистрироваться", use_container_width=True)

            if submit_register:
                if all([reg_username, reg_password, confirm_password, reg_full_name, reg_email, reg_role]):
                    if reg_password != confirm_password:
                        st.error("❌ Пароли не совпадают")
                    else:
                        if register_user(reg_username, reg_password, reg_role, reg_email, reg_full_name):
                            st.success("✅ Регистрация успешна! Теперь вы можете войти в систему.")
                        else:
                            st.error("❌ Пользователь с таким логином уже существует")
                else:
                    st.warning("⚠️ Заполните все обязательные поля")

    st.markdown("""
        </div>
        <div style="margin-top: 30px; color: var(--text-dim); text-align: center; font-size: 0.9rem;">
            <p>Тестовые пользователи:</p>
            <div style="display: flex; gap: 20px; justify-content: center; margin-top: 10px; flex-wrap: wrap;">
                <div style="background: rgba(157, 78, 221, 0.1); padding: 10px; border-radius: 10px; min-width: 150px;">
                    <div>👑 Администратор</div>
                    <div>Логин: <code>admin</code></div>
                    <div>Пароль: <code>admin123</code></div>
                </div>
                <div style="background: rgba(0, 229, 255, 0.1); padding: 10px; border-radius: 10px; min-width: 150px;">
                    <div>🎓 Студент</div>
                    <div>Логин: <code>student</code></div>
                    <div>Пароль: <code>student123</code></div>
                </div>
                <div style="background: rgba(255, 170, 0, 0.1); padding: 10px; border-radius: 10px; min-width: 150px;">
                    <div>💼 Работодатель</div>
                    <div>Логин: <code>employer</code></div>
                    <div>Пароль: <code>employer123</code></div>
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def require_auth(required_role=None):
    """Декоратор для проверки авторизации и роли"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            user = get_current_user()

            if not user:
                st.session_state.page = 'login'
                st.rerun()
                return

            if required_role:
                # Если required_role - список
                if isinstance(required_role, list):
                    if user['role'] not in required_role:
                        st.error(
                            f"⛔ У вас нет доступа к этой странице. Требуется одна из ролей: {', '.join([ROLES[r] for r in required_role])}")
                        st.session_state.page = 'dashboard'
                        st.rerun()
                        return
                # Если required_role - строка
                elif user['role'] != required_role:
                    st.error(f"⛔ У вас нет доступа к этой странице. Требуется роль: {ROLES[required_role]}")
                    st.session_state.page = 'dashboard'
                    st.rerun()
                    return

            return func(*args, **kwargs)

        return wrapper

    return decorator


# ========== УПРОЩЕННАЯ СИСТЕМА ПРОВЕРКИ РОЛЕЙ ==========
def is_admin():
    """Проверка, является ли пользователь администратором"""
    user = get_current_user()
    return user and user['role'] == 'admin'


def is_employer():
    """Проверка, является ли пользователь работодателем"""
    user = get_current_user()
    return user and user['role'] == 'employer'


def is_student():
    """Проверка, является ли пользователь студентом"""
    user = get_current_user()
    return user and user['role'] == 'student'