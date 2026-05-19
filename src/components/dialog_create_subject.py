import streamlit as st
from src.database.db import create_subject

@st.dialog("Create New Subject")
def create_subject_dialog(teacher_id):
    st.write("Enter the details of new subject")
    sub_id=st.text_input("Subject Code",placeholder="CS101")
    sub_name=st.text_input("Subject Name",placeholder="Introduction to Computer Science")
    sub_class=st.text_input("Class Section",placeholder="FY A")


    if st.button("Create Subject Now",type='primary',width='stretch'):
        if sub_id and sub_name and sub_class:
            try:
                create_subject(sub_id,sub_name,sub_class,teacher_id)
                st.toast("Subject Created Sucessfully...!!!!")
                st.rerun()
            except Exception as e:
                st.error(f"Error:{str(e)}")
        else:
            st.warning("Please fill the all required fields")