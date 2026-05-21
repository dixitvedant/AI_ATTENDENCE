import streamlit as st
from src.database.db import delete_subject


@st.dialog(
    "Delete Subject"
)
def delete_subject_dialog(
    subject_id
):

    st.warning(
        "Delete subject permanently?"
    )

    if st.button(
        "Delete",
        type='primary'
    ):

        delete_subject(
            subject_id
        )

        st.success(
            "Deleted"
        )

        st.rerun()