import streamlit as st

from src.database.db import (
    delete_lecture_session
)


@st.dialog(
    "Delete Lecture"
)
def delete_lecture_dialog(

    session_id
):

    st.warning(

        "This will permanently delete "
        "lecture and attendence logs."
    )

    st.write(
        "Are you sure?"
    )

    c1, c2 = st.columns(2)

    # =====================================
    # CANCEL
    # =====================================
    with c1:

        if st.button(

            "Cancel",

            use_container_width=True
        ):

            st.rerun()

    # =====================================
    # DELETE
    # =====================================
    with c2:

        if st.button(

            "Delete Lecture",

            type='primary',

            use_container_width=True
        ):

            try:

                delete_lecture_session(
                    session_id
                )

                st.toast(
                    "Lecture deleted"
                )

                st.rerun()

            except Exception as e:

                st.error(
                    f"Error: {e}"
                )