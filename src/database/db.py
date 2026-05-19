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

def create_attendence(logs):
    response=supabase.table('attendence_logs').insert(logs).execute()
    return response.data

def get_attendance_for_teacher(teacher_id):
    response=supabase.table('attendence_logs').select("*,subject!inner(*)").eq('subject.teacher_id',teacher_id).execute()
    return response.data



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