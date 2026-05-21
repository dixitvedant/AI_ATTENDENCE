import streamlit as st

from src.services.db_ai_services import (
    get_student_attendance,
    get_student_subjects,
    teacher_summary,
    get_subject_attendance,
    check_subject_enrollment,
    get_available_subjects,
    get_teacher_subjects
)


# ===================================
# SnapClass Smart Assistant
# ===================================
def ask_ai(question):

    q = (
        question
        .lower()
        .strip()
    )

    role = st.session_state.get(
        "user_role"
    )

    # ==========================
    # STUDENT
    # ==========================
    if role == "student":

        student_data = (
            st.session_state.get(
                "student_data"
            )
        )

        student_id = (
            student_data.get(
                "student_id"
            )
            if student_data
            else None
        )

        if not student_id:

            return (
                "Student login not found."
            )

        subjects = (
            get_available_subjects()
        )

        # Subject Attendance
        if any(
            w in q
            for w in [
                "attendance",
                "regular",
                "status"
            ]
        ):

            for sub in subjects:

                if sub in q:

                    return (
                        get_subject_attendance(
                            student_id,
                            sub
                        )
                    )

        # Enrollment
        if any(
            w in q
            for w in [
                "enrolled",
                "am i in",
                "taking",
                "study",
                "studying"
            ]
        ):

            for sub in subjects:

                if sub in q:

                    return (
                        check_subject_enrollment(
                            student_id,
                            sub
                        )
                    )

        # Attendance History
        if (
            "logs" in q
            or
            "history" in q
        ):

            return (
                "Attendance history feature can be added next."
            )

        # General Attendance
        if any(
            w in q
            for w in [
                "attendance",
                "regular",
                "present",
                "attend",
                "classes",
                "status"
            ]
        ):

            return (
                get_student_attendance(
                    student_id
                )
            )

        # Subjects
        if any(
            w in q
            for w in [
                "subject",
                "subjects",
                "course",
                "courses",
                "academic"
            ]
        ):

            return (
                get_student_subjects(
                    student_id
                )
            )

        # Summary
        if any(
            w in q
            for w in [
                "summary",
                "dashboard",
                "overview",
                "profile"
            ]
        ):

            return (
                get_student_attendance(
                    student_id
                )
                +
                "\n\n"
                +
                get_student_subjects(
                    student_id
                )
            )

        return (
            "I can help with attendance, subjects, enrollment and academic summary."
        )

    # ==========================
    # TEACHER
    # ==========================
    elif role == "teacher":

        teacher_data = (
            st.session_state.get(
                "teacher_data"
            )
        )

        teacher_id = (
            teacher_data.get(
                "teacher_id"
            )
            if teacher_data
            else None
        )

        if not teacher_id:

            return (
                "Teacher login not found."
            )

        # Teacher Subjects
        if any(
            w in q
            for w in [
                "subject",
                "subjects",
                "teach",
                "teaching"
            ]
        ):

            return (
                get_teacher_subjects(
                    teacher_id
                )
            )

        # Teacher Summary
        if any(
            w in q
            for w in [
                "summary",
                "attendance",
                "report",
                "class",
                "classes",
                "performance",
                "dashboard"
            ]
        ):

            return (
                teacher_summary(
                    teacher_id
                )
            )

        return (
            "I can help with teaching subjects and class attendance summary."
        )

    return (
        "Please login first."
    )