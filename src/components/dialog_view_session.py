import streamlit as st
import pandas as pd
from datetime import (
    datetime,
    timedelta
)

from src.database.db import (
    get_lecture_logs
)


@st.dialog(
    "Lecture Attendance Details"
)
def view_lecture_dialog(

    session
):

    logs = get_lecture_logs(

        session[
            'session_id'
        ]
    )

    if not logs:

        st.info(
            "No attendance found"
        )
        return

    # =====================================
    # HEADER
    # =====================================
    st.subheader(

        session[
            'subject'
        ][
            'name'
        ]
    )

    # =====================================
    # UTC -> IST (+5:30)
    # =====================================
    dt = datetime.fromisoformat(

        session[
            'lecture_time'
        ].replace(
            "Z",
            "+00:00"
        )
    )

    dt = dt + timedelta(

        hours=5,

        minutes=30
    )

    lecture_time = dt.strftime(

        "%Y-%m-%d %I:%M:%S %p"
    )

    st.caption(
        lecture_time
    )

    # =====================================
    # BUILD DATA
    # =====================================
    data = []

    for log in logs:

        data.append({

            "Student ID":

                log[
                    'students'
                ][
                    'student_id'
                ],

            "Student Name":

                log[
                    'students'
                ][
                    'name'
                ],

            "Status":

                "✅ Present"

                if log[
                    'is_present'
                ]

                else

                "❌ Absent"
        })

    df = pd.DataFrame(
        data
    )

    # =====================================
    # SUMMARY
    # =====================================
    present = len(

        df[
            df[
                'Status'
            ]
            ==
            "✅ Present"
        ]
    )

    total = len(df)

    absent = (

        total
        -
        present
    )

    c1,c2,c3 = st.columns(3)

    with c1:

        st.metric(

            "Students",

            total
        )

    with c2:

        st.metric(

            "Present",

            present
        )

    with c3:

        st.metric(

            "Absent",

            absent
        )

    st.divider()

    # =====================================
    # TABLE
    # =====================================
    st.dataframe(

        df,

        hide_index=True,

        width='stretch'
    )