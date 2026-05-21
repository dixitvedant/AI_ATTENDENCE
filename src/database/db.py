from src.database.config import supabase
import bcrypt

#Function for hashing password
def hash_pass(password):
    return bcrypt.hashpw(
    password.encode(),
    bcrypt.gensalt()).decode()

# Compare entered password with stored hashed password
def check_pass(password, hashed_password):
    return bcrypt.checkpw(
        password.encode(),
        hashed_password.encode()
    )


#Function for check teacher exists or not
def check_teacher_exists(username):
    #it means select table teachers from supabase and in that select column username,eq=equal to,means
    #suppose username=raj the check if raj is exist or not in column usernamea and execute 
    #the Query and stored result in response and compare if response.data is>0 means exist

    response=supabase.table("teachers").select("username").eq("username",username).execute()
    return len(response.data) > 0


#Function for create teacher
def create_teacher(username,password,name):
    #dictionary containing teacher details
    data={
        "username":username,

        #Store hashed password instead of plain text password
        "password":hash_pass(password),
        
        # Store teacher full name
        "name":name
    }

    # Insert teacher data into teachers table
    response=supabase.table("teachers").insert(data).execute()

    # Return inserted teacher record
    return response.data


def teacher_login(username, password):

    # Search teacher record using username
    response = supabase.table("teachers") \
        .select("*") \
        .eq("username", username) \
        .execute()

    # Check if teacher exists
    if response.data:

        # Get first matching teacher record
        teacher = response.data[0]

        # Verify entered password with stored hashed password
        if check_pass(password, teacher['password']):

            # Login successful
            return teacher

    # Login failed
    return None


#Function for Get all student information
def get_all_students():
    response=supabase.table('students').select('*').execute()
    return response.data

def create_student(new_name,face_embedding=None,voice_embedding=None):
    data={'name':new_name,'face_embedding':face_embedding,"voice_embedding":voice_embedding}
    response=supabase.table('students').insert(data).execute()
    return response

def create_subject(subject_code,name,section,teacher_id):
    data={"subject_code":subject_code,"name": name,"section":section,"teacher_id":teacher_id}
    response=supabase.table("subject").insert(data).execute()
    return response.data

def enroll_student_to_subject(student_id,subject_id):
    data={'student_id':student_id,"subject_id":subject_id}
    response=supabase.table('subject_students').insert(data).execute()
    return response.data


def unenroll_student_to_subject(student_id,subject_id):
    data={'student_id':student_id,"subject_id":subject_id}
    response=supabase.table('subject_students').delete().eq('student_id',student_id).eq('subject_id',subject_id).execute()
    return response.data

def get_student_subjects(student_id):
    response=supabase.table('subject_students').select('*,subject(*)').eq('student_id',student_id).execute()
    return response.data

def get_student_attendence(student_id):
    response=supabase.table('attendence_logs').select('*,subject(*)').eq('student_id',student_id).execute()
    return response.data

def create_attendence(

    logs,
    session_id
):

    for log in logs:

        log[
            'session_id'
        ] = session_id

    supabase.table(
        'attendence_logs'
    ).insert(
        logs
    ).execute()


def get_attendence_for_teacher(
    teacher_id
):

    response = (

        supabase
        .table(
            'attendence_logs'
        )
        .select(
            """
            *,
            subject!inner(*),
            students(*)
            """
        )
        .eq(
            'subject.teacher_id',
            teacher_id
        )
        .execute()
    )

    return response.data

def update_subject(
    subject_id,
    name,
    section
):

    supabase.table(
        'subject'
    ).update({

        'name':
            name,

        'section':
            section

    }).eq(

        'subject_id',
        subject_id

    ).execute()

def delete_subject(
    subject_id
):

    supabase.table(
        'subject'
    ).delete().eq(

        'subject_id',
        subject_id

    ).execute()
    

def get_students_for_subject(
    subject_id
):

    res = (

        supabase
        .table(
            'subject_students'
        )
        .select(
            'students(*)'
        )
        .eq(
            'subject_id',
            subject_id
        )
        .execute()
    )

    return [

        s[
            'students'
        ]

        for s in res.data
    ]

def create_attendence_session(

    subject_id,
    teacher_id,
    total_students,
    present_students
):

    res = (

        supabase
        .table(
            'attendence_sessions'
        )
        .insert({

            'subject_id':
                subject_id,

            'teacher_id':
                teacher_id,

            'total_students':
                total_students,

            'present_students':
                present_students
        })
        .execute()
    )

    return res.data[0]


def get_teacher_sessions(

    teacher_id
):

    response = (

        supabase
        .table(
            'attendence_sessions'
        )
        .select(

            "*,subject(*)"

        )
        .eq(
            'teacher_id',
            teacher_id
        )
        .order(

            'lecture_time',

            desc=True
        )
        .execute()
    )

    return response.data


def delete_lecture_session(

    session_id
):

    supabase.table(

        'attendence_sessions'

    ).delete().eq(

        'session_id',

        session_id

    ).execute()


def get_lecture_logs(

    session_id
):

    response = (

        supabase
        .table(
            'attendence_logs'
        )
        .select(

            "*,students(*)"

        )
        .eq(
            'session_id',
            session_id
        )
        .execute()
    )

    return response.data

def update_lecture_log(

    id,
    is_present,
    session_id
):

    # =====================================
    # UPDATE LOG
    # =====================================
    supabase.table(

        'attendence_logs'

    ).update({

        'is_present':
            is_present

    }).eq(

        'id',

        id

    ).execute()

    # =====================================
    # RECALCULATE SESSION
    # =====================================
    logs = supabase.table(

        'attendence_logs'

    ).select(

        'is_present'

    ).eq(

        'session_id',

        session_id

    ).execute()

    total = len(
        logs.data
    )

    present = sum(

        1

        for l in logs.data

        if l[
            'is_present'
        ]
    )

    # =====================================
    # UPDATE SESSION COUNTS
    # =====================================
    supabase.table(

        'attendence_sessions'

    ).update({

        'total_students':
            total,

        'present_students':
            present

    }).eq(

        'session_id',

        session_id

    ).execute()
# Function to get all subjects created by a specific teacher
def get_teacher_subject(teacher_id):

    # Fetch data from 'subject' table
    # Also fetch:
    # 1. subject_students(count) -> number of students
    # 2. attendance_logs(timestamp) -> attendence session timestamps
    response = supabase.table('subject') \
        .select("*, subject_students(count), attendence_logs(timestamp)") \
        .eq("teacher_id",teacher_id) \
        .execute()

    # Store fetched subject records
    subjects = response.data

    # Loop through every subject
    for sub in subjects:

        # Get total number of students in the subject
        # If no students exist, set count to 0
        sub['total_students'] = (
            sub.get("subject_students", [{}])[0].get('count', 0)
            if sub.get('subject_students')
            else 0
        )

        # Get attendance log records
        attendence = sub.get('attendence_logs', [])

        # Count unique attendance sessions using timestamps
        unique_sessions = len(
            set(log['timestamp'] for log in attendence)
        )

        # Store total classes conducted
        sub['total_classes'] = unique_sessions

        # Remove unnecessary nested data from final response
        sub.pop('subject_students', None)
        sub.pop('attendence_logs', None)

    # Return cleaned subject data
    return subjects