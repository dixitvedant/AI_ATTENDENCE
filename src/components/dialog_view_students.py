import streamlit as st
import pandas as pd

from src.database.db import (
    get_students_for_subject
)


@st.dialog(
    "Enrolled Students"
)
def view_students_dialog(
    subject_id
):

    students = (
        get_students_for_subject(
            subject_id
        )
    )

    # =====================================
    # NO STUDENTS
    # =====================================
    if not students:

        st.info(
            "No students enrolled yet"
        )
        return

    # =====================================
    # BUILD DATAFRAME
    # =====================================
    data = []

    for s in students:

        data.append({

            "Student ID":
                s[
                    'student_id'
                ],

            "Student Name":
                s[
                    'name'
                ]
        })

    df = pd.DataFrame(
        data
    )

    # =====================================
    # SEARCH
    # =====================================
    search = st.text_input(
        "Search Student"
    )

    if search:

        df = df[

            df[
                'Student Name'
            ]
            .str.contains(

                search,

                case=False,

                na=False
            )

            |

            df[
                'Student ID'
            ]
            .astype(str)
            .str.contains(

                search,

                case=False,

                na=False
            )
        ]

    # =====================================
    # DASHBOARD
    # =====================================
    st.metric(
        "Total Students",
        len(df)
    )

    st.divider()

    # =====================================
    # TABLE
    # =====================================
    st.dataframe(

        df,

        width='stretch',

        hide_index=True
    )