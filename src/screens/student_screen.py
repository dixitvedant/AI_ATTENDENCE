#Import Streamlit library
import streamlit as st

from src.components.header import header_dashboard
from src.ui.base_layout import style_background_dashboard
from src.ui.base_layout import style_base_layout
from src.components.footer import footer_dashboard
from src.components.dialog_enroll import enroll_dialog
from src.database.db import get_all_students,create_student,get_student_subjects,get_student_attendence,unenroll_student_to_subject
from src.components.subject_card import subject_card

#Import PIL Image for image processing
from PIL import Image

#Import NumPy
import numpy as np

#Import face recognition functions
from src.pipelines.face_pipeline import (
    predict_attendence,
    get_face_embeddings,
    train_classifier
)

#Import voice embedding function
from src.pipelines.voice_pipeline import get_voice_embedding

#Import database functions
from src.database.db import (
    get_all_students,
    create_student
)


#Student dashboard function
def student_dashboard():

    # =====================================================
    # GET LOGGED IN STUDENT DATA
    # =====================================================
    student_data = st.session_state.student_data
    student_id = student_data['student_id']

    # =====================================================
    # TOP HEADER SECTION
    # =====================================================
    c1, c2 = st.columns(
        2,
        vertical_alignment='center',
        gap='xxlarge'
    )

    # -----------------------------------------------------
    # Left column
    # -----------------------------------------------------
    with c1:
        header_dashboard()

    # -----------------------------------------------------
    # Right column
    # -----------------------------------------------------
    with c2:

        # Welcome message
        st.subheader(
            f"Welcome, {student_data['name']}"
        )

        # Logout button
        if st.button(
            "Logout",
            type='secondary',
            key='loginbackbtn',
            shortcut="control+backspace"
        ):

            # Reset login state
            st.session_state['is_logged_in'] = False

            # Remove session data
            del st.session_state.student_data

            # Refresh app
            st.rerun()

    # =====================================================
    # SPACING
    # =====================================================
    st.space()

    # =====================================================
    # SUBJECT HEADER + ENROLL BUTTON
    # =====================================================
    c1, c2 = st.columns(2)

    # Left column
    with c1:
        st.header('Your Enrolled Subjects')

    # Right column
    with c2:

        if st.button(
            'Enroll in Subject',
            type='primary',
            width='stretch'
        ):

            enroll_dialog()

    # Divider
    st.divider()

    # =====================================================
    # LOAD SUBJECTS + ATTENDANCE
    # =====================================================
    with st.spinner(
        'Loading your enrolled subjects..'
    ):

        subjects = get_student_subjects(student_id)

        logs = get_student_attendence(student_id)

    # =====================================================
    # CREATE ATTENDANCE STATS MAP
    # =====================================================
    stats_map = {}

    for log in logs:

        sid = log['subject_id']

        # Create subject entry
        if sid not in stats_map:

            stats_map[sid] = {
                "total": 0,
                "attended": 0
            }

        # Total classes
        stats_map[sid]['total'] += 1

        # Present count
        if log.get('is_present'):

            stats_map[sid]['attended'] += 1

    # =====================================================
    # DISPLAY SUBJECT CARDS
    # =====================================================
    cols = st.columns(2)

    for i, sub_node in enumerate(subjects):

        # Subject data
        sub = sub_node['subject']

        sid = sub['subject_id']

        # Get attendance stats
        stats = stats_map.get(
            sid,
            {
                "total": 0,
                "attended": 0
            }
        )

        # =================================================
        # UNENROLL BUTTON FUNCTION
        # =================================================
        def unenroll_button(
            sid=sid,
            sub_name=sub['name']
        ):

            if st.button(
                "Unenroll from this course",
                type='tertiary',
                width='stretch',
                icon=':material/delete_forever:',
                key=f"unenroll_{sid}"
            ):

                # Remove student from subject
                unenroll_student_to_subject(
                    student_id,
                    sid
                )

                # Success message
                st.toast(
                    f"Unenrolled from {sub_name} successfully!"
                )

                # Refresh page
                st.rerun()

        # =================================================
        # SUBJECT CARD UI
        # =================================================
        with cols[i % 2]:

            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=[
                    (
                        '📅',
                        'Total',
                        stats['total']
                    ),
                    (
                        '✅',
                        'Attended',
                        stats['attended']
                    ),
                ],
                footer_callback=unenroll_button
            )

    # =====================================================
    # FOOTER
    # =====================================================
    footer_dashboard()


#Student Screen after clicking student portal
def student_screen():
    
    #Apply dashboard background styling
    style_background_dashboard()

    #Apply base layout styling
    style_base_layout()
    
    #Check if student already logged in
    if "student_data" in st.session_state:

        #Open dashboard directly
        student_dashboard()

        #Stop further execution
        return

    #Create two columns layout
    c1, c2 = st.columns(
        2,
        vertical_alignment='center',
        gap='xxlarge'
    )

    #Left column
    with c1:

        #Display dashboard header
        header_dashboard()

    #Right column
    with c2:

        #Home button
        if st.button(
            "Go back to Home",
            type='secondary',
            shortcut="control+backspace",
            key="teacher_login_home_btn"
        ):

            #Reset login type
            st.session_state['login_type'] = None

            #Reload app
            st.rerun()

    #Page title
    st.header(
        'Login using FaceID',
        text_alignment='center'
    )

    #Vertical spacing
    st.space()
    st.space()

    #Registration flag
    show_registration=False

    #Open webcam for face capture
    photo_source=st.camera_input(
        "Position your face in the center"
    )

    #If image captured
    if photo_source:

        #Convert image into RGB NumPy array
        img = np.array(
            Image.open(photo_source).convert("RGB")
        )

        #Loading spinner
        with st.spinner('AI is scanning'):

            #Run face recognition pipeline
            detected,all_ids,num_faces=predict_attendence(img)

            #If no face detected
            if num_faces==0:

                #Warning message
                st.warning('Face not found!!')

            #If multiple faces detected
            elif num_faces>1:

                #Warning message
                st.warning('Multiple faces found')

            #If only one face found
            else:

                #If student recognized
                if detected:

                    #Get recognized student ID
                    student_id=list(detected.keys())[0]

                    #Fetch all students from database
                    all_students=get_all_students()

                    #Find matching student
                    student=next(
                        (
                            s for s in all_students
                            if s['student_id']==student_id
                        ),
                        None
                    )

                    #If student exists
                    if student:

                        #Store login status
                        st.session_state.is_logged_in=True

                        #Store user role
                        st.session_state.user_role='student'

                        #Store student data
                        st.session_state.student_data=student

                        #Welcome toast message
                        st.toast(
                            f"Welcome Back {student['name']}"
                        )

                        #Import time module
                        import time

                        #Wait for 1 second
                        time.sleep(1)

                        #Reload app
                        st.rerun()

                #If face not recognized
                else:

                    #Show information
                    st.info(
                        'Face not recognized!You must be a new student!'
                    )

                    #Enable registration form
                    show_registration=True

        #If registration required
        if show_registration:

            #Create bordered container
            with st.container(border=True):

                #Registration title
                st.header('Register new Profile')

                #Input student name
                new_name=st.text_input(
                    'Enter your name',
                    placeholder='E.g,Vedant Dixit'
                )

                #Voice enrollment title
                st.subheader('Optional:Voice Enrollment')

                #Voice enrollment info
                st.info(
                    'Enroll your voice for only attendence'
                )

                #Initialize audio variable
                audio_data=None

                #Try audio recording
                try:

                    #Record voice
                    audio_data=st.audio_input(
                        'Record a short phrase like i am present,My name is Akash.'
                    )

                #Handle audio error
                except Exception:

                    #Error message
                    st.error('Audio Data failed')

                #Create account button
                if st.button(
                    'Create Account',
                    type='primary'
                ):

                    #If name entered
                    if new_name:

                        #Loading spinner
                        with st.spinner('Creating Profile..'):

                            #Convert image into NumPy array
                            img = np.array(
                                Image.open(photo_source).convert("RGB")
                            )

                            #Generate face embeddings
                            encodings=get_face_embeddings(img)

                            #If embeddings generated
                            if encodings:

                                #Take first embedding
                                face_emb=encodings[0].tolist()

                                #Initialize voice embedding
                                voice_emb=None

                                #If audio available
                                if audio_data:

                                    #Generate voice embedding
                                    voice_emb=get_voice_embedding(
                                        audio_data.read()
                                    )

                                #Create student profile in database
                                response_data=create_student(
                                    new_name,
                                    face_embedding=face_emb,
                                    voice_embedding=voice_emb
                                )

                                #If registration successful
                                if response_data:

                                    #Retrain face classifier
                                    train_classifier()

                                    #Store login status
                                    st.session_state.is_logged_in=True

                                    #Store user role
                                    st.session_state.user_role='student'

                                    #Store student data
                                    st.session_state.student_data=response_data.data[0]

                                    #Success toast message
                                    st.toast(
                                        f"Profile Created! Hi {response_data.data[0]['name']}"
                                    )

                                    #Import time module
                                    import time

                                    #Wait for 1 second
                                    time.sleep(1)

                                    #Reload app
                                    st.rerun()

                                #If registration failed
                                else:

                                    #Show error
                                    st.error(
                                        'Couldnt capture your facial features for registration'
                                    )

                    #If name empty
                    else:

                        #Warning message
                        st.warning("Enter your name")

    #Display footer
    footer_dashboard()