import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.student_screen import student_screen
from src.screens.teacher_screen import teacher_screen

from src.components.dialog_auto_enroll import (
    auto_enroll_dialog
)


# =========================================================
# MAIN APPLICATION
# =========================================================
def main():
    st.set_page_config(
        page_title='SnapClass - Making Attendence faster using AI',
        page_icon= "https://i.ibb.co/YTYGn5qV/logo.png"
    )
    # -----------------------------------------------------
    # Initialize login type
    # -----------------------------------------------------
    if "login_type" not in st.session_state:

        st.session_state["login_type"] = None

    # =====================================================
    # SCREEN ROUTING
    # =====================================================
    match st.session_state["login_type"]:

        # Teacher screen
        case 'teacher':

            teacher_screen()

        # Student screen
        case 'student':

            student_screen()

        # Home screen
        case None:

            home_screen()

    # =====================================================
    # GET JOIN CODE FROM URL
    # Example:
    # http://localhost:8501/?join-code=CS101
    # =====================================================
    join_code = st.query_params.get('join-code')

    # -----------------------------------------------------
    # If join code exists
    # -----------------------------------------------------
    if join_code:

        # Force student login screen
        if st.session_state.login_type != 'student':

            st.session_state.login_type = 'student'

            st.rerun()

        # -------------------------------------------------
        # If student already logged in
        # -------------------------------------------------
        if (
            st.session_state.get('is_logged_in')
            and st.session_state.get('user_role') == 'student'
        ):

            auto_enroll_dialog(join_code)


# =========================================================
# RUN APPLICATION
# =========================================================
main()