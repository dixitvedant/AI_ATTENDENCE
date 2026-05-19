# #Import dlib library for face detection and face recognition
# import dlib

# #Import NumPy for numerical operations and arrays
# import numpy as np

# #Import pre-trained face recognition models
# import face_recognition_models

# #Import Support Vector Classifier from sklearn
# from sklearn.svm import SVC

# #Import Streamlit
# import streamlit as st

# #Import database function to fetch all students
# from src.database.db import get_all_students


# #Cache Dlib models so they load only once
# @st.cache_resource
# def load_dlib_models():

#     #Load frontal face detector
#     detector = dlib.get_frontal_face_detector() 

#     #Load face landmark predictor model
#     sp = dlib.shape_predictor(
#         face_recognition_models.pose_predictor_model_location()
#     )

#     #Load face recognition embedding model
#     facerec = dlib.face_recognition_model_v1(
#         face_recognition_models.face_recognition_model_location()
#     )

#     #Return all loaded models
#     return detector, sp, facerec


# #Function to generate face embeddings from image
# def get_face_embeddings(image_np):

#     #Load Dlib models
#     detector, sp, facerec = load_dlib_models()

#     #Detect faces in image
#     faces = detector(image_np, 1)

#     #Empty list to store embeddings
#     encodings= []

#     #Loop through all detected faces
#     for face in faces:

#         #Detect facial landmarks
#         shape = sp(image_np, face)

#         #Generate 128-dimensional face embedding
#         face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1)

#         #Convert embedding into NumPy array and store
#         encodings.append(np.array(face_descriptor))

#     #Return all embeddings
#     return encodings


# #Cache trained model
# @st.cache_resource
# def get_trained_model():

#     #Training feature list
#     X = []

#     #Training label list
#     y = []

#     #Fetch all students from database
#     student_db = get_all_students()

#     #If no students found return None
#     if not student_db:
#         return None
    
#     #Loop through every student
#     for student in student_db:

#         #Get stored face embedding
#         embedding = student.get('face_embedding')

#         #If embedding exists
#         if embedding:

#             #Add embedding into training data
#             X.append(np.array(embedding))

#             #Add student id as label
#             y.append(student.get('student_id'))

#     #If no embeddings found
#     if len(X) ==0:
#         return 0
    
#     #Create SVM classifier
#     clf = SVC(
#         kernel='linear',
#         probability=True,
#         class_weight='balanced'
#     )

#     #Train classifier
#     try:
#         clf.fit(X, y)

#     #Handle training error
#     except ValueError:
#         pass

#     #Return classifier and training data
#     return {
#         'clf': clf,
#         'X':X,
#         "y":y
#     }


# #Function to retrain classifier
# def train_classifier():

#     #Clear Streamlit cache
#     st.cache_resource.clear()

#     #Train model again
#     model_data = get_trained_model()

#     #Return True/False
#     return bool(model_data)


# #Function to predict attendance using face recognition
# def predict_attendance(class_image_np):

#     #Generate embeddings from captured image
#     encodings = get_face_embeddings(class_image_np)

#     #Dictionary to store detected students
#     detected_student = {}

#     #Load trained model
#     model_data = get_trained_model()

#     #If model not available
#     if not model_data:

#         #Return empty results
#         return detected_student, [], len(encodings)
    
#     #Extract classifier
#     clf = model_data['clf']

#     #Extract training embeddings
#     X_train = model_data['X']

#     #Extract training labels
#     y_train = model_data['y']

#     #Get all unique student IDs
#     all_students = sorted(list(set(y_train)))

#     #Loop through every detected face encoding
#     for encoding in encodings:

#         #If more than one student exists
#         if len(all_students)>= 2:

#             #Predict student ID using SVM
#             predicted_id= int(clf.predict([encoding])[0])

#         else:
#             #If only one student exists directly assign
#             predicted_id = int(all_students[0])

#         #Get embedding of predicted student
#         student_embedding = X_train[y_train.index(predicted_id)]

#         #Calculate Euclidean distance between embeddings
#         best_match_score = np.linalg.norm(
#             student_embedding - encoding
#         )

#         #Recognition threshold
#         resemblance_threshold = 0.6

#         #If similarity is good enough
#         if best_match_score <= resemblance_threshold:

#             #Mark student as detected
#             detected_student[predicted_id] = True

#     #Return detected students,
#     #all trained student IDs,
#     #and number of detected faces
#     return detected_student, all_students, len(encodings)
# ============================================================
# FACE RECOGNITION ATTENDANCE SYSTEM
# FIXED VERSION
# ============================================================

# Import dlib library for face detection and recognition
import dlib

# Import NumPy
import numpy as np

# Import pretrained face recognition models
import face_recognition_models

# Import Streamlit
import streamlit as st

# Import database function
from src.database.db import get_all_students


# ============================================================
# LOAD DLIB MODELS
# ============================================================

@st.cache_resource
def load_dlib_models():

    # Face detector
    detector = dlib.get_frontal_face_detector()

    # Landmark predictor
    sp = dlib.shape_predictor(
        face_recognition_models.pose_predictor_model_location()
    )

    # Face embedding model
    facerec = dlib.face_recognition_model_v1(
        face_recognition_models.face_recognition_model_location()
    )

    return detector, sp, facerec


# ============================================================
# GENERATE FACE EMBEDDINGS
# ============================================================

def get_face_embeddings(image_np):

    detector, sp, facerec = load_dlib_models()

    # Detect faces
    faces = detector(image_np, 1)

    encodings = []

    # Generate embedding for every face
    for face in faces:

        # Facial landmarks
        shape = sp(image_np, face)

        # 128D embedding
        face_descriptor = facerec.compute_face_descriptor(
            image_np,
            shape,
            1
        )

        encodings.append(np.array(face_descriptor))

    return encodings


# ============================================================
# LOAD ALL STUDENT EMBEDDINGS
# ============================================================

@st.cache_resource
def load_student_embeddings():

    # Fetch students from database
    student_db = get_all_students()

    # Dictionary:
    # {
    #   student_id : [embedding1, embedding2]
    # }
    student_embeddings = {}

    # No students
    if not student_db:
        return {}

    # Process every student
    for student in student_db:

        student_id = student.get("student_id")

        embedding = student.get("face_embedding")

        # Skip invalid embeddings
        if not embedding:
            continue

        embedding_np = np.array(embedding)

        # Create list if not exists
        if student_id not in student_embeddings:
            student_embeddings[student_id] = []

        # Store embedding
        student_embeddings[student_id].append(embedding_np)

    return student_embeddings


# ============================================================
# RETRAIN / RELOAD MODEL
# ============================================================

def train_classifier():

    # Clear Streamlit cache
    st.cache_resource.clear()

    # Reload embeddings
    load_student_embeddings()

    return True


# ============================================================
# FACE RECOGNITION
# ============================================================

def predict_attendence(class_image_np):

    # Generate embeddings from classroom image
    detected_face_embeddings = get_face_embeddings(class_image_np)

    # Store recognized students
    detected_students = {}

    # Load database embeddings
    student_embeddings_db = load_student_embeddings()

    # No students registered
    if not student_embeddings_db:
        return detected_students, [], len(detected_face_embeddings)

    # All registered students
    all_students = list(student_embeddings_db.keys())

    # ========================================================
    # RECOGNITION LOOP
    # ========================================================

    for detected_embedding in detected_face_embeddings:

        best_match_student = None

        # Start with large distance
        best_match_distance = 999

        # Compare against every student
        for student_id, stored_embeddings in student_embeddings_db.items():

            # Compare against every embedding of student
            for stored_embedding in stored_embeddings:

                # Euclidean distance
                distance = np.linalg.norm(
                    stored_embedding - detected_embedding
                )

                # Store minimum distance
                if distance < best_match_distance:

                    best_match_distance = distance
                    best_match_student = student_id

        # ====================================================
        # THRESHOLD CHECK
        # ====================================================

        # STRICT threshold
        RECOGNITION_THRESHOLD = 0.45

        # Face matched successfully
        if best_match_distance < RECOGNITION_THRESHOLD:

            detected_students[int(best_match_student)] = True

    # ========================================================
    # RETURN RESULTS
    # ========================================================

    return (
        detected_students,
        all_students,
        len(detected_face_embeddings)
    )