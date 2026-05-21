# =========================================
# Attendance Response
# =========================================
def attendance_reply(
    percent,
    present,
    total
):

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


# =========================================
# Subject Reply
# =========================================
def subject_reply(
    names
):

    return (
        "You are currently enrolled in:\n\n• "
        +
        "\n• ".join(
            names
        )
    )


# =========================================
# Teacher Reply
# =========================================
def teacher_reply(
    report
):

    return (
        "Here is your class attendance summary:\n\n"
        +
        report
    )


# =========================================
# Unknown
# =========================================
def fallback_reply():

    return (
        "I can help with attendance, "
        "subjects and academic information."
    )