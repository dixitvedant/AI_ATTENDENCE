import streamlit as st

from src.database.db import create_attendence , create_attendence_session


def clear_all_attendence_state():

    st.session_state.face_attendence_results = False

    st.session_state.voice_attendence_results = False

    st.session_state.attendence_images = []

    if 'uploaded_file_names' in st.session_state:
        st.session_state.uploaded_file_names = set()


def show_attendence_result(df, logs):

    st.write('Please review attendance before confirming.')

    st.dataframe(
        df,
        hide_index=True,
        width='stretch'
    )

    col1, col2 = st.columns(2)

    # =====================================================
    # DISCARD
    # =====================================================
    with col1:

        if st.button(
            'Discard',
            width='stretch',
        ):

            clear_all_attendence_state()

            st.rerun()

    # =====================================================
    # CONFIRM SAVE
    # =====================================================
    with col2:

        if st.button(
            'Confirm & Save',
            width='stretch',
            type='primary',
        ):

            try:

                # =====================================
                # CREATE LECTURE SESSION
                # =====================================
                subject_id = logs[0][
                    'subject_id'
                ]

                teacher_id = (
                    st.session_state
                    .teacher_data[
                        'teacher_id'
                    ]
                )

                total_students = len(
                    logs
                )

                present_students = sum(

                    1

                    for log in logs

                    if log[
                        'is_present'
                    ]
                )

                session = create_attendence_session(

                    subject_id,

                    teacher_id,

                    total_students,

                    present_students
                )

                # =====================================
                # SAVE ATTENDANCE INSIDE SESSION
                # =====================================
                create_attendence(

                    logs,

                    session[
                        'session_id'
                    ]
                )
                clear_all_attendence_state()

                st.toast('Attendance taken successfully')

                st.rerun()

            except Exception as e:

                st.error(f'Sync failed: {e}')


@st.dialog("Attendance Reports")
def attendence_result_dialog(df, logs):

        show_attendence_result(df, logs)