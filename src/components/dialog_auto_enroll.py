import streamlit as st
from src.database.db import enroll_student_to_subject
from src.database.config import supabase
import time


# =========================================================
# QUICK ENROLLMENT DIALOG
# =========================================================
@st.dialog("Quick Enrollment")
def auto_enroll_dialog(subject_code):

    # -----------------------------------------------------
    # Get logged-in student id
    # -----------------------------------------------------
    student_id = st.session_state.student_data['student_id']

    # =====================================================
    # SEARCH SUBJECT USING SUBJECT CODE
    # =====================================================
    res = supabase.table('subject') \
        .select('subject_id, name, subject_code') \
        .eq('subject_code', subject_code) \
        .execute()

    # -----------------------------------------------------
    # Subject not found
    # -----------------------------------------------------
    if not res.data:

        st.error('Subject code not found!')

        if st.button('Close'):

            st.query_params.clear()

            st.rerun()

        return

    # -----------------------------------------------------
    # Get subject data
    # -----------------------------------------------------
    subject = res.data[0]

    # =====================================================
    # CHECK IF ALREADY ENROLLED
    # =====================================================
    check = supabase.table('subject_students') \
        .select('*') \
        .eq('subject_id', subject['subject_id']) \
        .eq('student_id', student_id) \
        .execute()

    # -----------------------------------------------------
    # Already enrolled
    # -----------------------------------------------------
    if check.data:

        st.info("You're already enrolled!")

        if st.button('Got it!'):

            st.query_params.clear()

            st.rerun()

        return

    # =====================================================
    # CONFIRM ENROLLMENT
    # =====================================================
    st.markdown(
        f"Would you like to enroll in "
        f"**{subject['name']}**?"
    )

    # Buttons
    col1, col2 = st.columns(2)

    # -----------------------------------------------------
    # Cancel button
    # -----------------------------------------------------
    with col1:

        if st.button('No thanks'):

            st.query_params.clear()

            st.rerun()

    # -----------------------------------------------------
    # Enroll button
    # -----------------------------------------------------
    with col2:

        if st.button(
            'Yes enroll now!',
            type='primary',
            width='stretch'
        ):

            # Enroll student
            enroll_student_to_subject(
                student_id,
                subject['subject_id']
            )

            # Success message
            st.success('Joined successfully!')

            # Clear query params
            st.query_params.clear()

            # Small delay
            time.sleep(2)

            # Refresh app
            st.rerun()