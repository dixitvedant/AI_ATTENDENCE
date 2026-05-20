import streamlit as st

from src.ui.base_layout import style_background_dashboard, style_base_layout

from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import check_teacher_exists, create_teacher, teacher_login, get_teacher_subject,get_attendance_for_teacher
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog

from src.pipelines.face_pipeline import predict_attendence
from src.components.dialog_attendence_results import show_attendence_result
import numpy as np

from datetime import datetime

import pandas as pd

from src.database.config import supabase


from src.components.dialog_voice_attendence import voice_attendence_dialog

def teacher_screen():

    style_background_dashboard()
    style_base_layout()

    if "teacher_data" in st.session_state:
        teacher_dashboard()
    elif 'teacher_login_type' not in st.session_state or st.session_state.teacher_login_type=="login":
        teacher_screen_login()
    elif st.session_state.teacher_login_type == "register":
        teacher_screen_register()





def teacher_dashboard():
    teacher_data = st.session_state.teacher_data
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        st.subheader(f"""Welcome, {teacher_data['name']} """)
        if st.button("Logout", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['is_logged_in'] = False
            del st.session_state.teacher_data 
            st.rerun()


    st.space()

    if "current_teacher_tab" not in st.session_state:
        st.session_state.current_teacher_tab = 'take_attendance'
    tab1, tab2, tab3 = st.columns(3)


    with tab1:
        type1 = "primary" if st.session_state.current_teacher_tab == 'take_attendence' else "tertiary"
        if st.button('Take Attendance',type=type1, width='stretch', icon=':material/ar_on_you:'):
            st.session_state.current_teacher_tab = 'take_attendance'
            st.rerun()

    with tab2:
        type2 = "primary" if st.session_state.current_teacher_tab == 'manage_subjects' else "tertiary"
        if st.button('Manage Subjects', type=type2, width='stretch', icon=':material/book_ribbon:'):
            st.session_state.current_teacher_tab = 'manage_subjects'
            st.rerun()

    with tab3:
        type3 = "primary" if st.session_state.current_teacher_tab == 'attendence_records' else "tertiary"
        if st.button('Attendance Records',type=type3, width='stretch', icon=':material/cards_stack:'):
            st.session_state.current_teacher_tab = 'attendence_records'
            st.rerun()


    st.divider()

    if st.session_state.current_teacher_tab == "take_attendance":
        teacher_tab_take_attendence()
    if st.session_state.current_teacher_tab == "manage_subjects":
        teacher_tab_manage_subjects()
    if st.session_state.current_teacher_tab == "attendence_records":
        teacher_tab_attendence_records()

    


    footer_dashboard()

def teacher_tab_take_attendence():

    teacher_id = st.session_state.teacher_data['teacher_id']

    st.header('Take AI Attendance')

    # =====================================================
    # SESSION STATES
    # =====================================================
    if 'attendence_images' not in st.session_state:
        st.session_state.attendence_images = []

    if 'voice_attendence_results' not in st.session_state:
        st.session_state.voice_attendence_results = False

    if 'face_attendence_results' not in st.session_state:
        st.session_state.face_attendence_results = False

    # =====================================================
    # SUBJECTS
    # =====================================================
    subjects = get_teacher_subject(teacher_id)

    if not subjects:
        st.warning('You havent created any subjects yet! Please create one to begin!')
        return

    subject_options = {
        f"{s['name']} - {s['subject_code']}": s['subject_id']
        for s in subjects
    }

    col1, col2 = st.columns([3, 1], vertical_alignment='bottom')

    with col1:
        selected_subject_label = st.selectbox(
            'Select Subject',
            options=list(subject_options.keys())
        )

    with col2:
        if st.button(
            'Add Photos',
            type='primary',
            icon=':material/photo_prints:',
            width='stretch'
        ):
            add_photos_dialog()

    selected_subject_id = subject_options[selected_subject_label]


    # =====================================================
    # IMAGE PREVIEW
    # =====================================================
    if st.session_state.attendence_images:

        st.divider()

        st.subheader('Added Photos')

        gallery_cols = st.columns(4)

        for idx, img in enumerate(st.session_state.attendence_images):

            with gallery_cols[idx % 4]:

                st.image(
                    img,
                    caption=f'Photo {idx + 1}',
                    width='stretch'
                )

    # =====================================================
    # BUTTONS
    # =====================================================
    has_photos = bool(st.session_state.attendence_images)

    c1, c2, c3 = st.columns(3)

    # -----------------------------------------------------
    # CLEAR PHOTOS
    # -----------------------------------------------------
    with c1:

        if st.button(
            'Clear all photos',
            width='stretch',
            type='tertiary',
            icon=':material/delete:',
            disabled=not has_photos
        ):

            st.session_state.attendence_images = []

            if 'uploaded_file_names' in st.session_state:
                st.session_state.uploaded_file_names = set()

            st.toast('All photos cleared')

            st.rerun()

    # -----------------------------------------------------
    # FACE ANALYSIS
    # -----------------------------------------------------
    with c2:

        if st.button(
            'Run Face Analysis',
            width='stretch',
            type='secondary',
            icon=':material/analytics:',
            disabled=not has_photos
        ):

            with st.spinner('Deep scanning classroom photos...'):

                try:

                    all_detected_ids = {}

                    for idx, img in enumerate(st.session_state.attendence_images):

                        img_np = np.array(img.convert('RGB'))

                        detected, _, _ = predict_attendence(img_np)

                        if detected:

                            for sid in detected.keys():

                                student_id = int(sid)

                                all_detected_ids.setdefault(
                                    student_id,
                                    []
                                ).append(f"Photo {idx + 1}")

                    enrolled_res = (
                        supabase
                        .table('subject_students')
                        .select("*, students(*)")
                        .eq('subject_id', selected_subject_id)
                        .execute()
                    )

                    enrolled_students = enrolled_res.data

                    if not enrolled_students:
                        st.warning('No students enrolled in this course')
                        return

                    results = []

                    attendence_to_log = []

                    current_timestamp = datetime.now().strftime(
                        "%Y-%m-%dT%H:%M:%S"
                    )

                    for node in enrolled_students:

                        student = node['students']

                        sources = all_detected_ids.get(
                            int(student['student_id']),
                            []
                        )

                        is_present = len(sources) > 0

                        results.append({
                            "Name": student['name'],
                            "ID": student['student_id'],
                            "Source": ", ".join(sources)
                            if is_present else "-",
                            "Status": "✅ Present"
                            if is_present else "❌ Absent"
                        })

                        attendence_to_log.append({
                            'student_id': student['student_id'],
                            'subject_id': selected_subject_id,
                            'timestamp': current_timestamp,
                            'is_present': bool(is_present)
                        })

                    st.session_state.face_attendence_results = (
                        pd.DataFrame(results),
                        attendence_to_log
                    )

                    st.toast('Face analysis completed')

                except Exception as e:

                    st.error(f'Face analysis failed: {e}')

    # -----------------------------------------------------
    # VOICE ATTENDANCE
    # -----------------------------------------------------
    with c3:

        if st.button(
            'Use Voice Attendance',
            type='primary',
            width='stretch',
            icon=':material/mic:'
        ):

            voice_attendence_dialog(selected_subject_id)

    # =====================================================
    # SHOW FACE RESULTS
    # =====================================================
    if st.session_state.face_attendence_results:

        st.divider()

        df_results, logs = st.session_state.face_attendence_results

        show_attendence_result(df_results, logs)






def teacher_tab_manage_subjects():

    teacher_id = st.session_state.teacher_data['teacher_id']

    col1, col2 = st.columns(2)

    with col1:
        st.header('Manage Subjects')

    with col2:

        if st.button(
            'Create New Subject',
            width='stretch',
        ):

            create_subject_dialog(teacher_id)

    # =====================================================
    # GET SUBJECTS
    # =====================================================
    subjects = get_teacher_subject(teacher_id)

    # =====================================================
    # SHOW SUBJECTS
    # =====================================================
    if subjects:

        for sub in subjects:

            stats = [
                ("🫂", "Students", sub['total_students']),
                ("🕰️", "Classes", sub['total_classes']),
            ]

            # =============================================
            # SHARE BUTTON CALLBACK
            # =============================================
            def share_btn(
                subject_name=sub['name'],
                subject_code=sub['subject_code']
            ):

                if st.button(
                    f"Share Code: {subject_name}",
                    key=f"share_{subject_code}",
                    icon=":material/share:"
                ):

                    share_subject_dialog(
                        subject_name,
                        subject_code
                    )

                st.space()

            # =============================================
            # SUBJECT CARD
            # =============================================
            subject_card(
                name=sub['name'],
                code=sub['subject_code'],
                section=sub['section'],
                stats=stats,
                footer_callback=share_btn
            )

    else:

        st.info(
            "NO SUBJECTS FOUND. CREATE ONE ABOVE"
        )



 [2026-05-20 06:04:56.856867] + cuda-pathfinder==1.5.4

 + cuda-toolkit==13.0.2

 + [2026-05-20 06:04:56.857384] decorator==5.3.1

 + deprecation==2.1.0

 + dlib-bin==[2026-05-20 06:04:56.857691] 20.0.1

 + face-recognition-models==0.3.0 (from git+https://github.com/ageitgey/face_recognition_models@e67de717267507d1e9246de95692eb8be736ab61)

 + filelock==[2026-05-20 06:04:56.857910] 3.29.0

 + fsspec==2026.4.0

 + gitdb==4.0.12

 +[2026-05-20 06:04:56.858147]  gitpython==3.1.50

 + h11==0.16.0

 +[2026-05-20 06:04:56.858832]  h2==4.3.0

 + hpack==4.1.0

 + httpcore==1.0.9

 + httptools==0.7.1

 + [2026-05-20 06:04:56.859016] httpx==0.28.1

 + hyperframe==6.1.0

 + idna==3.15

 + itsdangerous==2.2.0

 +[2026-05-20 06:04:56.859197]  jinja2==3.1.6

 + joblib==1.5.3

 + jsonschema==4.26.0

 + jsonschema-specifications==2025.9.1

 + lazy-loader==0.5[2026-05-20 06:04:56.859402] 

 + librosa==0.11.0

 + llvmlite==0.47.0

 + markdown-it-py==4.2.0

 + markupsafe==3.0.3

 [2026-05-20 06:04:56.859545] + mdurl==0.1.2

 + mmh3==5.2.1

 + mpmath==1.3.0

 + msgpack==1.1.2[2026-05-20 06:04:56.859731] 

 + multidict==6.7.1

 + narwhals==2.21.2

 + networkx==3.6.1

 + numba==[2026-05-20 06:04:56.859884] 0.65.1

 + numpy==2.4.6

 + nvidia-cublas==13.1.1.3

 + nvidia-cuda-cupti==13.0.85[2026-05-20 06:04:56.860022] 

 + nvidia-cuda-nvrtc==13.0.88

 + nvidia-cuda-runtime==13.0.96

 + nvidia-cudnn-cu13==9.20.0.48

 + nvidia-cufft[2026-05-20 06:04:56.860140] ==12.0.0.61

 + nvidia-cufile==1.15.1.6

 + [2026-05-20 06:04:56.860275] nvidia-curand==10.4.0.35

 + nvidia-cusolver==12.0.4.66

 + nvidia-cusparse==12.6.3.3

 + nvidia-cusparselt-cu13==0.8.1

 + nvidia-nccl-cu13[2026-05-20 06:04:56.860452] ==2.29.7

 + nvidia-nvjitlink==13.0.88

 + nvidia-nvshmem-cu13==3.4.5

 + nvidia-nvtx==[2026-05-20 06:04:56.860597] 13.0.85

 + packaging==26.2

 + pandas==3.0.3

 + pillow==12.2.0

 + [2026-05-20 06:04:56.860753] platformdirs==4.9.6

 + pooch==1.9.0

 + postgrest==2.30.0

 + propcache==[2026-05-20 06:04:56.860951] 0.5.2

 + protobuf==7.35.0

 + pyarrow==24.0.0

 + pycparser==3.0

 + pydantic==2.13.4

 + pydantic-core==2.46.4

 + pydeck==0.9.2

 + pygments==2.20.0

 + pyiceberg==0.11.1[2026-05-20 06:04:56.861226] 

 + pyjwt==2.12.1

 + pyparsing==3.3.2

 + [2026-05-20 06:04:56.861460] pyroaring==1.1.0

 + python-dateutil==2.9.0.post0

 + python-multipart[2026-05-20 06:04:56.861743] ==0.0.29

 + realtime==2.30.0

 + referencing==0.37.0

 + requests==2.34.2

 + resemblyzer==0.1.4

 + rich==14.3.4

 + rpds-py==0.30.0

 + scikit-learn[2026-05-20 06:04:56.861985] ==1.8.0

 + scipy==1.17.1

 + segno==1.6.6

 + setuptools==69.5.1

 + six==1.17.0[2026-05-20 06:04:56.864622] 

 + smmap==5.0.3

 + soundfile==0.13.1

 + soxr==1.1.0

 + standard-aifc==3.13.0[2026-05-20 06:04:56.864853] 

 + standard-chunk==3.13.0

 + standard-sunau==3.13.0

 + starlette==1.0.0

 + storage3==[2026-05-20 06:04:56.865069] 2.30.0

 + streamlit==1.57.0

 + strenum==0.4.15

 + strictyaml==1.7.3

 +[2026-05-20 06:04:56.865235]  supabase==2.30.0

 + supabase-auth==2.30.0

 + supabase-functions==2.30.0

 + sympy==1.14.0

 [2026-05-20 06:04:56.865431] + tenacity==9.1.4

 + threadpoolctl==3.6.0

 + toml==0.10.2

 + torch==[2026-05-20 06:04:56.865668] 2.12.0

 + triton==3.7.0

 + typing==3.10.0.0

 + typing-extensions==4.15.0

 [2026-05-20 06:04:56.865885] + typing-inspection==0.4.2

 + urllib3==2.7.0

 + uvicorn==0.47.0[2026-05-20 06:04:56.866042] 

 + watchdog==6.0.0

 + webrtcvad==2.0.10

 +[2026-05-20 06:04:56.866242]  websockets==15.0.1

 + yarl==1.24.2

 + [2026-05-20 06:04:56.891018] zstandard==0.25.0

Checking if Streamlit is installed

Found Streamlit version 1.57.0 in the environment

Installing rich for an improved exception logging

Using uv pip install.

Using Python 3.14.5 environment at /home/adminuser/venv

Audited 1 package in 4ms


────────────────────────────────────────────────────────────────────────────────────────


[06:05:00] 🐍 Python dependencies were installed from /mount/src/ai_attendence/requirements.txt using uv.

Check if streamlit is installed

Streamlit is already installed

[06:05:01] 📦 Processed dependencies!

2026-05-20 06:05:03.361 Uvicorn server started on 0.0.0.0:8501




main
dixitvedant/ai_attendence/main/app.py



def login_teacher(username, password):
    if not username or not password:
        return False
    
    teacher = teacher_login(username, password)

    if teacher:
        st.session_state.user_role ='teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True
        return True
    

    return False
def teacher_screen_login():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()

    st.header('Login using password', text_alignment='center')
    st.space()
    st.space()


    teacher_username = st.text_input("Enter username", placeholder='vedant')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Login', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            if login_teacher(teacher_username, teacher_pass):
                st.toast("welcome back!", icon="👋")
                import time
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid username and password combo")

    with btnc2:
        if st.button('Register Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'register'

    footer_dashboard()



def register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm):
    if not teacher_username or not teacher_name or not teacher_pass:
        return False, "All Fields are required!"
    if check_teacher_exists(teacher_username):
        return False, "Username already taken"
    if teacher_pass != teacher_pass_confirm:
        return False, "Password doesn't match"
    
    try:
        create_teacher(teacher_username, teacher_pass, teacher_name)
        return True, "Sucessfully Created! Login Now"
    except Exception as e:
        return False, "Unexpected Error!"
    

def teacher_screen_register():
    c1, c2 = st.columns(2, vertical_alignment='center', gap='xxlarge')
    with c1:
        header_dashboard()
    with c2:
        if st.button("Go back to Home", type='secondary', key='loginbackbtn', shortcut="control+backspace"):
            st.session_state['login_type'] = None
            st.rerun()



    st.header('Register your teacher profile')

    st.space()
    st.space()

    
    teacher_username = st.text_input("Enter username", placeholder='vedantdixit')

    teacher_name = st.text_input("Enter name", placeholder='Vedant Dixit')

    teacher_pass = st.text_input("Enter password", type='password', placeholder="Enter password")

    teacher_pass_confirm = st.text_input("Confirm your password", type='password', placeholder="Enter password")

    st.divider()

    btnc1, btnc2 = st.columns(2)

    with btnc1:
        if st.button('Register now', icon=':material/passkey:', shortcut='control+enter', width='stretch'):
            success, message = register_teacher(teacher_username, teacher_name, teacher_pass, teacher_pass_confirm)
            if success:
                st.success(message)
                import time
                time.sleep(2)
                st.session_state.teacher_login_type = "login"
                st.rerun()
            else:
                st.error(message)


    with btnc2:
        if st.button('Login Instead', type="primary", icon=':material/passkey:', width='stretch'):
            st.session_state.teacher_login_type = 'login'

    footer_dashboard()
