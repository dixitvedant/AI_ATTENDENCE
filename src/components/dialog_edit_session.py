import streamlit as st

from src.database.db import (

    get_lecture_logs,

    update_lecture_log
)


@st.dialog(
    "Edit Lecture Attendance"
)
def edit_lecture_dialog(

    session_id
):

    logs = (

        get_lecture_logs(
            session_id
        )
    )

    if not logs:

        st.info(
            "No attendance found"
        )
        return

    st.write(
        "Modify attendance below"
    )

    edited_logs = []

    # =====================================
    # STUDENTS
    # =====================================
    for log in logs:

        c1, c2 = st.columns(
            [3,1]
        )

        with c1:

            st.write(

                f"{log['students']['name']} "

                f"("

                f"{log['students']['student_id']}"

                f")"
            )

        with c2:

            status = st.checkbox(

                "Present",

                value=bool(

                    log[
                        'is_present'
                    ]
                ),

                key=
                    f"edit_{
                        log[
                            'id'
                        ]
                    }"
            )

            edited_logs.append({

                'id':

                    log[
                        'id'
                    ],

                'is_present':
                    status
            })

    st.divider()

    # =====================================
    # SAVE
    # =====================================
    if st.button(

        "Save Changes",

        type='primary',

        use_container_width=True
    ):

        try:

            for row in edited_logs:

                update_lecture_log(

                row[
                    'id'
                ],

                row[
                    'is_present'
                ],

                session_id
            )

            st.toast(
                "Lecture updated"
            )

            st.rerun()

        except Exception as e:

            st.error(
                f"Error: {e}"
            )