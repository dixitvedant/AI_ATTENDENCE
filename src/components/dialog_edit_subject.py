import streamlit as st
from src.database.db import update_subject


@st.dialog(
    "Edit Subject"
)
def edit_subject_dialog(sub):

    name = st.text_input(
        "Subject Name",
        value=sub['name']
    )

    section = st.text_input(
        "Section",
        value=sub['section']
    )

    if st.button(
        "Update",
        type='primary'
    ):

        update_subject(

            sub[
                'subject_id'
            ],

            name,

            section
        )

        st.success(
            "Updated!"
        )

        st.rerun()