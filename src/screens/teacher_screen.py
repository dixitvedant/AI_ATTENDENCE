import streamlit as st
from datetime import timedelta

from src.ui.base_layout import style_background_dashboard, style_base_layout
from src.components.header import header_dashboard
from src.components.footer import footer_dashboard
from src.components.subject_card import subject_card
from src.database.db import check_teacher_exists, create_teacher, teacher_login, get_teacher_subject,get_attendence_for_teacher
from src.components.dialog_create_subject import create_subject_dialog
from src.components.dialog_share_subject import share_subject_dialog
from src.components.dialog_add_photo import add_photos_dialog
from src.screens.ai_screen import ai_chat_widget
from src.pipelines.face_pipeline import predict_attendence
from src.components.dialog_attendence_results import show_attendence_result
from src.components.dialog_edit_subject import edit_subject_dialog
from src.components.dialog_delete_subject import delete_subject_dialog
from src.components.dialog_view_students import view_students_dialog
from src.database.db import get_teacher_sessions
from src.components.dialog_delete_session import delete_lecture_dialog
from src.components.dialog_edit_session import edit_lecture_dialog
from src.components.dialog_view_session import view_lecture_dialog


# from src.dialogs.view_students_dialog import view_students_dialog

import numpy as np

from datetime import datetime

import pandas as pd

from src.database.config import supabase
import pandas as pd
import streamlit as st

from datetime import datetime
from io import BytesIO

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table
)

from reportlab.lib.styles import (
    getSampleStyleSheet
)

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

    ai_chat_widget()



def teacher_dashboard():

    teacher_data = (
        st.session_state.teacher_data
    )

    # =====================================
    # HEADER
    # =====================================
    c1, c2 = st.columns(

        2,

        vertical_alignment='center',

        gap='xxlarge'
    )

    with c1:

        header_dashboard()

    with c2:

        st.subheader(

            f"Welcome, "

            f"{teacher_data['name']}"
        )

        if st.button(

            "Logout",

            type='secondary',

            key='loginbackbtn',

            shortcut=
                "control+backspace"
        ):

            st.session_state[
                'is_logged_in'
            ] = False

            del st.session_state[
                'teacher_data'
            ]

            st.rerun()

    st.space()

    # =====================================
    # DEFAULT TAB
    # =====================================
    if (

        "current_teacher_tab"

        not in

        st.session_state
    ):

        st.session_state[
            'current_teacher_tab'
        ] = 'take_attendance'

    # =====================================
    # TAB BUTTONS
    # =====================================
    tab1, tab2, tab3, tab4 = (

        st.columns(4)
    )

    # =====================================
    # TAKE ATTENDANCE
    # =====================================
    with tab1:

        type1 = (

            "primary"

            if

            st.session_state[
                'current_teacher_tab'
            ]

            ==

            'take_attendance'

            else

            "tertiary"
        )

        if st.button(

            'Take Attendance',

            type=type1,

            width='stretch',

            icon=
                ':material/ar_on_you:'
        ):

            st.session_state[
                'current_teacher_tab'
            ] = 'take_attendance'

            st.rerun()

    # =====================================
    # MANAGE SUBJECTS
    # =====================================
    with tab2:

        type2 = (

            "primary"

            if

            st.session_state[
                'current_teacher_tab'
            ]

            ==

            'manage_subjects'

            else

            "tertiary"
        )

        if st.button(

            'Manage Subjects',

            type=type2,

            width='stretch',

            icon=
                ':material/book_ribbon:'
        ):

            st.session_state[
                'current_teacher_tab'
            ] = 'manage_subjects'

            st.rerun()

    # =====================================
    # ATTENDANCE RECORDS
    # =====================================
    with tab3:

        type3 = (

            "primary"

            if

            st.session_state[
                'current_teacher_tab'
            ]

            ==

            'attendence_records'

            else

            "tertiary"
        )

        if st.button(

            'Attendance Records',

            type=type3,

            width='stretch',

            icon=
                ':material/cards_stack:'
        ):

            st.session_state[
                'current_teacher_tab'
            ] = 'attendence_records'

            st.rerun()

    # =====================================
    # LECTURE MANAGEMENT
    # =====================================
    with tab4:

        type4 = (

            "primary"

            if

            st.session_state[
                'current_teacher_tab'
            ]

            ==

            'lecture_management'

            else

            "tertiary"
        )

        if st.button(

            'Lecture Management',

            type=type4,

            width='stretch',

            icon=
                ':material/event_note:'
        ):

            st.session_state[
                'current_teacher_tab'
            ] = 'lecture_management'

            st.rerun()

    st.divider()

    # =====================================
    # TAB ROUTING
    # =====================================
    if (

        st.session_state[
            'current_teacher_tab'
        ]

        ==

        "take_attendance"
    ):

        teacher_tab_take_attendence()

    elif (

        st.session_state[
            'current_teacher_tab'
        ]

        ==

        "manage_subjects"
    ):

        teacher_tab_manage_subjects()

    elif (

        st.session_state[
            'current_teacher_tab'
        ]

        ==

        "attendence_records"
    ):

        teacher_tab_attendence_records()

    elif (

        st.session_state[
            'current_teacher_tab'
        ]

        ==

        "lecture_management"
    ):

        teacher_tab_lecture_management()

    # =====================================
    # FOOTER
    # =====================================
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

    teacher_id = (
        st.session_state
        .teacher_data[
            'teacher_id'
        ]
    )

    # =====================================
    # HEADER
    # =====================================
    col1, col2 = st.columns(2)

    with col1:

        st.header(
            'Manage Subjects'
        )

    with col2:

        if st.button(

            'Create New Subject',

            width='stretch'
        ):

            create_subject_dialog(
                teacher_id
            )

    # =====================================
    # GET SUBJECTS
    # =====================================
    subjects = (
        get_teacher_subject(
            teacher_id
        )
    )

# =====================================
# DASHBOARD
    # =====================================
    if subjects:

        total_subjects = len(
            subjects
        )

        total_students = sum(

            s[
                'total_students'
            ]

            for s in subjects
        )

        total_classes = sum(

            s[
                'total_classes'
            ]

            for s in subjects
        )

        st.subheader(
            "Dashboard"
        )

        d1,d2,d3 = st.columns(
            3,
            gap='medium'
        )

        with d1:

            st.metric(

                label=
                    "📚 Subjects",

                value=
                    total_subjects,

                border=True
            )

        with d2:

            st.metric(

                label=
                    "👨‍🎓 Students",

                value=
                    total_students,

                border=True
            )

        with d3:

            st.metric(

                label=
                    "🕒 Classes",

                value=
                    total_classes,

                border=True
            )

        st.divider()

    # =====================================
    # SHOW SUBJECTS
    # =====================================
    if subjects:

        for sub in subjects:

            stats = [

                (
                    "🫂",
                    "Students",
                    sub[
                        'total_students'
                    ]
                ),

                (
                    "🕰️",
                    "Classes",
                    sub[
                        'total_classes'
                    ]
                )
            ]

            # =====================================
            # FOOTER CALLBACK
            # =====================================
            def share_btn(

                subject_name=
                    sub['name'],

                subject_code=
                    sub['subject_code'],

                subject_id=
                    sub['subject_id'],

                current_sub=
                    sub
            ):

                c1,c2,c3,c4 = st.columns(4)

                # -----------------------------
                # SHARE
                # -----------------------------
                with c1:

                    if st.button(

                        "Share",

                        key=
                            f"share_{subject_code}",

                        icon=
                            ":material/share:",

                        use_container_width=
                            True
                    ):

                        share_subject_dialog(

                            subject_name,

                            subject_code
                        )

                # -----------------------------
                # STUDENTS
                # -----------------------------
                with c2:

                    if st.button(

                        "Students",

                        key=
                            f"students_{subject_code}",

                        icon=
                            ":material/groups:",

                        use_container_width=
                            True
                    ):

                        view_students_dialog(
                            subject_id
                        )

                # -----------------------------
                # EDIT
                # -----------------------------
                with c3:

                    if st.button(

                        "Edit",

                        key=
                            f"edit_{subject_code}",

                        icon=
                            ":material/edit:",

                        use_container_width=
                            True
                    ):

                        edit_subject_dialog(
                            current_sub
                        )

                # -----------------------------
                # DELETE
                # -----------------------------
                with c4:

                    if st.button(

                        "Delete",

                        key=
                            f"delete_{subject_code}",

                        icon=
                            ":material/delete:",

                        use_container_width=
                            True
                    ):

                        delete_subject_dialog(
                            subject_id
                        )

                st.space()

            # =====================================
            # SUBJECT CARD
            # =====================================
            subject_card(

                name=
                    sub[
                        'name'
                    ],

                code=
                    sub[
                        'subject_code'
                    ],

                section=
                    sub[
                        'section'
                    ],

                stats=
                    stats,

                footer_callback=
                    share_btn
            )

    else:

        st.info(
            "NO SUBJECTS FOUND. CREATE ONE ABOVE"
        )



def teacher_tab_attendence_records():

    st.header(
        'Attendance Records'
    )

    teacher_id = (
        st.session_state
        .teacher_data[
            'teacher_id'
        ]
    )

    records = (
        get_attendence_for_teacher(
            teacher_id
        )
    )

    if not records:

        st.info(
            "No attendance records found"
        )
        return

    data = []

    # =====================================
    # BUILD DATA
    # =====================================
    for r in records:

        ts = r.get(
            'timestamp'
        )

        if ts:

            dt = (
                datetime
                .fromisoformat(
                    ts.replace(
                        "Z",
                        "+00:00"
                    )
                )
            )

            formatted_time = (
                dt.strftime(
                    "%Y-%m-%d %I:%M:%S %p"
                )
            )

            ts_group = (
                dt.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            date_only = (
                dt.date()
            )

            month_year = (
                dt.strftime(
                    "%B %Y"
                )
            )

        else:

            formatted_time = (
                "N/A"
            )

            ts_group = None
            date_only = None
            month_year = None

        data.append({

            "ts_group":
                ts_group,

            "Date":
                date_only,

            "Month":
                month_year,

            "Time":
                formatted_time,

            "Subject":
                r[
                    'subject'
                ][
                    'name'
                ],

            "Subject Code":
                r[
                    'subject'
                ][
                    'subject_code'
                ],

            "Student Name":
                r[
                    'students'
                ][
                    'name'
                ],

            "Student ID":
                r[
                    'students'
                ][
                    'student_id'
                ],

            "is_present":
                bool(
                    r.get(
                        'is_present',
                        False
                    )
                )
        })

    # =====================================
    # DATAFRAME
    # =====================================
    df = pd.DataFrame(
        data
    )

    if df.empty:

        st.info(
            "No data available"
        )
        return

    # =====================================
    # SUBJECT FILTER
    # =====================================
    subjects = sorted(

        df[
            'Subject'
        ]
        .dropna()
        .unique()
    )

    selected_subject = st.selectbox(

        "Select Subject",

        subjects
    )

    filtered_df = (

        df[
            df[
                'Subject'
            ]

            ==

            selected_subject
        ]
    )

    # =====================================
    # DATE FILTER
    # =====================================
    st.subheader(
        "Date Filter"
    )

    col1, col2 = (
        st.columns(2)
    )

    with col1:

        start_date = (
            st.date_input(

                "From",

                filtered_df[
                    'Date'
                ].min()
            )
        )

    with col2:

        end_date = (
            st.date_input(

                "To",

                filtered_df[
                    'Date'
                ].max()
            )
        )

    filtered_df = (

        filtered_df[

            (
                filtered_df[
                    'Date'
                ]

                >=

                start_date
            )

            &

            (
                filtered_df[
                    'Date'
                ]

                <=

                end_date
            )
        ]
    )

    # =====================================
    # MONTH FILTER
    # =====================================
    months = sorted(

        filtered_df[
            'Month'
        ]
        .dropna()
        .unique()
    )

    selected_month = st.selectbox(

        "Monthly Filter",

        ["All"]
        +
        list(months)
    )

    if (
        selected_month
        !=
        "All"
    ):

        filtered_df = (

            filtered_df[

                filtered_df[
                    'Month'
                ]

                ==

                selected_month
            ]
        )

    # =====================================
    # SEARCH
    # =====================================
    search = st.text_input(
        "Search Student Name / ID"
    )

    # =====================================
    # STUDENT SUMMARY PREP
    # =====================================
    student_summary = (

        filtered_df
        .groupby(
            [
                'Student ID',
                'Student Name'
            ]
        )
        .agg(

            Present_Count=(
                'is_present',
                'sum'
            ),

            Total_Classes=(
                'is_present',
                'count'
            )
        )
        .reset_index()
    )

    student_summary[
        'Absent_Count'
    ] = (

        student_summary[
            'Total_Classes'
        ]

        -

        student_summary[
            'Present_Count'
        ]
    )

    student_summary[
        'Attendance_Num'
    ] = (

        student_summary[
            'Present_Count'
        ]

        /

        student_summary[
            'Total_Classes'
        ]

    ) * 100

    student_summary[
        'Attendance %'
    ] = (

        student_summary[
            'Attendance_Num'
        ]

    ).round(2).astype(str) + "%"

        # =====================================
    # SEARCH FILTER
    # =====================================
    if search:

        student_summary = (

            student_summary[

                student_summary[
                    'Student Name'
                ]
                .str.contains(

                    search,

                    case=False,

                    na=False
                )

                |

                student_summary[
                    'Student ID'
                ]
                .astype(str)
                .str.contains(

                    search,

                    case=False,

                    na=False
                )
            ]
        )

    # =====================================
    # LOW ATTENDANCE
    # =====================================
    low_attendance = (

        student_summary[

            student_summary[
                'Attendance_Num'
            ]

            <

            75
        ]
    )

    # =====================================
    # DASHBOARD TOP
    # =====================================
    total_students = len(
        student_summary
    )

    total_classes = 0

    if not student_summary.empty:

        total_classes = (

            student_summary[
                'Total_Classes'
            ]
            .max()
        )

    avg_attendance = 0

    if not student_summary.empty:

        avg_attendance = round(

            student_summary[
                'Attendance_Num'
            ]
            .mean(),

            2
        )

    low_count = len(
        low_attendance
    )

    st.subheader(
        "Attendance Dashboard"
    )

    col1,col2,col3,col4 = st.columns(4)

    with col1:

        st.metric(
            "Students",
            total_students
        )

    with col2:

        st.metric(
            "Classes",
            total_classes
        )

    with col3:

        st.metric(
            "Average %",
            f"{avg_attendance}%"
        )

    with col4:

        st.metric(
            "Below 75%",
            low_count
        )

    st.divider()

    # =====================================
    # LOW ATTENDANCE TABLE
    # =====================================
    if not low_attendance.empty:

        st.warning(
            "Students below 75% attendance"
        )

        st.dataframe(

            low_attendance[
                [
                    'Student ID',
                    'Student Name',
                    'Attendance %'
                ]
            ],

            width='stretch',

            hide_index=True
        )

    # =====================================
    # CLASS SUMMARY
    # =====================================
    summary = (

        filtered_df
        .groupby(
            [
                'ts_group',
                'Time',
                'Subject',
                'Subject Code'
            ]
        )
        .apply(

            lambda g:

            pd.Series({

                'Present_Count':

                    g[
                        'is_present'
                    ]
                    .sum(),

                'Total_Count':

                    len(g)
            })
        )
        .reset_index()
    )

    summary[
        'Attendance Stats'
    ] = (

        "✅ "

        +

        summary[
            'Present_Count'
        ]
        .astype(str)

        +

        " / "

        +

        summary[
            'Total_Count'
        ]
        .astype(str)

        +

        " Students"
    )

    display_df = (

        summary
        .sort_values(

            by=
                'ts_group',

            ascending=
                False
        )[
            [
                'Time',
                'Subject',
                'Subject Code',
                'Attendance Stats'
            ]
        ]
    )

    st.subheader(

        f"{selected_subject} "
        "Class Attendance"
    )

    st.dataframe(

        display_df,

        width='stretch',

        hide_index=True
    )

        # =====================================
    # STUDENT REPORT
    # =====================================
    st.subheader(

        f"{selected_subject} "
        "Student Attendance Summary"
    )

    st.dataframe(

        student_summary[
            [
                'Student ID',
                'Student Name',
                'Present_Count',
                'Absent_Count',
                'Total_Classes',
                'Attendance %'
            ]
        ],

        width='stretch',

        hide_index=True
    )

    # # =====================================
    # # BAR CHART
    # # =====================================
    # st.subheader(
    #     "Attendance Chart"
    # )

    # if not student_summary.empty:

    #     chart_df = (

    #         student_summary
    #         .set_index(
    #             'Student Name'
    #         )[
    #             'Present_Count'
    #         ]
    #     )

    #     st.bar_chart(
    #         chart_df
    #     )

    # st.divider()

    # =====================================
    # DOWNLOAD REPORTS
    # =====================================
    st.subheader(
        "Download Reports"
    )

    col1,col2,col3 = st.columns(3)

    # =====================================
    # CSV
    # =====================================
    csv = (

        student_summary
        .to_csv(
            index=False
        )
    )

    with col1:

        st.download_button(

            label=
                "CSV",

            data=
                csv,

            file_name=
                f"{selected_subject}_attendance.csv",

            mime=
                "text/csv",

            use_container_width=True
        )

    # =====================================
    # EXCEL
    # =====================================
    excel_buffer = (
        BytesIO()
    )

    with pd.ExcelWriter(

        excel_buffer,

        engine=
            'openpyxl'

    ) as writer:

        student_summary.to_excel(

            writer,

            sheet_name=
                'Attendance',

            index=
                False
        )

    excel_data = (
        excel_buffer
        .getvalue()
    )

    with col2:

        st.download_button(

            label=
                "Excel",

            data=
                excel_data,

            file_name=
                f"{selected_subject}_attendance.xlsx",

            mime=
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",

            use_container_width=True
        )

    # =====================================
    # PDF
    # =====================================
    pdf_buffer = (
        BytesIO()
    )

    doc = (
        SimpleDocTemplate(
            pdf_buffer
        )
    )

    styles = (
        getSampleStyleSheet()
    )

    elements = []

    elements.append(

        Paragraph(

            f"{selected_subject} Attendance Report",

            styles[
                'Title'
            ]
        )
    )

    elements.append(
        Spacer(1,12)
    )

    table_data = [[

        'Student ID',
        'Student Name',
        'Present',
        'Absent',
        'Total',
        '%'
    ]]

    for _, row in (
        student_summary
        .iterrows()
    ):

        table_data.append([

            str(
                row[
                    'Student ID'
                ]
            ),

            str(
                row[
                    'Student Name'
                ]
            ),

            str(
                row[
                    'Present_Count'
                ]
            ),

            str(
                row[
                    'Absent_Count'
                ]
            ),

            str(
                row[
                    'Total_Classes'
                ]
            ),

            str(
                row[
                    'Attendance %'
                ]
            )
        ])

    table = Table(
        table_data
    )

    elements.append(
        table
    )

    doc.build(
        elements
    )

    pdf_data = (
        pdf_buffer
        .getvalue()
    )

    with col3:

        st.download_button(

            label=
                "PDF",

            data=
                pdf_data,

            file_name=
                f"{selected_subject}_attendance.pdf",

            mime=
                "application/pdf",

            use_container_width=True
        )

#Session managemenr

def teacher_tab_lecture_management():

    st.header(
        "Lecture Management"
    )

    teacher_id = (

        st.session_state
        .teacher_data[
            'teacher_id'
        ]
    )

    sessions = (

        get_teacher_sessions(
            teacher_id
        )
    )

    if not sessions:

        st.info(
            "No lectures found"
        )
        return

    # =====================================
    # LECTURE CARDS
    # =====================================
    for s in sessions:

        # =====================================
        # UTC -> IST (+5:30)
        # =====================================
        dt = datetime.fromisoformat(

            s[
                'lecture_time'
            ].replace(
                "Z",
                "+00:00"
            )
        )

        # Add 5 hour 30 min
        dt = dt + timedelta(

            hours=5,

            minutes=30
        )

        lecture_time = dt.strftime(

            "%Y-%m-%d %I:%M:%S %p"
        )

        lecture_time = dt.strftime(

            "%d %b %Y %I:%M %p"
        )

        present = (

            s[
                'present_students'
            ]
        )

        total = (

            s[
                'total_students'
            ]
        )

        # =====================================
        # CARD
        # =====================================
        with st.container(
            border=True
        ):

            c1, c2 = st.columns(
                [3, 2],
                vertical_alignment='center'
            )

            # =====================================
            # LEFT SIDE
            # =====================================
            with c1:

                st.subheader(

                    s[
                        'subject'
                    ][
                        'name'
                    ]
                )

                st.caption(
                    lecture_time
                )

                st.write(

                    f"✅ "
                    f"{present}"
                    f" / "
                    f"{total}"
                    f" Students"
                )

            # =====================================
            # RIGHT SIDE BUTTONS
            # =====================================
            with c2:

                v, e, d = st.columns(
                    3
                )

                # =====================================
                # VIEW
                # =====================================
                with v:

                   if st.button(

                    "View",

                    key=f"view_{
                        s['session_id']
                    }"
                ):

                    view_lecture_dialog(
                        s
                    )

                # =====================================
                # EDIT
                # =====================================
                with e:

                    if st.button(

                        "Edit",

                        key=
                            f"edit_{
                                s['session_id']
                            }",

                        use_container_width=
                            True
                    ):

                        edit_lecture_dialog(

                            s[
                                'session_id'
                            ]
                        )

                # =====================================
                # DELETE
                # =====================================
                with d:

                    if st.button(

                        "Del❌",

                        key=
                            f"delete_{
                                s['session_id']
                            }",

                        use_container_width=
                            True,

                        type=
                            'secondary'
                    ):

                        delete_lecture_dialog(

                            s[
                                'session_id'
                            ]
                        )

        st.space()

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