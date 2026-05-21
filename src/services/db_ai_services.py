import streamlit as st
from supabase import create_client


# =====================================
# Supabase
# =====================================
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(
    url,
    key
)


# =====================================
# Dynamic Subject List
# =====================================
def get_available_subjects():

    rows = (
        supabase
        .table(
            "subject"
        )
        .select(
            "name"
        )
        .execute()
    )

    return [
        s["name"].lower()
        for s in rows.data
    ]


# =====================================
# Student Attendance
# =====================================
def get_student_attendance(
    student_id
):

    logs = (
        supabase
        .table(
            "attendence_logs"
        )
        .select(
            "is_present"
        )
        .eq(
            "student_id",
            student_id
        )
        .execute()
    )

    data = logs.data

    if not data:

        return (
            "I couldn't find attendance records yet."
        )

    total = len(data)

    present = sum(
        1
        for r in data
        if r["is_present"]
    )

    percent = (
        present
        / total
    ) * 100

    if percent >= 75:

        status = (
            "You are maintaining regular attendance."
        )

    elif percent >= 60:

        status = (
            "Your attendance is moderate and could improve."
        )

    else:

        status = (
            "Your attendance is currently low and needs attention."
        )

    return (
        f"Your attendance is "
        f"{percent:.2f}% "
        f"({present}/{total} classes attended).\n\n"
        f"{status}"
    )


# =====================================
# Student Subjects
# =====================================
def get_student_subjects(
    student_id
):

    rows = (
        supabase
        .table(
            "subject_students"
        )
        .select(
            "subject_id"
        )
        .eq(
            "student_id",
            student_id
        )
        .execute()
    )

    ids = [
        r["subject_id"]
        for r in rows.data
    ]

    if not ids:

        return (
            "No enrolled subjects found."
        )

    subjects = (
        supabase
        .table(
            "subject"
        )
        .select(
            "name"
        )
        .in_(
            "subject_id",
            ids
        )
        .execute()
    )

    names = [
        s["name"]
        for s in subjects.data
    ]

    return (
        "You are currently enrolled in:\n\n• "
        +
        "\n• ".join(
            names
        )
    )


# =====================================
# Subject Attendance
# =====================================
def get_subject_attendance(
    student_id,
    subject_name
):

    subject = (
        supabase
        .table(
            "subject"
        )
        .select(
            "subject_id,name"
        )
        .ilike(
            "name",
            f"%{subject_name}%"
        )
        .execute()
    )

    if not subject.data:

        return (
            f"I couldn't find "
            f"{subject_name}."
        )

    sid = subject.data[0][
        "subject_id"
    ]

    logs = (
        supabase
        .table(
            "attendence_logs"
        )
        .select(
            "is_present"
        )
        .eq(
            "student_id",
            student_id
        )
        .eq(
            "subject_id",
            sid
        )
        .execute()
    )

    data = logs.data

    if not data:

        return (
            f"No attendance found for "
            f"{subject.data[0]['name']}."
        )

    total = len(data)

    present = sum(
        1
        for r in data
        if r["is_present"]
    )

    percent = (
        present
        / total
    ) * 100

    return (
        f"Your attendance in "
        f"{subject.data[0]['name']} "
        f"is {percent:.2f}% "
        f"({present}/{total} classes)."
    )


# =====================================
# Enrollment Check
# =====================================
def check_subject_enrollment(
    student_id,
    subject_name
):

    enroll = (
        supabase
        .table(
            "subject_students"
        )
        .select(
            "subject_id"
        )
        .eq(
            "student_id",
            student_id
        )
        .execute()
    )

    ids = [
        r["subject_id"]
        for r in enroll.data
    ]

    subject = (
        supabase
        .table(
            "subject"
        )
        .select(
            "name"
        )
        .in_(
            "subject_id",
            ids
        )
        .ilike(
            "name",
            f"%{subject_name}%"
        )
        .execute()
    )

    if subject.data:

        return (
            f"Yes, you are enrolled in "
            f"{subject.data[0]['name']}."
        )

    return (
        f"No, you are not enrolled in "
        f"{subject_name}."
    )


# =====================================
# Teacher Subjects
# =====================================
def get_teacher_subjects(
    teacher_id
):

    rows = (
        supabase
        .table(
            "subject"
        )
        .select(
            "name"
        )
        .eq(
            "teacher_id",
            teacher_id
        )
        .execute()
    )

    if not rows.data:

        return (
            "No subjects assigned."
        )

    names = [
        s["name"]
        for s in rows.data
    ]

    return (
        "You are teaching:\n\n• "
        +
        "\n• ".join(
            names
        )
    )


# =====================================
# Teacher Summary
# =====================================
def teacher_summary(
    teacher_id
):

    subs = (
        supabase
        .table(
            "subject"
        )
        .select(
            "subject_id,name"
        )
        .eq(
            "teacher_id",
            teacher_id
        )
        .execute()
    )

    if not subs.data:

        return (
            "No subjects assigned."
        )

    report = []

    for s in subs.data:

        sid = s["subject_id"]

        logs = (
            supabase
            .table(
                "attendence_logs"
            )
            .select(
                "is_present"
            )
            .eq(
                "subject_id",
                sid
            )
            .execute()
        )

        total = len(logs.data)

        present = sum(
            1
            for r in logs.data
            if r["is_present"]
        )

        percent = (
            present / total * 100
        ) if total else 0

        report.append(
            f"• {s['name']} — "
            f"{percent:.0f}% "
            f"({present}/{total})"
        )

    return (
        "Here is your class attendance summary:\n\n"
        +
        "\n".join(report)
    )