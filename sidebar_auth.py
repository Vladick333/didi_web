import streamlit as st
from auth import get_current_user, ROLES, logout


def create_auth_sidebar():
    """Создание сайдбара с навигацией в зависимости от роли"""
    with st.sidebar:
        user = get_current_user()

        if user:
            # --- ШАПКА ПРОФИЛЯ (Имя и Роль) ---
            st.markdown(f"""
            <div style="text-align: center; padding: 20px 0; border-bottom: 2px solid rgba(157, 78, 221, 0.5); margin-bottom: 25px;">
                <div style="font-size: 3rem; margin-bottom: 10px;">
                    {'👑' if user['role'] == 'admin' else '💼' if user['role'] == 'employer' else '🎓'}
                </div>
                <h2 style="color: var(--neon-purple); margin: 0; font-size: 1.2rem;">{user['full_name']}</h2>
                <p style="color: var(--text-dim); margin: 5px 0 0 0; font-size: 0.9rem;">
                    {ROLES.get(user['role'], user['role'])}
                </p>
            </div>
            """, unsafe_allow_html=True)

            # --- ЛОГИКА КНОПОК ПО РОЛЯМ ---

            # 1. РОЛЬ: АДМИН (Есть ВСЕ кнопки)
            if user['role'] == 'admin':
                st.markdown("### 🛠 Меню Админа")
                if st.button("🏠 Панель управления", use_container_width=True):
                    st.session_state.page = 'dashboard'
                    st.rerun()
                if st.button("👨‍🎓 Студенты", use_container_width=True):
                    st.session_state.page = 'students'
                    st.rerun()
                if st.button("📝 Подать заявку (Тест)", use_container_width=True):
                    st.session_state.page = 'student_form'
                    st.rerun()
                if st.button("💼 Вакансии", use_container_width=True):
                    st.session_state.page = 'vacancies'
                    st.rerun()
                if st.button("📨 Отклики", use_container_width=True):
                    st.session_state.page = 'applications'
                    st.rerun()
                if st.button("📊 Трудоустройство", use_container_width=True):
                    st.session_state.page = 'employment_reports'
                    st.rerun()
                if st.button("🔔 Уведомления", use_container_width=True):
                    st.session_state.page = 'notifications'
                    st.rerun()
                if st.button("📈 Аналитика", use_container_width=True):
                    st.session_state.page = 'analytics'
                    st.rerun()

            # 2. РОЛЬ: СТУДЕНТ (Подать заявку, Вакансии, Уведомления)
            elif user['role'] == 'student':
                st.markdown("### 🎓 Меню Студента")
                # Кнопка "Главная" нужна, чтобы не потеряться
                if st.button("🏠 Главная", use_container_width=True):
                    st.session_state.page = 'dashboard'
                    st.rerun()

                # Твои требования:
                if st.button("📝 Подать заявку / Профиль", use_container_width=True):
                    # Чтобы открыть форму редактирования себя
                    st.session_state.edit_mode = True
                    st.session_state.current_student_id = user.get('id')  # Если ID студента совпадает с ID юзера
                    st.session_state.page = 'student_form'
                    st.rerun()

                if st.button("💼 Вакансии", use_container_width=True):
                    st.session_state.page = 'vacancies'
                    st.rerun()

                if st.button("🔔 Уведомления", use_container_width=True):
                    st.session_state.page = 'notifications'
                    st.rerun()

            # 3. РОЛЬ: РАБОТОДАТЕЛЬ (Отклики, Трудоустройство, Уведомления)
            elif user['role'] == 'employer':
                st.markdown("### 💼 Меню HR")
                if st.button("🏠 Главная", use_container_width=True):
                    st.session_state.page = 'dashboard'
                    st.rerun()
                    
                if st.button("👨‍🎓 База студентов", use_container_width=True):
                    st.session_state.page = 'students'
                    st.rerun()
                # ================================
                # Твои требования:
                if st.button("📨 Отклики на вакансии", use_container_width=True):
                    st.session_state.page = 'applications'
                    st.rerun()

                if st.button("📊 Трудоустройство", use_container_width=True):
                    st.session_state.page = 'employment_reports'
                    st.rerun()

                if st.button("🔔 Уведомления", use_container_width=True):
                    st.session_state.page = 'notifications'
                    st.rerun()

            # --- КНОПКА ВЫХОДА (У всех) ---
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚪 Выйти", use_container_width=True, type="secondary"):
                logout()

        else:
            # Если вдруг меню загрузилось без входа (на всякий случай)

            st.error("Требуется авторизация")

