# Import Streamlit library
import streamlit as st

# Library used to generate QR codes
import segno

# Used for storing QR image in memory
import io


# =========================================================
# SHARE SUBJECT DIALOG
# =========================================================
# This creates a popup dialog in Streamlit
#
# Parameters:
# name         -> Subject/Class name
# subject_code -> Unique joining code
# =========================================================
@st.dialog("Share Class Link")
def share_subject_dialog(name, subject_code):

    # -----------------------------------------------------
    # Base URL of Streamlit application
    # -----------------------------------------------------
    # localhost means app is running on your local computer
    # Later you can replace this with:
    # https://yourdomain.com
    # -----------------------------------------------------
    app_domain = "snapclass-master.streamlit.app"

    # -----------------------------------------------------
    # Create join URL
    # Example:
    # http://localhost:8501/?join-code=ABC123
    # -----------------------------------------------------
    join_url = f"{app_domain}/?join-code={subject_code}"

    # Dialog heading
    st.header("Scan to join")

    # =====================================================
    # GENERATE QR CODE
    # =====================================================

    # Create QR object using join URL
    qr = segno.make(join_url)

    # Create in-memory binary stream
    # This stores QR image temporarily in RAM
    out = io.BytesIO()

    # -----------------------------------------------------
    # Save QR as PNG image
    #
    # kind='png'   -> output format
    # scale=10     -> image size
    # border=1     -> QR border thickness
    # -----------------------------------------------------
    qr.save(
        out,
        kind='png',
        scale=10,
        border=1
    )

    # =====================================================
    # CREATE 2 COLUMNS
    # =====================================================
    # Left column  -> text/link/code
    # Right column -> QR image
    # =====================================================
    col1, col2 = st.columns(2)

    # =====================================================
    # LEFT COLUMN
    # =====================================================
    with col1:

        # Section title
        st.markdown('### Copy Link')

        # Display join URL in copyable code box
        st.code(join_url, language="text")

        # Display subject code separately
        st.code(subject_code, language="text")

        # Information message
        st.info(
            'Copy this link to share on Whatsapp or Email'
        )

    # =====================================================
    # RIGHT COLUMN
    # =====================================================
    with col2:

        # Section title
        st.markdown('### Scan to join')

        # Display QR image
        st.image(

            # Convert BytesIO image data into displayable format
            out.getvalue(),

            # Width of image
            width=230,

            # Caption below image
            caption='QRCODE for class joining'
        )