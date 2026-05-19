import streamlit as st
from PIL import Image


@st.dialog("Capture or Upload Photos")
def add_photos_dialog():

    st.write("Add classroom photos to scan for attendance")

    # =====================================================
    # Initialize session states
    # =====================================================
    if 'photo_tab' not in st.session_state:
        st.session_state.photo_tab = 'camera'

    if 'attendence_images' not in st.session_state:
        st.session_state.attendence_images = []

    if 'uploaded_file_names' not in st.session_state:
        st.session_state.uploaded_file_names = set()

    # =====================================================
    # TAB BUTTONS
    # =====================================================
    t1, t2 = st.columns(2)

    with t1:

        type_camera = (
            "primary"
            if st.session_state.photo_tab == 'camera'
            else 'tertiary'
        )

        if st.button(
            'Camera',
            type=type_camera,
            width='stretch'
        ):

            st.session_state.photo_tab = 'camera'

    with t2:

        type_upload = (
            "primary"
            if st.session_state.photo_tab == 'upload'
            else 'tertiary'
        )

        if st.button(
            'Upload Photos',
            type=type_upload,
            width='stretch'
        ):

            st.session_state.photo_tab = 'upload'

    # =====================================================
    # CAMERA MODE
    # =====================================================
    if st.session_state.photo_tab == 'camera':

        cam_photo = st.camera_input(
            'Take Snapshot',
            key='dialog_cam'
        )

        if cam_photo is not None:

            # Prevent duplicate camera images
            if cam_photo.name not in st.session_state.uploaded_file_names:

                image = Image.open(cam_photo)

                st.session_state.attendence_images.append(image)

                st.session_state.uploaded_file_names.add(cam_photo.name)

                st.toast('Photo Captured Successfully')
                st.rerun()

    # =====================================================
    # UPLOAD MODE
    # =====================================================
    if st.session_state.photo_tab == 'upload':

        uploaded_files = st.file_uploader(
            'Choose image files',
            type=['jpg', 'png', 'jpeg'],
            accept_multiple_files=True,
            key='dialog_upload'
        )

        if uploaded_files:

            added_count = 0

            for f in uploaded_files:

                # Avoid duplicate uploads
                if f.name not in st.session_state.uploaded_file_names:

                    image = Image.open(f)

                    st.session_state.attendence_images.append(image)

                    st.session_state.uploaded_file_names.add(f.name)

                    added_count += 1

            if added_count > 0:
                st.toast(f'{added_count} Photo(s) Uploaded Successfully')
                st.rerun()

    # =====================================================
    # IMAGE PREVIEW
    # =====================================================
    if st.session_state.attendence_images:

        st.divider()

        st.subheader("Added Photos")

        cols = st.columns(3)

        for idx, img in enumerate(st.session_state.attendence_images):

            with cols[idx % 3]:

                st.image(
                    img,
                    caption=f'Photo {idx + 1}',
                    width='stretch'
                )

    # =====================================================
    # ACTION BUTTONS
    # =====================================================
    st.divider()

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            'Clear All',
            type='tertiary',
            width='stretch'
        ):

            st.session_state.attendence_images = []

            st.session_state.uploaded_file_names = set()

            st.toast("All Photos Cleared")

            st.rerun()

    with c2:

        if st.button(
            'Done',
            type='primary',
            width='stretch'
        ):

            st.rerun()